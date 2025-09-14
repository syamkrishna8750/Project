from django.contrib import admin
from .models import ServiceRequest

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('id','user','service_type','vehicle_type','status','mechanic','created_at')
    list_filter = ('service_type','vehicle_type','status')
    search_fields = ('user__username','location','vehicle_details')
