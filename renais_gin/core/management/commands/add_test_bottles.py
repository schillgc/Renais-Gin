"""
Management command to add test bottles for development.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Bottle
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Add test bottles for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of test bottles to create'
        )
        parser.add_argument(
            '--user',
            type=str,
            default='testuser',
            help='Username to assign bottles to'
        )

    def handle(self, *args, **options):
        count = options['count']
        username = options['user']

        # Get or create user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'password': 'testpass123'
            }
        )

        if created:
            self.stdout.write(
                self.style.WARNING(f'Created new user: {username}')
            )

        regions = ['Chablis', 'Burgundy', 'Champagne', 'Loire Valley', 'Provence']
        vintages = ['2020', '2021', '2022', '2023']

        bottles_created = 0

        for i in range(count):
            bottle_id = f"TEST_{i + 1:03d}"

            # Skip if bottle already exists
            if Bottle.objects.filter(bottle_id=bottle_id).exists():
                self.stdout.write(
                    self.style.WARNING(f'Bottle {bottle_id} already exists, skipping...')
                )
                continue

            bottle = Bottle.objects.create(
                bottle_id=bottle_id,
                batch_id=f"BATCH_{random.randint(100, 999)}",
                production_date=date.today() - timedelta(days=random.randint(30, 365)),
                terroir_region=random.choice(regions),
                terroir_vintage=random.choice(vintages),
                registered_to=user,
                status='registered'
            )

            bottles_created += 1
            self.stdout.write(
                self.style.SUCCESS(f'Created bottle: {bottle.bottle_id}')
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {bottles_created} test bottles for user {username}'
            )
        )
