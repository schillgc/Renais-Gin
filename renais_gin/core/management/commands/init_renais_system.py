# core/management/commands/init_renais_system.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from bottles.models import BottleBatch, Bottle
from datetime import date


class Command(BaseCommand):
    help = 'Initialize the Renais Gin system with sample data'

    def handle(self, *args, **options):
        User = get_user_model()

        self.stdout.write('Initializing Renais Gin System...')

        # Create sample batch
        batch, created = BottleBatch.objects.get_or_create(
            batch_id='BATCH_2023_CHABLIS',
            defaults={
                'production_date': date(2023, 10, 1),
                'region': 'Chablis',
                'vintage': '2022',
                'terroir_data': {
                    'soil_type': 'Kimmeridgian clay',
                    'climate': 'Continental',
                    'elevation': '150m'
                },
                'total_bottles': 1000
            }
        )

        if created:
            self.stdout.write(f'Created batch: {batch.batch_id}')

        # Create sample bottles
        for i in range(1, 11):
            bottle_id = f'BOT_2023_{i:03d}'
            bottle, created = Bottle.objects.get_or_create(
                bottle_id=bottle_id,
                defaults={'batch': batch}
            )
            if created:
                self.stdout.write(f'Created bottle: {bottle_id}')

        self.stdout.write(
            self.style.SUCCESS('Renais Gin system initialized successfully!')
        )


