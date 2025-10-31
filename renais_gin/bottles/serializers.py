from rest_framework import serializers
from .models import Bottle, BottleBatch


class BottleBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = BottleBatch
        fields = ['batch_id', 'production_date', 'region', 'vintage']


class BottleSerializer(serializers.ModelSerializer):
    batch = BottleBatchSerializer(read_only=True)
    is_eligible_for_pledge = serializers.SerializerMethodField()

    class Meta:
        model = Bottle
        fields = ['bottle_id', 'batch', 'is_registered', 'registered_to', 'is_eligible_for_pledge']

    def get_is_eligible_for_pledge(self, obj):
        return obj.is_registered and not obj.pledge_submitted
