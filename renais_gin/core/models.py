from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    karma_score = models.IntegerField(default=0)
    country = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    impact_story = models.TextField(blank=True)
    is_community_validator = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # Preferences
    preferred_causes = models.JSONField(default=list, blank=True)
    notification_preferences = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    total_pledges = models.IntegerField(default=0)
    approved_pledges = models.IntegerField(default=0)
    total_rebates = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} Profile"
