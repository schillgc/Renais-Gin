# core/management/commands/update_karma_scores.py
from django.core.management.base import BaseCommand
from core.models import User


class Command(BaseCommand):
    help = 'Update karma scores based on user activity'

    def handle(self, *args, **options):
        users = User.objects.all()

        for user in users:
            profile = user.profile
            # Calculate karma score based on various factors
            new_karma = (
                    profile.approved_pledges * 10 +
                    profile.total_pledges * 2 +
                    int(profile.total_rebates) * 5
            )

            if user.karma_score != new_karma:
                user.karma_score = new_karma
                user.save()
                self.stdout.write(f'Updated {user.username} karma to {new_karma}')

        self.stdout.write(
            self.style.SUCCESS('Karma scores updated successfully!')
        )
