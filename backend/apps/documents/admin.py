from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display  = ["id", "original_name", "case", "doc_type", "pages", "processing_status", "uploaded_at"]
    list_filter   = ["doc_type", "processing_status"]
    search_fields = ["original_name", "extracted_text"]
    ordering      = ["-uploaded_at"]
    readonly_fields = ["pages", "extracted_text", "page_texts", "processing_status", "processing_error", "uploaded_at"]
