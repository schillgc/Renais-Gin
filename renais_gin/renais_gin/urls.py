# renais_gin/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Renais Gin API",
        default_version='v1',
        description="API for Renais Gin sustainability platform",
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('bottles/', TemplateView.as_view(template_name='bottles.html'), name='bottles'),
    path('karma/', TemplateView.as_view(template_name='karma.html'), name='karma'),

    # API endpoints
    path('api/auth/', include('core.urls')),
    path('api/karma/', include('karma.urls')),
    path('api/bottles/', include('bottles.urls')),
    path('api/ai/', include('ai_agents.urls')),

    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
