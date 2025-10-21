# community/serializers.py
from rest_framework import serializers
from .models import CommunityCircle, CommunityStory


class CommunityCircleSerializer(serializers.ModelSerializer):
    leader = serializers.StringRelatedField()
    members = serializers.StringRelatedField(many=True)

    class Meta:
        model = CommunityCircle
        fields = '__all__'


class CommunityStorySerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    circle = serializers.StringRelatedField()

    class Meta:
        model = CommunityStory
        fields = '__all__'
