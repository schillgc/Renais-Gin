# File: renais_gin/core/management/commands/populate_test_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import (Bottle, KarmaPledge, UserProfile, CommunityCircle, MovementMetrics)
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Populate database with comprehensive test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of test users to create',
        )
        parser.add_argument(
            '--bottles',
            type=int,
            default=25,
            help='Number of bottles per user',
        )

    def handle(self, *args, **options):
        num_users = options['users']
        num_bottles = options['bottles']

        self.stdout.write('Creating test data...')

        # Create test users with profiles
        users = []
        countries = ['United States', 'United Kingdom', 'France', 'Germany', 'Canada', 'Australia', 'Japan']

        for i in range(num_users):
            username = f'testuser_{i + 1}'
            email = f'testuser{i + 1}@renaisgin.com'

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'Test',
                    'last_name': f'User {i + 1}'
                }
            )

            if created:
                user.set_password('testpass123')
                user.save()

                # Create user profile
                profile, _ = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'karma_score': random.uniform(0, 50),
                        'country': random.choice(countries)
                    }
                )

                self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))

            users.append(user)

        # Create bottles and pledges
        terroir_options = [
            {
                "region": "Chablis", "vintage": "2022", "soil_type": "Kimmeridgian limestone",
                "grapes": "Chardonnay", "harvest_date": "2022-09-15", "elevation": "150m",
                "climate": "Cool continental", "rainfall": "650mm", "sun_exposure": "South-facing"
            },
            {
                "region": "Burgundy", "vintage": "2021", "soil_type": "Clay-limestone",
                "grapes": "Pinot Noir", "harvest_date": "2021-09-20", "elevation": "200m",
                "climate": "Temperate continental", "rainfall": "700mm", "sun_exposure": "East-facing"
            },
            {
                "region": "Champagne", "vintage": "2020", "soil_type": "Chalk",
                "grapes": "Pinot Meunier", "harvest_date": "2020-09-10", "elevation": "100m",
                "climate": "Cool continental", "rainfall": "600mm", "sun_exposure": "South-facing"
            },
            {
                "region": "Bordeaux", "vintage": "2019", "soil_type": "Gravel",
                "grapes": "Cabernet Sauvignon", "harvest_date": "2019-10-05", "elevation": "50m",
                "climate": "Maritime", "rainfall": "900mm", "sun_exposure": "Southwest-facing"
            }
        ]

        pledge_templates = [
            ("I will plant 10 native trees in my local park to support biodiversity.",
             "I'll coordinate with the local parks department and organize a community planting day."),
            ("I will donate school supplies to 20 underprivileged children in my community.",
             "I'll purchase supplies from local stores and work with schools to distribute them."),
            ("I will organize a beach cleanup event with at least 30 volunteers.",
             "I'll partner with local environmental groups and promote the event on social media."),
            ("I will teach coding skills to 5 teenagers from low-income families.",
             "I'll offer free weekly classes at the community center over 8 weeks."),
            ("I will start a community garden that produces food for local food banks.",
             "I'll secure a plot of land, recruit volunteers, and coordinate with food banks for distribution."),
            ("I will reduce my household waste by 50% through composting and recycling.",
             "I'll set up a composting system and educate my family on proper recycling practices."),
            ("I will mentor 3 young entrepreneurs in sustainable business practices.",
             "I'll offer monthly guidance sessions and connect them with my professional network."),
        ]

        batch_ids = [f"BATCH_{i:03d}" for i in range(1, 11)]

        bottles_created = 0
        pledges_created = 0

        for user in users:
            user_bottle_count = random.randint(1, num_bottles)

            for i in range(user_bottle_count):
                bottle_id = f"BOT_{user.id}_{i + 1:04d}"

                bottle, created = Bottle.objects.get_or_create(
                    bottle_id=bottle_id,
                    defaults={
                        'batch_id': random.choice(batch_ids),
                        'production_date': date.today() - timedelta(days=random.randint(30, 730)),
                        'terroir_data': random.choice(terroir_options),
                        'registered': True,
                        'registered_to': user,
                        'registration_date': date.today() - timedelta(days=random.randint(1, 180))
                    }
                )

                if created:
                    bottles_created += 1

                    # Create pledge for 70% of bottles
                    if random.random() < 0.7:
                        pledge_text, impact_plan = random.choice(pledge_templates)
                        impact_types = ['environmental', 'community', 'education', 'other']

                        pledge = KarmaPledge.objects.create(
                            user=user,
                            bottle=bottle,
                            pledge_text=pledge_text,
                            impact_plan=impact_plan,
                            impact_type=random.choice(impact_types),
                            status=random.choice(['pending', 'approved', 'approved', 'needs_review']),
                            approvals=random.randint(0, 5),
                            timestamp=date.today() - timedelta(days=random.randint(1, 180))
                        )
                        pledges_created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {bottles_created} bottles'))
        self.stdout.write(self.style.SUCCESS(f'Created {pledges_created} pledges'))

        # Create community circles
        circle_names = [
            ("Green Warriors", "Los Angeles, CA"),
            ("Community Builders", "New York, NY"),
            ("Education First", "Chicago, IL"),
            ("Sustainable Living", "San Francisco, CA"),
            ("Impact Makers", "Seattle, WA"),
        ]

        circles_created = 0
        for name, location in circle_names:
            leader = random.choice(users)
            circle, created = CommunityCircle.objects.get_or_create(
                name=name,
                defaults={
                    'leader': leader,
                    'location': location,
                    'description': f'A community dedicated to making positive change in {location}.'
                }
            )

            if created:
                # Add random members
                members = random.sample(users, k=random.randint(3, 8))
                circle.members.set(members)
                circles_created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {circles_created} community circles'))

        # Update movement metrics
        from core.services import MovementMetricsService
        MovementMetricsService.update_metrics()

        self.stdout.write(self.style.SUCCESS('Test data population complete!'))


