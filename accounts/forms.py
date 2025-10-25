from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import MechanicProfile
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
import re



class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="We'll use this to contact you if needed.",
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter a username'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add HTML5 validation attributes for password fields
        self.fields['password1'].widget.attrs.update({
            'minlength': '8',
            'pattern': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
            'title': 'Password must have: 8+ characters, 1 uppercase, 1 lowercase, 1 number, 1 special character (@$!%*#?&)'
        })
        self.fields['password2'].widget.attrs.update({
            'minlength': '8'
        })

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            # Check minimum length
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long.")
            
            # Check for at least one digit
            if not re.search(r'\d', password):
                raise ValidationError("Password must contain at least one digit (0-9).")
            
            # Check for at least one uppercase letter
            if not re.search(r'[A-Z]', password):
                raise ValidationError("Password must contain at least one uppercase letter (A-Z).")
            
            # Check for at least one lowercase letter
            if not re.search(r'[a-z]', password):
                raise ValidationError("Password must contain at least one lowercase letter (a-z).")
            
            # Check for at least one special character
            if not re.search(r'[@$!%*#?&]', password):
                raise ValidationError("Password must contain at least one special character (@, $, !, %, *, #, ?, &).")
            
            # Optional: Check for common weak passwords
            weak_passwords = [
                'password', '12345678', 'qwertyui', 'admin123', 
                'welcome1', 'password1', 'abc12345'
            ]
            if password.lower() in weak_passwords:
                raise ValidationError("This password is too common. Please choose a stronger one.")
            
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match.")
        
        return cleaned_data



from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
import re

class MechanicRegistrationForm(UserRegistrationForm):
    service_center_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your service center name'}),
        error_messages={
            'required': 'Service center name is required.',
            'max_length': 'Service center name cannot exceed 255 characters.'
        }
    )
    
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your 10-digit phone number',
            'pattern': '[0-9]{10}',
            'title': 'Please enter a 10-digit phone number'
        }),
        validators=[
            RegexValidator(
                regex=r'^[6-9]\d{9}$',
                message="Please enter a valid 10-digit Indian phone number starting with 6-9."
            )
        ],
        error_messages={
            'required': 'Phone number is required.'
        }
    )
    
    location = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter your service center full address',
            'rows': 3
        }),
        required=True,
        validators=[
            MinLengthValidator(
                10,
                message="Location address must be at least 10 characters long."
            )
        ],
        error_messages={
            'required': 'Location address is required.'
        }
    )
    
    latitude = forms.FloatField(
        widget=forms.HiddenInput(),
        required=False
    )
    
    longitude = forms.FloatField(
        widget=forms.HiddenInput(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add HTML5 validation attributes for password fields
        self.fields['password1'].widget.attrs.update({
            'minlength': '8',
            'pattern': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
            'title': 'Password must have: 8+ chars, 1 uppercase, 1 lowercase, 1 number, 1 special character'
        })
        self.fields['password2'].widget.attrs.update({
            'minlength': '8'
        })

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove any spaces, dashes, or other characters
            phone = re.sub(r'[^\d]', '', phone)
            
            # Check if it's exactly 10 digits and starts with 6-9
            if len(phone) != 10:
                raise ValidationError("Phone number must be exactly 10 digits.")
            
            if not phone[0] in '6789':
                raise ValidationError("Phone number must start with 6, 7, 8, or 9.")
            
            # Check if phone number already exists in MechanicProfile
            from .models import MechanicProfile
            if MechanicProfile.objects.filter(phone=phone).exists():
                raise ValidationError("This phone number is already registered.")
                
        return phone

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long.")
            if not re.search(r'\d', password):
                raise ValidationError("Password must contain at least one digit.")
            if not re.search(r'[A-Z]', password):
                raise ValidationError("Password must contain at least one uppercase letter.")
            if not re.search(r'[a-z]', password):
                raise ValidationError("Password must contain at least one lowercase letter.")
            if not re.search(r'[@$!%*#?&]', password):
                raise ValidationError("Password must contain at least one special character (@, $, !, etc).")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match.")
        
        return cleaned_data

    class Meta(UserRegistrationForm.Meta):
        fields = UserRegistrationForm.Meta.fields + [
            'service_center_name',
            'phone',
            'location',
            'latitude',
            'longitude'
        ]

class MechanicProfileForm(forms.ModelForm):
    class Meta:
        model = MechanicProfile
        fields = ['service_center_name', 'phone', 'location', 'latitude', 'longitude']



