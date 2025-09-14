from django.db import models
from django.contrib.auth.models import User
import datetime

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
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_CHOICES)

    # 🔹 Structured vehicle fields
    vehicle_brand = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=50)
    vehicle_year = models.PositiveIntegerField(
        choices=[(y, y) for y in range(1980, datetime.date.today().year + 1)]
    )
    vehicle_number = models.CharField(max_length=20)

    owner_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)

    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    location = models.CharField(max_length=255)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    mechanic = models.ForeignKey(
        'accounts.MechanicProfile', null=True, blank=True, on_delete=models.SET_NULL
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehicle_brand} {self.vehicle_model} ({self.vehicle_number}) - {self.service_type}"
