"""
Context processors for Renais Gin core application.
"""

from django.conf import settings
from .services import RenaisGinService


def movement_metrics(request):
    """
    Add movement metrics to template context.
    """
    service = RenaisGinService()
    metrics = service.get_movement_metrics()

    return {
        'movement_metrics': metrics,
        'renais_settings': settings.RENAIS_SETTINGS,
    }


def user_context(request):
    """
    Add user-specific context to templates.
    """
    context = {}

    if request.user.is_authenticated:
        service = RenaisGinService()
        user_metrics = service.get_user_metrics(request.user)
        context['user_metrics'] = user_metrics

        # Add user profile if exists
        if hasattr(request.user, 'profile'):
            context['user_profile'] = request.user.profile

    return context
