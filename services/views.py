# services/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .forms import ServiceRequestForm, FeedbackForm
from .models import ServiceRequest, Feedback
from accounts.models import MechanicProfile
from geopy.distance import geodesic
from django.http import JsonResponse
import json
import math


def home(request):
    # If user is logged in and is a mechanic, redirect to mechanic dashboard
    if request.user.is_authenticated and hasattr(request.user, 'mechanicprofile'):
        return redirect('mechanic_dashboard')
    
    # Everyone else (regular users and guests) sees the home page
    return render(request, 'home.html')

@login_required
def choose_vehicle(request):
    return render(request, 'services/choose_vehicle.html')


# ---------------- Helper Function ----------------
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


# ---------------- Service Request ----------------
@login_required
def request_service(request):
    """
    GET: Show service request form.
    POST: Save request (status stays pending).
    """
    vehicle_type = request.GET.get("vehicle")

    if request.method == "POST":
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            sr = form.save(commit=False)
            sr.user = request.user
            
            if vehicle_type:
                sr.vehicle_type = vehicle_type

            # Accept latitude/longitude from hidden inputs
            lat = request.POST.get("latitude") or request.POST.get("lat")
            lon = request.POST.get("longitude") or request.POST.get("lon")

            try:
                sr.latitude = float(lat) if lat not in (None, "") else None
                sr.longitude = float(lon) if lon not in (None, "") else None
            except (ValueError, TypeError):
                sr.latitude = sr.longitude = None

            sr.status = "Pending"  # ✅ Always pending initially
            sr.save()
            
            # redirect to nearby mechanics for selection
            return redirect('nearby_mechanics', request_id=sr.id)
        else:
            messages.error(request, "Please fix the errors in the form.")
    else:
        initial = {}
        if vehicle_type:
            initial["vehicle_type"] = vehicle_type
        form = ServiceRequestForm(initial=initial)

    return render(request, "services/request_service.html", {
        "form": form,
        "vehicle_type": vehicle_type
    })


# ---------------- Nearby Mechanics ----------------

@login_required
def nearby_mechanics(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id, user=request.user)
    radius_km = 50
    
    # USE THE SAME LOCATION AS YOUR MECHANICS
    # Since your mechanics are in Kerala, use those coordinates
    user_lat = 10.884653  # Valanchery coordinates
    user_lng = 76.038162
    
    # Optional: Update the service request with correct coordinates
    if service_request.latitude != user_lat or service_request.longitude != user_lng:
        service_request.latitude = user_lat
        service_request.longitude = user_lng
        service_request.save()

    # Rest of your code...
    all_mechanics = MechanicProfile.objects.filter(
        is_available=True, 
        approved=True
    ).exclude(latitude=None).exclude(longitude=None)
    
    nearby_mechanics = []
    user_location = (user_lat, user_lng)

    for mechanic in all_mechanics:
        try:
            mechanic_location = (float(mechanic.latitude), float(mechanic.longitude))
            distance_km = geodesic(user_location, mechanic_location).km

            if distance_km <= radius_km:
                nearby_mechanics.append({
                    'mechanic': mechanic,
                    'distance': round(distance_km, 2)
                })
        except (TypeError, ValueError):
            continue

    nearby_mechanics.sort(key=lambda x: x['distance'])
    
    context = {
        'service_request': service_request,
        'nearby_mechanics': nearby_mechanics,
        'radius_km': radius_km,
        'user_location': f"{user_lat}, {user_lng}",
    }
    return render(request, 'services/nearby_mechanics.html', context)

# ---------------- Mechanic Assignment ----------------
@login_required
def assign_mechanic(request, request_id, mechanic_id):
    sr = get_object_or_404(ServiceRequest, id=request_id, user=request.user)
    mech = get_object_or_404(MechanicProfile, id=mechanic_id)

    sr.mechanic = mech
    sr.status = 'Pending'   
    sr.save()
    return redirect('service_success', request_id=sr.id)




# ---------------- User Dashboard ----------------
@login_required
def user_dashboard(request):
    reqs = ServiceRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'services/user_dashboard.html', {'requests': reqs})


@login_required
def mechanic_dashboard(request):
    mechanic = MechanicProfile.objects.get(user=request.user)
    requests = ServiceRequest.objects.filter(mechanic=mechanic)
    return render(request, 'services/mechanic_dashboard.html', {'requests': requests})



# ---------------- Mechanic Accept Request ----------------
@login_required
def accept_request(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)

    # ensure only the assigned mechanic can accept
    if service_request.mechanic and request.user == service_request.mechanic.user:
        service_request.status = 'Accepted'
        service_request.save()
        messages.success(request, "Service request accepted successfully!")
    else:
        messages.error(request, "You are not authorized to accept this request.")

    return redirect('mechanic_dashboard')



