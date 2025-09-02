from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile, MovementMetrics
from core.services import MovementMetricsService


class Command(BaseCommand):
    help = 'Initialize the Renais Gin ecosystem'

    def handle(self, *args, **options):
        self.stdout.write('Initializing Renais Gin AI Ecosystem...')

        # Create default movement metrics
        MovementMetricsService.update_metrics()

        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@renaisgin.com', 'adminpassword')
            self.stdout.write('Created admin user')

        self.stdout.write('Ecosystem initialized. Ready to craft a better world.')
