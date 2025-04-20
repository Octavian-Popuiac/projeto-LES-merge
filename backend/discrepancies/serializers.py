from rest_framework import serializers
from .models import Discrepancy

class DiscrepancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Discrepancy
        fields = ["id", "project", "example", "labels", "created_at", "status"]

class DiscrepancyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discrepancy
        fields = ["id", "project", "created_at", "status", "example", "labels"]

class DiscrepancyItemSerializer(serializers.Serializer):
    text = serializers.CharField()
    start = serializers.IntegerField(required=False)
    end = serializers.IntegerField(required=False)
    label_user_a = serializers.CharField()
    label_user_b = serializers.CharField()


class LabelStatsSerializer(serializers.Serializer):
    label = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class DiscrepancyDetectSerializer(serializers.Serializer):
    example_id = serializers.IntegerField()
    example_text = serializers.CharField()
    label_stats = serializers.ListField(child=LabelStatsSerializer())
    type = serializers.CharField()
