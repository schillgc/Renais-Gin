from rest_framework import serializers
from .models import KarmaPledge, KarmaValidation, KarmaRebate


class KarmaPledgeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    bottle = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = KarmaPledge
        fields = [
            'id', 'submission_id', 'user', 'bottle', 'pledge_text', 'impact_plan',
            'impact_type', 'status', 'ai_confidence_score', 'approvals',
            'rejections', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'submission_id', 'user', 'ai_confidence_score',
            'approvals', 'rejections', 'created_at', 'updated_at'
        ]


class KarmaPledgeCreateSerializer(serializers.ModelSerializer):
    bottle_id = serializers.CharField(write_only=True)

    class Meta:
        model = KarmaPledge
        fields = ['bottle_id', 'pledge_text', 'impact_plan', 'impact_type']

    def validate_bottle_id(self, value):
        from bottles.models import Bottle
        try:
            bottle = Bottle.objects.get(bottle_id=value, registered_to=self.context['request'].user)
            if hasattr(bottle, 'pledges'):
                raise serializers.ValidationError('Bottle already has a pledge')
            self.context['bottle'] = bottle
        except Bottle.DoesNotExist:
            raise serializers.ValidationError('Bottle not found or not registered to you')
        return value

    def create(self, validated_data):
        # Simplified implementation for now
        from .models import KarmaPledge
        import hashlib
        from datetime import datetime

        bottle_id = validated_data.pop('bottle_id')
        user = self.context['request'].user
        bottle = self.context['bottle']

        # Generate submission ID
        submission_id = hashlib.sha256(
            f"{user.id}{bottle.id}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        pledge = KarmaPledge.objects.create(
            submission_id=submission_id,
            user=user,
            bottle=bottle,
            **validated_data
        )

        return pledge


class KarmaValidationSerializer(serializers.ModelSerializer):
    validator = serializers.StringRelatedField(read_only=True)
    pledge_submission_id = serializers.CharField(source='pledge.submission_id', read_only=True)

    class Meta:
        model = KarmaValidation
        fields = ['id', 'pledge', 'pledge_submission_id', 'validator', 'approval', 'comments', 'created_at']
        read_only_fields = ['id', 'validator', 'created_at']


class KarmaRebateSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    pledge_submission_id = serializers.CharField(source='pledge.submission_id', read_only=True)

    class Meta:
        model = KarmaRebate
        fields = [
            'id', 'pledge', 'pledge_submission_id', 'user', 'amount',
            'status', 'processed_date', 'transaction_id', 'created_at'
        ]
        read_only_fields = fields
