from django.contrib import admin
from .models import Draft


@admin.register(Draft)
class DraftAdmin(admin.ModelAdmin):
    list_display  = ["id", "title", "case", "draft_type", "version", "status", "ai_generated", "created_at"]
    list_filter   = ["draft_type", "status", "ai_generated"]
    search_fields = ["title", "content", "ref_no"]
    ordering      = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]
