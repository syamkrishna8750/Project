from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import MechanicProfile

class MechanicProfileForm(forms.ModelForm):
    class Meta:
        model = MechanicProfile
        fields = ['service_center_name', 'phone', 'location', 'latitude', 'longitude']

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="We'll use this to contact you if needed.")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class MechanicRegistrationForm(UserRegistrationForm):
    service_center_name = forms.CharField(max_length=255, required=True)
    phone = forms.CharField(max_length=20, required=True)
    location = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter your service center full address',
            'rows': 3
        }), 
        required=True
    )
    latitude = forms.FloatField(
        widget=forms.HiddenInput(),
        required=False
    )
    longitude = forms.FloatField(
        widget=forms.HiddenInput(),
        required=False
    )