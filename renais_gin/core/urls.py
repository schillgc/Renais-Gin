# core/urls.py
"""
Core app URL configuration for Renais Gin.
"""

from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'core'

urlpatterns = [
    # Public pages
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', TemplateView.as_view(template_name='core/contact.html'), name='contact'),

    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard and main app
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),

    # Bottle management
    path('bottles/', views.bottles_view, name='bottles'),
    path('bottles/register/', views.register_bottle_view, name='register_bottle'),
    path('bottles/<str:bottle_id>/', views.bottle_detail_view, name='bottle_detail'),

    # Karma pledges
    path('karma/', views.karma_view, name='karma'),
    path('karma/submit/<str:bottle_id>/', views.submit_pledge_view, name='submit_pledge'),
    path('karma/pledge/<int:pledge_id>/', views.pledge_detail_view, name='pledge_detail'),

    # Community validation
    path('community/pledges/', views.community_pledges_view, name='community_pledges'),
    path('community/validate/<int:pledge_id>/', views.validate_pledge_view, name='validate_pledge'),

    # Community circles
    path('community/circles/', views.community_circles_view, name='community_circles'),
    path('community/circles/create/', views.create_circle_view, name='create_circle'),
    path('community/circles/<int:circle_id>/', views.circle_detail_view, name='circle_detail'),
    path('community/circles/<int:circle_id>/join/', views.join_circle_view, name='join_circle'),
    path('community/circles/<int:circle_id>/leave/', views.leave_circle_view, name='leave_circle'),

    # Impact and stories
    path('impact/stories/', views.impact_stories_view, name='impact_stories'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),

    # Document management
    path('documents/upload/', views.upload_pdf_view, name='upload_pdf'),
    path('documents/', views.my_documents_view, name='my_documents'),

    # Reports
    path('reports/generate/', TemplateView.as_view(template_name='core/generate_report.html'), name='generate_report'),

    # API endpoints (HTML views)
    path('api/metrics/', views.movement_metrics_api, name='api_metrics'),  # FIXED: Changed name to 'api_metrics'
]
