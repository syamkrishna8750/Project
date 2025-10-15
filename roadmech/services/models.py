from django.db import models
from django.contrib.auth.models import User
import datetime
from accounts.models import MechanicProfile


class ServiceRequest(models.Model):
    VEHICLE_CHOICES = [
        ('car', 'Car'),
        ('bike', 'Bike'),
    ]
    SERVICE_CHOICES = [
        ('towing', 'Towing'),
        ('fuel', 'Fuel Delivery'),
        ('battery', 'Battery Jumpstart'),
        ('tire', 'Tire Replacement'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mechanic = models.ForeignKey(
       'accounts.MechanicProfile',
        null=True,
        blank=True,
       on_delete=models.SET_NULL
    )

    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_CHOICES)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)

    # Vehicle details
    vehicle_brand = models.CharField(max_length=100, blank=True, null=True)
    vehicle_model = models.CharField(max_length=50, blank=True, null=True)
    vehicle_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        choices=[(y, y) for y in range(1980, datetime.date.today().year + 1)]
    )
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)

    # Owner details
    owner_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # Location fields
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.service_type} ({self.vehicle_type})"

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mechanic = models.ForeignKey(
        'accounts.MechanicProfile',
        on_delete=models.CASCADE,
        related_name="feedbacks"
    )
    rating = models.PositiveIntegerField(default=1)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'mechanic')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.mechanic.service_center_name} ({self.rating}⭐)"
