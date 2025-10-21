"""
Management command to initialize the AI ecosystem.
"""

from django.core.management.base import BaseCommand
from core.ai_services import RenaissanceAICore


class Command(BaseCommand):
    help = 'Initialize the Renais AI ecosystem and test basic functionality'

    def handle(self, *args, **options):
        self.stdout.write('Initializing Renais AI Ecosystem...')

        try:
            # Initialize AI core
            ai_core = RenaissanceAICore()
            ai_core.initialize_ecosystem()

            # Test basic functionality
            self.stdout.write('Testing AI validation...')

            test_pledge = "I pledge to use this $5 rebate to plant 10 native trees in my local park."
            test_plan = "I'll coordinate with the parks department and organize a community planting day."

            validation_result = ai_core.process_pledge_submission(
                'test_user', 'test_bottle', test_pledge, test_plan
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'AI Validation Test: {validation_result["status"]} '
                    f'(Score: {validation_result.get("score", "N/A")})'
                )
            )

            # Test impact classification
            impact_type = ai_core.classify_impact_type(test_plan)
            self.stdout.write(
                self.style.SUCCESS(f'Impact Classification Test: {impact_type}')
            )

            # Test QR code generation
            bottle_data = {
                'bottle_id': 'DEMO_001',
                'batch_id': 'BATCH_DEMO',
                'production_date': '2023-10-01',
                'terroir_region': 'Chablis',
                'terroir_vintage': '2022'
            }

            qr_path = ai_core.bottle_manager.generate_bottle_qr(
                'DEMO_001', bottle_data
            )
            self.stdout.write(
                self.style.SUCCESS(f'QR Code Generation Test: {qr_path}')
            )

            self.stdout.write(
                self.style.SUCCESS(
                    'Renais AI Ecosystem initialized successfully! '
                    'All systems are operational.'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error initializing AI ecosystem: {e}')
            )
