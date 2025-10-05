from django.contrib.auth.models import User
from django.db import models

class MechanicProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    service_center_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=255, blank=True, null=True)  # human address
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.service_center_name or self.user.username
