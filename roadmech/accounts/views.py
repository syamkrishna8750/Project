from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm, MechanicRegistrationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from services.models import ServiceRequest
from .models import MechanicProfile
from utils.geocode import geocode_address


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

# In your views.py
def mechanic_register(request):
    if request.method == 'POST':
        form = MechanicRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create MechanicProfile with all required fields
            mp = MechanicProfile.objects.create(
                user=user,
                service_center_name=form.cleaned_data['service_center_name'],
                phone=form.cleaned_data['phone'],
                location=form.cleaned_data['location'],
                latitude=form.cleaned_data.get('latitude'),
                longitude=form.cleaned_data.get('longitude'),
                approved=False  # Mechanic needs to be approved by admin
            )
            
            # Login the user or redirect to login page
            # login(request, user)
            messages.success(request, 'Mechanic registration successful! Waiting for approval.')
            return redirect('login')
    else:
        form = MechanicRegistrationForm()
    
    return render(request, 'accounts/mechanic_register.html', {'form': form})

@login_required
def mechanic_dashboard(request):
    # only mechanics should access: ensure they have a MechanicProfile
    try:
        mp = request.user.mechanicprofile
    except Exception:
        messages.error(request, "You must register as a mechanic to view this page.")
        return redirect('home')

    pending_requests = ServiceRequest.objects.filter(status='Pending')
    my_accepted = ServiceRequest.objects.filter(mechanic=mp)
    context = {'pending_requests': pending_requests, 'my_accepted': my_accepted}
    return render(request, 'services/mechanic_dashboard.html', context)


@login_required
def redirect_after_login(request):
    # send mechanic to mechanic dashboard
    if hasattr(request.user, "mechanicprofile"):
        return redirect("mechanic_dashboard")
    # normal users go to home
    return redirect("home")