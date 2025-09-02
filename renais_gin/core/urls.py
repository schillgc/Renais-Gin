from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register-bottle/', views.register_bottle, name='register_bottle'),
    path('submit-pledge/<str:bottle_id>/', views.submit_pledge, name='submit_pledge'),
    path('validate-pledge/<int:pledge_id>/', views.validate_pledge, name='validate_pledge'),
    path('api/metrics/', views.api_movement_metrics, name='api_metrics'),
    path('upload-pdf/', views.upload_pdf, name='upload_pdf'),
    path('download-pdf/<int:pdf_id>/', views.download_pdf, name='download_pdf'),
    path('pdf/<str:pdf_name>/', views.view_static_pdf, name='view_static_pdf'),
    path('generate-report/', views.generate_impact_report, name='generate_report'),
    path('generate-report/<int:pledge_id>/', views.generate_impact_report, name='generate_pledge_report'),
]
