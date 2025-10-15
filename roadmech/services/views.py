# services/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .forms import ServiceRequestForm, FeedbackForm
from .models import ServiceRequest, Feedback
from accounts.models import MechanicProfile
from geopy.distance import geodesic
import math

def home(request):
    return render(request, 'home.html')

@login_required
def choose_vehicle(request):
    return render(request, 'services/choose_vehicle.html')

def haversine_km(lat1, lon1, lat2, lon2):
    """Return distance in kilometers between two lat/lon points using Haversine."""
    if None in (lat1, lon1, lat2, lon2):
        return None
    R = 6371.0  # Earth's radius in kilometers
    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    a = math.sin(dlat/2)**2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@login_required
def request_service(request):
    """
    GET: show form
    POST: save ServiceRequest (including lat/lon) then redirect to nearby_mechanics view
    """
    vehicle_type = request.GET.get("vehicle")  # from choose_vehicle

    if request.method == "POST":
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            sr = form.save(commit=False)
            sr.user = request.user
            if vehicle_type:
                sr.vehicle_type = vehicle_type

            # Accept latitude/longitude from hidden inputs (strings)
            lat = request.POST.get("latitude") or request.POST.get("lat")
            lon = request.POST.get("longitude") or request.POST.get("lon")
            try:
                sr.latitude = float(lat) if lat not in (None, "") else None
                sr.longitude = float(lon) if lon not in (None, "") else None
            except (ValueError, TypeError):
                sr.latitude = None
                sr.longitude = None

            sr.save()
            # Redirect to nearby list (view will compute distances)
            return redirect('nearby_mechanics', request_id=sr.id)
        else:
            # Form invalid: fall through to re-render with errors
            messages.error(request, "Please fix the errors in the form.")
    else:
        initial = {}
        if vehicle_type:
            initial["vehicle_type"] = vehicle_type
        form = ServiceRequestForm(initial=initial)

    return render(request, "services/request_service.html", {"form": form, "vehicle_type": vehicle_type})

@login_required
def nearby_mechanics(request, request_id):
    """Show nearby mechanics for a saved ServiceRequest"""
    service_request = get_object_or_404(ServiceRequest, id=request_id, user=request.user)

    # Check if service request has valid coordinates
    if service_request.latitude is None or service_request.longitude is None:
        messages.error(request, "Location not set on your request. Please allow geolocation or enter a location.")
        return redirect('request_service')

    user_location = (service_request.latitude, service_request.longitude)
    radius_km = 50  # Configurable radius (you can change this as needed)

    # Get approved mechanics with valid coordinates
    mechanics = MechanicProfile.objects.filter(approved=True).exclude(
        latitude__isnull=True
    ).exclude(
        longitude__isnull=True
    )
    
    nearby_mechanics = []

    for mechanic in mechanics:
        mechanic_location = (mechanic.latitude, mechanic.longitude)
        distance = geodesic(user_location, mechanic_location).km

        if distance <= radius_km:
            # Calculate average rating
            avg_rating = mechanic.feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0
            nearby_mechanics.append({
                'mechanic': mechanic,
                'distance': round(distance, 2),
                'avg_rating': round(avg_rating, 1)
            })

    # Sort by distance (closest first)
    nearby_mechanics.sort(key=lambda x: x['distance'])

    context = {
        'service_request': service_request,
        'nearby_mechanics': nearby_mechanics,
        'radius_km': radius_km
    }
    return render(request, 'services/nearby_mechanics.html', context)


@login_required
def assign_mechanic(request, request_id, mechanic_id):
    sr = get_object_or_404(ServiceRequest, pk=request_id, user=request.user)
    mech = get_object_or_404(MechanicProfile, pk=mechanic_id, approved=True)
    sr.mechanic = mech
    sr.status = "Accepted"
    sr.save()
    messages.success(request, "Mechanic assigned to your request.")
    return redirect("user_dashboard")

@login_required
def user_dashboard(request):
    reqs = ServiceRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'services/user_dashboard.html', {'requests': reqs})

@login_required
def accept_request(request, pk):
    try:
        mp = request.user.mechanicprofile
    except Exception:
        messages.error(request, "Only registered mechanics can accept requests.")
        return redirect('home')

    sr = get_object_or_404(ServiceRequest, pk=pk)
    if sr.status != 'Pending':
        messages.warning(request, "This request is not available to accept.")
        return redirect('mechanic_dashboard')
    sr.mechanic = mp
    sr.status = 'Accepted'
    sr.save()
    messages.success(request, "You accepted the request.")
    return redirect('mechanic_dashboard')

def service_success(request):
    return render(request, "services/service_success.html")

@login_required
@login_required
def give_feedback(request, mechanic_id):
    mechanic = get_object_or_404(MechanicProfile, id=mechanic_id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback, created = Feedback.objects.update_or_create(
                user=request.user,
                mechanic=mechanic,
                defaults=form.cleaned_data
            )
            messages.success(request, "Thank you for your feedback!")
            return redirect('mechanic_detail', mechanic_id=mechanic.id)
    else:
        form = FeedbackForm()

    return render(request, 'services/give_feedback.html', {
        'form': form,
        'mechanic': mechanic
    })

def mechanic_detail(request, mechanic_id):
    mechanic = get_object_or_404(MechanicProfile, id=mechanic_id)
    feedbacks = mechanic.feedbacks.all()
    avg_rating = feedbacks.aggregate(Avg("rating"))["rating__avg"] or 0
    return render(request, 'services/mechanic_detail.html', {
        'mechanic': mechanic,
        'feedbacks': feedbacks,
        'avg_rating': round(avg_rating, 1)
    })

@login_required
def search_mechanics(request):
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")
    radius_km = float(request.GET.get("radius", 10))
    mechanics_list = []

    if lat and lon:
        try:
            lat_f = float(lat); lon_f = float(lon)
        except ValueError:
            lat_f = lon_f = None

        if lat_f is not None:
            qs = MechanicProfile.objects.filter(approved=True).exclude(latitude__isnull=True).exclude(longitude__isnull=True)
            for mech in qs:
                if mech.latitude is None or mech.longitude is None: continue
                distance = haversine_km(lat_f, lon_f, mech.latitude, mech.longitude)
                if distance <= radius_km:
                    mechanics_list.append((mech, distance))
            mechanics_list.sort(key=lambda x: x[1])

    return render(request, "services/search_mechanics.html", {
        "query": f"{lat},{lon}" if lat and lon else "",
        "radius": radius_km,
        "mechanics": mechanics_list,
    })

mechanics = MechanicProfile.objects.filter(approved=True).annotate(avg_rating=Avg('feedbacks__rating'))