# File: renais_gin/core/management/commands/create_demo_user.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile, Bottle, KarmaPledge
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Create a demo user with sample data for demonstrations'

    def handle(self, *args, **options):
        # Create or get demo user
        demo_user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@renaisgin.com',
                'first_name': 'Demo',
                'last_name': 'User',
            }
        )

        if created:
            demo_user.set_password('demo123')
            demo_user.save()
            self.stdout.write(self.style.SUCCESS('Created demo user'))
        else:
            self.stdout.write(self.style.WARNING('Demo user already exists'))

        # Create or get profile
        profile, _ = UserProfile.objects.get_or_create(
            user=demo_user,
            defaults={
                'karma_score': 25.0,
                'country': 'United States',
            }
        )

        # Create sample bottles with pledges
        bottles_data = [
            {
                'bottle_id': 'DEMO_001',
                'batch_id': 'BATCH_001',
                'pledge': 'I will organize a community cleanup event in my neighborhood.',
                'impact': 'I will recruit 20+ volunteers and partner with local businesses for supplies.',
                'type': 'environmental'
            },
            {
                'bottle_id': 'DEMO_002',
                'batch_id': 'BATCH_002',
                'pledge': 'I will teach coding to underprivileged youth at the community center.',
                'impact': 'I will conduct 8-week free classes every Saturday afternoon.',
                'type': 'education'
            },
            {
                'bottle_id': 'DEMO_003',
                'batch_id': 'BATCH_001',
                'pledge': 'I will donate food to the local food bank every month.',
                'impact': 'I will contribute non-perishable items worth at least $50 monthly.',
                'type': 'community'
            }
        ]

        for data in bottles_data:
            bottle, created = Bottle.objects.get_or_create(
                bottle_id=data['bottle_id'],
                defaults={
                    'batch_id': data['batch_id'],
                    'production_date': date.today() - timedelta(days=60),
                    'terroir_data': {
                        "region": "Chablis",
                        "vintage": "2022",
                        "soil_type": "Kimmeridgian limestone",
                        "grapes": "Chardonnay"
                    },
                    'registered': True,
                    'registered_to': demo_user,
                    'registration_date': date.today() - timedelta(days=30)
                }
            )

            if created:
                # Create pledge
                KarmaPledge.objects.create(
                    user=demo_user,
                    bottle=bottle,
                    pledge_text=data['pledge'],
                    impact_plan=data['impact'],
                    impact_type=data['type'],
                    status='approved',
                    approvals=3,
                    timestamp=date.today() - timedelta(days=25)
                )
                self.stdout.write(self.style.SUCCESS(f'Created bottle {data["bottle_id"]} with pledge'))

        self.stdout.write(self.style.SUCCESS('\nDemo user setup complete!'))
        self.stdout.write('Username: demo')
        self.stdout.write('Password: demo123')
