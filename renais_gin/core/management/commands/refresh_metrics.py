from django.core.management.base import BaseCommand

from core.services import MovementMetricsService


class Command(BaseCommand):
    help = 'Refresh the stored movement metrics snapshot'

    def handle(self, *args, **options):
        metrics = MovementMetricsService.update_metrics()
        self.stdout.write(self.style.SUCCESS(
            f'Refreshed movement metrics at {metrics.last_updated.isoformat()}'
        ))
