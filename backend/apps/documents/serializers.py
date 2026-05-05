"""
Documents serializers.
"""
from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """Full document serializer — used for responses."""
    file_size_kb = serializers.ReadOnlyField()
    filename     = serializers.ReadOnlyField()
    case_title   = serializers.SerializerMethodField()

    class Meta:
        model  = Document
        fields = [
            "id", "case", "case_title", "file", "filename",
            "original_name", "doc_type", "pages",
            "extracted_text", "page_texts",
            "processing_status", "processing_error",
            "file_size_kb", "uploaded_at",
        ]
        read_only_fields = [
            "id", "pages", "extracted_text", "page_texts",
            "processing_status", "processing_error",
            "file_size_kb", "filename", "uploaded_at",
        ]

    def get_case_title(self, obj):
        return obj.case.title if obj.case else None


class DocumentUploadSerializer(serializers.Serializer):
    """Validates the upload endpoint payload."""
    case_id  = serializers.IntegerField()
    file     = serializers.FileField()
    doc_type = serializers.ChoiceField(
        choices=Document.DOC_TYPE_CHOICES,
        default=Document.DOC_TYPE_OTHER,
        required=False,
    )

    def validate_file(self, value):
        # 50 MB limit
        max_size = 50 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("File size must be under 50 MB.")
        allowed = [".pdf", ".doc", ".docx", ".txt", ".jpg", ".jpeg", ".png"]
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed:
            raise serializers.ValidationError(
                f"File type '{ext}' not allowed. Allowed: {', '.join(allowed)}"
            )
        return value


class DocumentProcessSerializer(serializers.Serializer):
    """Validates the process endpoint payload."""
    document_id = serializers.IntegerField()
