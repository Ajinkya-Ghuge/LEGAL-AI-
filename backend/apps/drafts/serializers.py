"""
Drafts serializers.
"""
from rest_framework import serializers
from .models import Draft


class DraftListSerializer(serializers.ModelSerializer):
    """Lightweight — for list views."""
    draft_type_display = serializers.SerializerMethodField()
    status_display     = serializers.SerializerMethodField()
    case_title         = serializers.SerializerMethodField()

    class Meta:
        model  = Draft
        fields = [
            "id", "case", "case_title", "title",
            "draft_type", "draft_type_display",
            "status", "status_display",
            "version", "ai_generated", "ref_no",
            "created_at", "updated_at",
        ]

    def get_draft_type_display(self, obj):
        return obj.get_draft_type_display()

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_case_title(self, obj):
        return obj.case.title if obj.case else None


class DraftDetailSerializer(serializers.ModelSerializer):
    """Full serializer — includes content."""
    draft_type_display = serializers.SerializerMethodField()
    status_display     = serializers.SerializerMethodField()
    case_title         = serializers.SerializerMethodField()

    class Meta:
        model  = Draft
        fields = "__all__"
        read_only_fields = ["id", "version", "created_at", "updated_at"]

    def get_draft_type_display(self, obj):
        return obj.get_draft_type_display()

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_case_title(self, obj):
        return obj.case.title if obj.case else None


class DraftUpdateSerializer(serializers.Serializer):
    """Input for PUT /api/drafts/<id>/"""
    content             = serializers.CharField()
    title               = serializers.CharField(required=False, allow_blank=True)
    status              = serializers.ChoiceField(
        choices=Draft.STATUS_CHOICES, required=False
    )
    save_as_new_version = serializers.BooleanField(default=False)


class DraftGenerateSerializer(serializers.Serializer):
    """Input for POST /api/drafts/generate/"""
    case_id     = serializers.IntegerField()
    draft_type  = serializers.ChoiceField(choices=Draft.DRAFT_TYPE_CHOICES)
    document_id = serializers.IntegerField(required=False, allow_null=True)
    case_text   = serializers.CharField(required=False, allow_blank=True, default="")
    extra_notes = serializers.CharField(required=False, allow_blank=True, default="")
