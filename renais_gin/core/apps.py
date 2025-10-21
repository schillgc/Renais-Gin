from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core'

    def ready(self):
        try:
            import core.signals
        except ImportError:
            # Signals module doesn't exist yet, that's ok
            pass
