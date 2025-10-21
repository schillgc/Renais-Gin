"""
Serializers for Renais Gin API
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from core.models import Bottle, KarmaPledge, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class BottleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bottle
        fields = [
            'id', 'bottle_id', 'batch_id', 'production_date',
            'terroir_region', 'terroir_vintage', 'registered',
            'registered_to', 'registration_date', 'qr_code_path'
        ]
        read_only_fields = ['id', 'registration_date', 'qr_code_path']


class PledgeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    bottle_id = serializers.CharField(max_length=100)

    class Meta:
        model = KarmaPledge
        fields = [
            'id', 'user', 'bottle_id', 'pledge_text', 'impact_plan',
            'submission_id', 'status', 'approvals', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'submission_id', 'status',
            'approvals', 'created_at', 'updated_at'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'bio', 'location', 'country',
            'preferred_causes', 'impact_score', 'member_since'
        ]
        read_only_fields = ['id', 'user', 'impact_score', 'member_since']


class MetricsSerializer(serializers.Serializer):
    """Serializer for movement metrics"""
    movement_metrics = serializers.DictField()
    impact_by_category = serializers.DictField()
    community_engagement = serializers.DictField()
    global_reach = serializers.DictField()
    timestamp = serializers.DateTimeField()

    def validate(self, data):
        """Validate metrics data"""
        required_metrics = ['total_pledges', 'total_rebates', 'community_size', 'impact_stories']
        if not all(metric in data['movement_metrics'] for metric in required_metrics):
            raise serializers.ValidationError("Missing required movement metrics")
        return data


class ValidationResultSerializer(serializers.Serializer):
    """Serializer for AI validation results"""
    status = serializers.ChoiceField(choices=['approved', 'rejected', 'needs_review'])
    score = serializers.FloatField(min_value=0.0, max_value=1.0)
    reason = serializers.CharField(required=False, allow_blank=True)


class RecommendationSerializer(serializers.Serializer):
    """Serializer for personalized recommendations"""
    type = serializers.ChoiceField(choices=['cause', 'content'])
    value = serializers.CharField()
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
