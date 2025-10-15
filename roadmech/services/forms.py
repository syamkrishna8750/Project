# services/forms.py
from django import forms
from .models import ServiceRequest, Feedback
import datetime

class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = [
            'service_type',
            'vehicle_brand',
            'vehicle_model',
            'vehicle_year',
            'vehicle_number',
            'owner_name',
            'phone_number',
            'location',
            'latitude',
            'longitude',
        ]
        widgets = {
            'location': forms.TextInput(attrs={'placeholder': 'Address or description'}),
            'vehicle_year': forms.Select(choices=[('', 'Year')] + [(y, y) for y in range(1980, datetime.date.today().year + 1)]),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }



class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
