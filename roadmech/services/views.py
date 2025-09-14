from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ServiceRequestForm
from .models import ServiceRequest
from django.contrib import messages

def home(request):
    return render(request, 'home.html')

@login_required
def choose_vehicle(request):
    return render(request, 'services/choose_vehicle.html')

@login_required
def request_service(request):
    vehicle_type = request.GET.get("vehicle")  # 👈 match the template
    if request.method == "POST":
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.user = request.user
            service_request.vehicle_type = vehicle_type
            service_request.save()
            return redirect("service_success")
    else:
        form = ServiceRequestForm()
    return render(request, "services/request_services.html", {"form": form, "vehicle_type": vehicle_type})

@login_required
def user_dashboard(request):
    requests = ServiceRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'services/user_dashboard.html', {'requests': requests})

@login_required
def accept_request(request, pk):
    # Only mechanics should accept; check MechanicProfile
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
