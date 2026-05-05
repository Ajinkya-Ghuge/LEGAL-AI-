from django.contrib import admin
from .models import TimelineEvent, MedicalSummary


@admin.register(TimelineEvent)
class TimelineEventAdmin(admin.ModelAdmin):
    list_display  = ["id", "case", "date", "title", "tag", "doctor"]
    list_filter   = ["tag"]
    search_fields = ["title", "description", "doctor"]
    ordering      = ["date", "order"]


@admin.register(MedicalSummary)
class MedicalSummaryAdmin(admin.ModelAdmin):
    list_display  = ["id", "case", "case_strength", "created_at"]
    search_fields = ["notes"]
    readonly_fields = ["created_at", "updated_at"]