# ---------------- Feedback ----------------
@login_required
def give_feedback(request, request_id=None, mechanic_id=None):
    """Allow user to give feedback for a service request or mechanic."""
    service_request = None
    mechanic = None
    
    try:
        if request_id:
            service_request = get_object_or_404(ServiceRequest, id=request_id, user=request.user)
            mechanic = service_request.mechanic
        elif mechanic_id:
            # Use try-except to handle non-existent mechanics gracefully
            try:
                mechanic = MechanicProfile.objects.get(id=mechanic_id)
            except MechanicProfile.DoesNotExist:
                messages.error(request, "The mechanic you're trying to review no longer exists.")
                return redirect('user_dashboard')
    
        if not mechanic:
            messages.error(request, "No mechanic found to give feedback for.")
            return redirect('user_dashboard')

        # Check if feedback already exists
        if service_request:
            existing_feedback = Feedback.objects.filter(
                service_request=service_request, 
                user=request.user
            ).exists()
            if existing_feedback:
                messages.error(request, "You have already submitted feedback for this service request.")
                return redirect('my_requests')

        if request.method == 'POST':
            rating = request.POST.get('rating')
            comment = request.POST.get('comment', '')

            # Validate rating
            if not rating or not rating.isdigit() or int(rating) not in range(1, 6):
                messages.error(request, "Please provide a valid rating (1-5 stars).")
            else:
                # Create feedback
                Feedback.objects.create(
                    user=request.user,
                    mechanic=mechanic,
                    service_request=service_request,
                    rating=int(rating),
                    comment=comment
                )

                messages.success(request, "Thank you for your feedback!")
                if service_request:
                    return redirect('my_requests')
                else:
                    return redirect('search_mechanics')  # or wherever makes sense

        return render(request, 'services/give_feedback.html', {
            'mechanic': mechanic,
            'service_request': service_request
        })
        
    except Exception as e:
        messages.error(request, "An error occurred while processing your feedback.")
        return redirect('user_dashboard')


# ---------------- Mechanic Detail ----------------
def mechanic_detail(request, mechanic_id):
    mechanic = get_object_or_404(MechanicProfile, id=mechanic_id)
    feedbacks = mechanic.feedbacks.all()
    avg_rating = feedbacks.aggregate(Avg("rating"))["rating__avg"] or 0

    return render(request, 'services/mechanic_detail.html', {
        'mechanic': mechanic,
        'feedbacks': feedbacks,
        'avg_rating': round(avg_rating, 1)
    })


# ---------------- My Requests ----------------
@login_required
def my_requests(request):
    requests = ServiceRequest.objects.filter(user=request.user).select_related('mechanic')
    return render(request, 'services/my_requests.html', {'requests': requests})


# ---------------- Search Mechanics ----------------
@login_required
def search_mechanics(request):
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")
    radius_km = float(request.GET.get("radius", 50))
    mechanics_list = []

    if lat and lon:
        try:
            lat_f, lon_f = float(lat), float(lon)
        except ValueError:
            lat_f = lon_f = None

        if lat_f is not None:
            qs = MechanicProfile.objects.filter(approved=True).exclude(
                latitude__isnull=True, longitude__isnull=True
            )

            for mech in qs:
                if mech.latitude is None or mech.longitude is None:
                    continue
                distance = haversine_km(lat_f, lon_f, mech.latitude, mech.longitude)
                if distance <= radius_km:
                    avg_rating = mech.feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0
                    mechanics_list.append({
                        'mechanic': mech,
                        'distance': round(distance, 2),
                        'avg_rating': round(avg_rating, 1)
                    })

            mechanics_list.sort(key=lambda x: x['distance'])

    return render(request, "services/search_mechanics.html", {
        "query": f"{lat},{lon}" if lat and lon else "",
        "radius": radius_km,
        "mechanics": mechanics_list,
    })

# services/views.py - Add this function
@login_required
def service_history(request):
    # Get user's service requests ordered by creation date
    service_requests = ServiceRequest.objects.filter(user=request.user).order_by('-created_at')
    
    # Add feedback information for each request
    for req in service_requests:
        req.feedback_exists = Feedback.objects.filter(service_request=req, user=request.user).exists()
        req.can_give_feedback = (
            req.status == 'Completed' and 
            req.mechanic and 
            not req.feedback_exists
        )
    
    context = {
        'service_requests': service_requests,
    }
    return render(request, 'services/service_history.html', context)


@login_required
def service_success(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id, user=request.user)
    return render(request, 'services/service_success.html', {'service_request': service_request})

@login_required
def update_request_status(request, request_id):
    if request.method == 'POST':
        import json
        service_request = get_object_or_404(ServiceRequest, id=request_id)
        
        # Check if the current user is the assigned mechanic
        if service_request.mechanic.user != request.user:
            return JsonResponse({'success': False, 'error': 'Not authorized'})
        
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status in ['Accepted', 'Completed']:
            service_request.status = new_status
            service_request.save()
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@login_required
def complete_request(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    
    if service_request.mechanic.user != request.user:
        messages.error(request, 'You are not authorized to complete this request.')
        return redirect('mechanic_dashboard')
    
    if service_request.status == 'Accepted':
        service_request.status = 'Completed'
        service_request.save()
        messages.success(request, 'Service marked as completed!')
    else:
        messages.warning(request, 'This request cannot be marked as completed.')
    
    return redirect('mechanic_dashboard')


@login_required
def mechanic_dashboard(request):
    try:
        mechanic = MechanicProfile.objects.get(user=request.user)
        requests = ServiceRequest.objects.filter(mechanic=mechanic)
        
        # Separate requests by status
        pending_requests = requests.filter(status='Pending')
        accepted_requests = requests.filter(status='Accepted')
        completed_requests = requests.filter(status='Completed')
        
        # Calculate average rating
        from django.db.models import Avg
        average_rating = Feedback.objects.filter(
            mechanic=mechanic
        ).aggregate(Avg('rating'))['rating__avg'] or 0.0
        
        context = {
            'mechanic': mechanic,
            'pending_requests': pending_requests,
            'my_accepted': accepted_requests,
            'completed_requests': completed_requests,
            'average_rating': round(average_rating, 1),
        }
        return render(request, 'services/mechanic_dashboard.html', context)
        
    except MechanicProfile.DoesNotExist:
        messages.error(request, 'You are not registered as a mechanic.')
        return redirect('home')

@login_required
def create_service_request(request):
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.user = request.user
            service_request.save()
            messages.success(request, 'Service request submitted successfully!')
            return redirect('service_requests')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ServiceRequestForm()
    
    return render(request, 'services/create_request.html', {'form': form})    