from django import forms
from .models import ServiceRequest, Feedback
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
import re
import datetime

class ServiceRequestForm(forms.ModelForm):
    # Custom field with validation
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your 10-digit phone number',
            'pattern': '[6-9][0-9]{9}',
            'title': 'Please enter a valid 10-digit Indian phone number'
        }),
        validators=[
            RegexValidator(
                regex=r'^[6-9]\d{9}$',
                message="Please enter a valid 10-digit Indian phone number starting with 6-9."
            )
        ],
        error_messages={
            'required': 'Phone number is required for service requests.'
        }
    )
    
    owner_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter owner name'}),
        validators=[
            MinLengthValidator(
                2,
                message="Owner name must be at least 2 characters long."
            )
        ],
        error_messages={
            'required': 'Owner name is required.'
        }
    )
    
    vehicle_brand = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter vehicle brand'}),
        validators=[
            MinLengthValidator(
                2,
                message="Vehicle brand must be at least 2 characters long."
            )
        ],
        error_messages={
            'required': 'Vehicle brand is required.'
        }
    )
    
    vehicle_model = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter vehicle model'}),
        validators=[
            MinLengthValidator(
                1,
                message="Vehicle model is required."
            )
        ],
        error_messages={
            'required': 'Vehicle model is required.'
        }
    )
    
    vehicle_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter vehicle number'}),
        validators=[
            MinLengthValidator(
                3,
                message="Vehicle number must be at least 3 characters long."
            )
        ],
        error_messages={
            'required': 'Vehicle number is required.'
        }
    )
    
    location = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your current location'}),
        validators=[
            MinLengthValidator(
                10,
                message="Location must be at least 10 characters long for accurate service."
            )
        ],
        error_messages={
            'required': 'Location is required to dispatch assistance.'
        }
    )

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
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'placeholder': 'Enter your current location with landmarks'}),
            'vehicle_year': forms.Select(choices=[('', 'Select Year')] + [(y, y) for y in range(1980, datetime.date.today().year + 1)]),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make service_type required
        self.fields['service_type'].required = True
        self.fields['vehicle_year'].required = True

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Remove any spaces, dashes, or other characters
            phone_number = re.sub(r'[^\d]', '', phone_number)
            
            # Check if it's exactly 10 digits and starts with 6-9
            if len(phone_number) != 10:
                raise ValidationError("Phone number must be exactly 10 digits.")
            
            if not phone_number[0] in '6789':
                raise ValidationError("Phone number must start with 6, 7, 8, or 9.")
                
        return phone_number

    def clean_vehicle_year(self):
        vehicle_year = self.cleaned_data.get('vehicle_year')
        if vehicle_year:
            current_year = datetime.date.today().year
            if vehicle_year < 1980 or vehicle_year > current_year + 1:
                raise ValidationError(f"Vehicle year must be between 1980 and {current_year + 1}.")
        return vehicle_year

    def clean_vehicle_number(self):
        vehicle_number = self.cleaned_data.get('vehicle_number')
        if vehicle_number:
            # Basic vehicle number validation
            vehicle_number = vehicle_number.strip().upper()
            
            # Check for minimum length
            if len(vehicle_number) < 3:
                raise ValidationError("Vehicle number seems too short. Please enter a valid vehicle number.")
            
            # Optional: Add more specific validation for Indian vehicle numbers
            # Example: Check if it matches common Indian vehicle number patterns
            if re.search(r'[^A-Z0-9\s]', vehicle_number):
                raise ValidationError("Vehicle number contains invalid characters. Use only letters, numbers, and spaces.")
                
        return vehicle_number

    def clean_owner_name(self):
        owner_name = self.cleaned_data.get('owner_name')
        if owner_name:
            # Remove extra spaces
            owner_name = ' '.join(owner_name.strip().split())
            
            # Check if name contains only letters and spaces
            if not re.match(r'^[A-Za-z\s\.]+$', owner_name):
                raise ValidationError("Owner name can only contain letters, spaces, and dots.")
            
            # Check if name has at least 2 characters (after cleaning)
            if len(owner_name) < 2:
                raise ValidationError("Owner name must be at least 2 characters long.")
                
        return owner_name

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location:
            # Remove extra spaces
            location = ' '.join(location.strip().split())
            
            # Check minimum length
            if len(location) < 10:
                raise ValidationError("Please provide a more detailed location (at least 10 characters) for accurate service.")
                
        return location

    def clean(self):
        cleaned_data = super().clean()
        
        # Validate coordinates if provided
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        
        if latitude and longitude:
            if not (-90 <= float(latitude) <= 90):
                self.add_error('latitude', "Invalid latitude value. Must be between -90 and 90.")
            if not (-180 <= float(longitude) <= 180):
                self.add_error('longitude', "Invalid longitude value. Must be between -180 and 180.")
        
        return cleaned_data

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }