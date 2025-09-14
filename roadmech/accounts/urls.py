from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from accounts import views as account_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('mechanic/register/', views.mechanic_register, name='mechanic_register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('mechanic/dashboard/', views.mechanic_dashboard, name='mechanic_dashboard'),
    path('redirect/', account_views.redirect_after_login, name='redirect_after_login'),
]
