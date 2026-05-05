"""
Timeline serializers.
"""
from rest_framework import serializers
from .models import TimelineEvent, MedicalSummary


class TimelineEventSerializer(serializers.ModelSerializer):
    tag_display = serializers.SerializerMethodField()

    class Meta:
        model  = TimelineEvent
        fields = [
            "id", "case", "date", "title", "doctor",
            "description", "tag", "tag_display",
            "medications", "order", "created_at",
        ]
        read_only_fields = ["id", "created_at", "tag_display"]

    def get_tag_display(self, obj):
        return obj.get_tag_display()

    def validate_medications(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Medications must be a list of strings.")
        return value


class MedicalSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model  = MedicalSummary
        fields = [
            "id", "case",
            "injuries", "treatments", "medications", "icd_codes",
            "economic_damages", "non_economic_damages",
            "notes", "missing_docs",
            "case_strength", "legal_strategy",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MedicalSummaryCreateSerializer(serializers.Serializer):
    """Input for the generate_summary action."""
    case_id     = serializers.IntegerField()
    document_id = serializers.IntegerField(required=False, allow_null=True)
    case_text   = serializers.CharField(required=False, allow_blank=True, default="")
