# community/admin.py
from django.contrib import admin
from .models import CommunityCircle, CommunityStory

admin.site.register(CommunityCircle)
admin.site.register(CommunityStory)
