from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('choose/', views.choose_vehicle, name='choose_vehicle'),
     path('request/', views.request_service, name='request_service'),
    path('success/', views.service_success, name='service_success'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('mechanic/accept/<int:pk>/', views.accept_request, name='accept_request'),
]
