
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class MechanicProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    service_center_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)  # Add unique=True
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    specialization = models.CharField(max_length=255, blank=True, null=True)
    approved = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def average_rating(self):
        avg = self.feedback_set.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0.0
    
    @property
    def rating(self):
        """Property alias for templates"""
        return self.average_rating()

    def __str__(self):
        return self.service_center_name