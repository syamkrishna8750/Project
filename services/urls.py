from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('choose/', views.choose_vehicle, name='choose_vehicle'),
    path('request/', views.request_service, name='request_service'),
    path('nearby/<int:request_id>/', views.nearby_mechanics, name='nearby_mechanics'),
    path('assign/<int:request_id>/<int:mechanic_id>/', views.assign_mechanic, name='assign_mechanic'),
    path('mechanic/<int:mechanic_id>/', views.mechanic_detail, name='mechanic_detail'),
    path('search/', views.search_mechanics, name='search_mechanics'),
    path('mechanic/<int:mechanic_id>/feedback/', views.give_feedback, name='give_feedback'),
    path('service/success/<int:request_id>/', views.service_success, name='service_success'),
    path('accept/<int:request_id>/', views.accept_request, name='accept_request'),
    path('feedback/<int:request_id>/', views.give_feedback, name='give_feedback'),
    path('service-history/', views.service_history, name='service_history'),
    path('mechanic/dashboard/', views.mechanic_dashboard, name='mechanic_dashboard'),
    path('update-status/<int:request_id>/', views.update_request_status, name='update_request_status'),
    path('complete/<int:request_id>/', views.complete_request, name='complete_request'), 
    path('cancel-request/<int:request_id>/', views.cancel_request, name='cancel_request'),

    
]



