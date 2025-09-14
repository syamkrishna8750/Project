from django.contrib.auth.models import User
from django.db import models

class MechanicProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    service_center_name = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)  # ✅ add this

    def __str__(self):
        return self.user.username