# core/management/commands/init_ai_system.py
from django.core.management.base import BaseCommand
from ai_agents.services import AIService


class Command(BaseCommand):
    help = 'Initialize AI system and load initial models'

    def handle(self, *args, **options):
        self.stdout.write('Initializing Renais AI System...')

        # Initialize AI service
        ai_service = AIService()

        self.stdout.write(
            self.style.SUCCESS('AI System initialized successfully!')
        )
