from django.contrib import admin
from .models import MechanicProfile

@admin.register(MechanicProfile)
class MechanicProfileAdmin(admin.ModelAdmin):
    list_display = ('service_center_name', 'user', 'phone', 'created_at')
    search_fields = ('service_center_name', 'user__username', 'phone')
