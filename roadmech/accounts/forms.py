from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="We'll use this to contact you if needed.")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class MechanicRegistrationForm(UserRegistrationForm):
    service_center_name = forms.CharField(max_length=255, required=True)
    phone = forms.CharField(max_length=20, required=True)
    location = forms.CharField(widget=forms.Textarea, required=True)  # ✅ changed
