"""
Cases serializers.
"""
from rest_framework import serializers
from .models import Case


class CaseListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    claim_amount_display = serializers.ReadOnlyField()
    document_count = serializers.SerializerMethodField()
    draft_count    = serializers.SerializerMethodField()

    class Meta:
        model  = Case
        fields = [
            "id", "title", "case_no", "case_type", "status",
            "client_name", "accident_date", "claim_amount",
            "claim_amount_display", "created_at",
            "document_count", "draft_count",
        ]

    def get_document_count(self, obj):
        return obj.documents.count()

    def get_draft_count(self, obj):
        return obj.drafts.count()


class CaseDetailSerializer(serializers.ModelSerializer):
    """Full serializer for create / retrieve / update."""
    claim_amount_display = serializers.ReadOnlyField()

    class Meta:
        model  = Case
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_claim_amount(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Claim amount cannot be negative.")
        return value

    def validate_injuries(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Injuries must be a list of strings.")
        return value

    def validate_compensation(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Compensation must be a list of objects.")
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Each compensation item must be an object.")
            if "head" not in item or "amount" not in item:
                raise serializers.ValidationError(
                    "Each compensation item must have 'head' and 'amount' keys."
                )
        return value
