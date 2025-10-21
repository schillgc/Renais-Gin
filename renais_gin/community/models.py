# community/models.py
from django.db import models
from core.models import User

class CommunityCircle(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_circles')
    members = models.ManyToManyField(User, related_name='community_circles', blank=True)
    max_members = models.IntegerField(default=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CommunityStory(models.Model):
    circle = models.ForeignKey(CommunityCircle, on_delete=models.CASCADE, related_name='stories')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    impact_metrics = models.JSONField(default=dict, blank=True)  # e.g., {"trees_planted": 10, "people_helped": 50}
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
