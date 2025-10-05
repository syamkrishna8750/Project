from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('choose/', views.choose_vehicle, name='choose_vehicle'),
    path('request/', views.request_service, name='request_service'),
    path('nearby/<int:request_id>/', views.nearby_mechanics, name='nearby_mechanics'),
    path('assign/<int:request_id>/<int:mechanic_id>/', views.assign_mechanic, name='assign_mechanic'),
    path('accept/<int:pk>/', views.accept_request, name='accept_request'),
    path('success/', views.service_success, name='service_success'),
    path('mechanic/<int:mechanic_id>/', views.mechanic_detail, name='mechanic_detail'),
    path('search/', views.search_mechanics, name='search_mechanics'),
    path('feedback/<int:mechanic_id>/', views.give_feedback, name='give_feedback'),
]

