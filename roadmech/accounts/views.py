from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm, MechanicRegistrationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from services.models import ServiceRequest

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

def mechanic_register(request):
    if request.method == 'POST':
        form = MechanicRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            service_center_name = form.cleaned_data.get('service_center_name')
            phone = form.cleaned_data.get('phone')
            location = form.cleaned_data.get('location')  # ✅ use location instead of address

            from .models import MechanicProfile
            MechanicProfile.objects.create(
                user=user,
                service_center_name=service_center_name,
                phone=phone,
                location=location  # ✅ updated
            )
            messages.success(request, "Mechanic account created. You can log in now.")
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