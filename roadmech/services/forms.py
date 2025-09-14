from django import forms
from .models import ServiceRequest
import datetime

# Generate year choices dynamically
current_year = datetime.date.today().year
YEAR_CHOICES = [(year, year) for year in range(1990, current_year + 1)]

class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = [
            'vehicle_brand',
            'vehicle_model',
            'vehicle_year',
            'vehicle_number',
            'owner_name',
            'phone_number',
            'service_type',
            'location',
        ]
        widgets = {
            'vehicle_brand': forms.TextInput(attrs={'placeholder': 'e.g. Toyota'}),
            'vehicle_model': forms.TextInput(attrs={'placeholder': 'e.g. Corolla'}),
            'vehicle_year': forms.Select(choices=YEAR_CHOICES),
            'vehicle_number': forms.TextInput(attrs={'placeholder': 'e.g. KA-05-1234'}),
            'owner_name': forms.TextInput(attrs={'placeholder': 'Your Full Name'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'e.g. +91 9876543210'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g. Highway 85 near Exit 12'}),
        }
