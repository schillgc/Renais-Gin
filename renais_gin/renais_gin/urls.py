from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # Core app URLs - this includes all the Renais Gin functionality
    path('', include('core.urls', namespace='core')),

    # Redirect root to dashboard
    path('', RedirectView.as_view(pattern_name='core:dashboard', permanent=False)),

    # Authentication URLs (using Django's built-in auth)
    path('accounts/', include('django.contrib.auth.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers (optional but recommended)
handler404 = 'core.views.custom_404_view'
handler500 = 'core.views.custom_500_view'
