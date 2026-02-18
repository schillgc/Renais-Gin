# renais_gin/urls.py

"""
Project URL configuration for renais_gin.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Schema configuration for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Renais Gin API",
        default_version='v1',
        description="API for Renais Gin community platform - Craft Your Perfect World",
        contact=openapi.Contact(email="support@renaisgin.com"),
        license=openapi.License(name="Renais Gin License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Core app URLs - FIXED: Include with namespace
    path('', include('core.urls', namespace='core')),

    # API URLs
    path('api/v1/', include('core.api_urls')),

    # Authentication URLs
    path('accounts/', include('django.contrib.auth.urls')),

    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='api-redoc'),

    # Favicon redirect
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
]

# Add debug toolbar URLs in development
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Add media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'core.views.custom_404_view'
handler500 = 'core.views.custom_500_view'

# Admin site customization
admin.site.site_header = 'Renais Gin Administration'
admin.site.site_title = 'Renais Gin Admin'
admin.site.index_title = 'Welcome to Renais Gin Administration'
