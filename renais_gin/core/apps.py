"""
App configuration for Renais Gin core application.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuration class for the core Renais Gin application.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Renais Gin Core'

    def ready(self):
        """
        Application initialization method.
        Called when Django starts.
        """
        # Import signal handlers - do this at the end to avoid circular imports
        try:
            import core.signals
        except ImportError:
            # Silently ignore if signals module doesn't exist yet
            pass
