# core/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Template views
    path('register/', views.register_user, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # API endpoints
    path('api/register/', views.register_user, name='api-register'),
    path('api/login/', views.login_user, name='api-login'),
    path('api/logout/', views.logout_user, name='api-logout'),
    path('api/profile/', views.UserProfileView.as_view(), name='api-profile'),
    path('api/stats/', views.UserStatsView.as_view(), name='api-stats'),
]
