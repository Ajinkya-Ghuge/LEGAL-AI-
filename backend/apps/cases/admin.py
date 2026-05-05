from django.contrib import admin
from .models import Case


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display  = ["id", "case_no", "title", "client_name", "case_type", "status", "claim_amount", "created_at"]
    list_filter   = ["status", "case_type"]
    search_fields = ["title", "case_no", "client_name"]
    ordering      = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]
