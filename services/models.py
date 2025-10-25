from django.db import models
from django.contrib.auth.models import User
import datetime
# Remove this import to avoid circular imports
# from accounts.models import MechanicProfile


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
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Use string reference to avoid circular imports
    mechanic = models.ForeignKey('accounts.MechanicProfile', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

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

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.service_type} ({self.vehicle_type})"
    
    # FIXED INDENTATION - these should be at the same level as other methods
    @property
    def can_give_feedback(self):
        """User can give feedback if there's a mechanic and no feedback exists"""
        return (self.mechanic is not None and 
                not self.feedback_exists and
                self.status != 'Cancelled')
    
    @property
    def feedback_exists(self):
        """Check if feedback already exists for this request"""
        # Use the correct approach - query the Feedback model
        from .models import Feedback  # Import here to avoid circular imports
        return Feedback.objects.filter(service_request=self).exists()


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_request = models.ForeignKey('ServiceRequest', on_delete=models.CASCADE, null=True, blank=True)
    # Use string reference to avoid circular imports
    mechanic = models.ForeignKey('accounts.MechanicProfile', on_delete=models.CASCADE, null=True, blank=True)

    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.mechanic:
            return f"{self.user.username} rated {self.mechanic.service_center_name} ({self.rating}/5)"
        return f"{self.user.username} rating ({self.rating}/5)"

    class Meta:
        unique_together = ('user', 'service_request')