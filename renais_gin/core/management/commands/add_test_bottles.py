from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Bottle
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Add test bottles with terroir data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of test bottles to create (default: 10)',
        )

    def handle(self, *args, **options):
        count = options['count']

        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@renaisgin.com',
                'password': 'testpassword123'
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created test user: {user.username}')
            )

        # Terroir data examples
        terroir_options = [
            {
                "region": "Chablis",
                "vintage": "2022",
                "soil_type": "Kimmeridgian limestone",
                "grapes": "Chardonnay",
                "harvest_date": "2022-09-15",
                "elevation": "150m",
                "climate": "Cool continental",
                "rainfall": "650mm",
                "sun_exposure": "South-facing"
            },
            {
                "region": "Burgundy",
                "vintage": "2021",
                "soil_type": "Clay-limestone",
                "grapes": "Pinot Noir",
                "harvest_date": "2021-09-20",
                "elevation": "200m",
                "climate": "Temperate continental",
                "rainfall": "700mm",
                "sun_exposure": "East-facing"
            },
            {
                "region": "Champagne",
                "vintage": "2020",
                "soil_type": "Chalk",
                "grapes": "Pinot Meunier",
                "harvest_date": "2020-09-10",
                "elevation": "100m",
                "climate": "Cool continental",
                "rainfall": "600mm",
                "sun_exposure": "South-facing"
            }
        ]

        # Batch IDs
        batch_ids = ["BATCH_001", "BATCH_002", "BATCH_003"]

        # Create test bottles
        bottles_created = 0
        for i in range(count):
            # Select random terroir data
            terroir_data = random.choice(terroir_options)
            batch_id = random.choice(batch_ids)

            # Calculate production date (within last 2 years)
            production_date = date.today() - timedelta(days=random.randint(30, 730))

            bottle = Bottle.objects.create(
                bottle_id=f"TEST_{i + 1:03d}",
                batch_id=batch_id,
                production_date=production_date,
                terroir_data=terroir_data,
                registered=random.choice([True, False]),
                registered_to=user if random.choice([True, False]) else None
            )

            if bottle.registered:
                bottles_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created bottle {bottle.bottle_id} with terroir data')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Created unregistered bottle {bottle.bottle_id}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {bottles_created} registered bottles and {count - bottles_created} unregistered bottles')
        )
