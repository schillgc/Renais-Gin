"""
Management command to add test pledges for development.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Bottle, KarmaPledge
import hashlib
from datetime import datetime


class Command(BaseCommand):
    help = 'Add test pledges for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of test pledges to create'
        )
        parser.add_argument(
            '--user',
            type=str,
            default='testuser',
            help='Username to create pledges for'
        )

    def handle(self, *args, **options):
        count = options['count']
        username = options['user']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User {username} does not exist')
            )
            return

        # Get user's registered bottles without pledges
        available_bottles = Bottle.objects.filter(
            registered_to=user,
            status='registered'
        ).exclude(karmapledge__isnull=False)

        if not available_bottles:
            self.stdout.write(
                self.style.ERROR(f'No available bottles found for user {username}')
            )
            return

        pledges_created = 0
        sample_pledges = [
            {
                'text': "I pledge to use this $5 rebate to plant 10 native trees in my local park to support biodiversity and create a greener community space for everyone to enjoy.",
                'plan': "I'll coordinate with the city parks department to identify appropriate native species and organize a community planting day next month with my neighbors.",
                'type': 'environmental'
            },
            {
                'text': "I pledge to use this $5 rebate to purchase supplies for a neighborhood cleanup event to remove litter and beautify our shared spaces.",
                'plan': "I will organize volunteers, get cleanup supplies from the local hardware store, and coordinate with the city for waste disposal after our cleanup day.",
                'type': 'community'
            },
            {
                'text': "I pledge to use this $5 rebate to create educational materials about sustainable living practices for my local community center.",
                'plan': "I'll design and print informational brochures about composting, recycling, and energy conservation to distribute at the community center's sustainability workshop.",
                'type': 'education'
            },
            {
                'text': "I pledge to use this $5 rebate to support a local food bank by purchasing fresh produce for families in need in our community.",
                'plan': "I will visit the local farmers market, use the rebate to buy fresh vegetables, and deliver them to our neighborhood food bank distribution center.",
                'type': 'community'
            },
            {
                'text': "I pledge to use this $5 rebate to install a small pollinator garden in my backyard to support local bee and butterfly populations.",
                'plan': "I'll purchase native flowering plants from a local nursery and create a designated pollinator-friendly area in my garden with proper habitat features.",
                'type': 'environmental'
            }
        ]

        for i, bottle in enumerate(available_bottles[:count]):
            pledge_data = sample_pledges[i % len(sample_pledges)]

            # Generate submission ID
            submission_id = hashlib.sha256(
                f"{user.id}{bottle.bottle_id}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16]

            pledge = KarmaPledge.objects.create(
                user=user,
                bottle=bottle,
                pledge_text=pledge_data['text'],
                impact_plan=pledge_data['plan'],
                impact_type=pledge_data['type'],
                sentiment_score=0.8,  # High score for sample pledges
                status='pending',
                submission_id=submission_id
            )

            pledges_created += 1
            self.stdout.write(
                self.style.SUCCESS(f'Created pledge: {pledge.submission_id}')
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {pledges_created} test pledges for user {username}'
            )
        )
