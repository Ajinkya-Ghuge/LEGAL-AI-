"""
LegalAI Web — URL patterns for all HTML pages and AJAX endpoints.
"""
from django.urls import path
from . import views

urlpatterns = [
    # ── Pages ─────────────────────────────────────────────────────────────
    path("",                          views.index,            name="index"),
    path("dashboard/",                views.dashboard,        name="dashboard"),
    path("cases/",                    views.cases_list,       name="cases_list"),
    path("cases/new/",                views.new_case,         name="new_case"),
    path("cases/<int:case_id>/",      views.case_workspace,   name="case_workspace"),
    path("timeline/",                 views.timeline,         name="timeline"),
    path("draft-editor/",             views.draft_editor,     name="draft_editor"),
    path("medical-analysis/",         views.medical_analysis, name="medical_analysis"),
    path("compensation/",             views.compensation,     name="compensation"),
    path("ask/",                      views.ask_question,     name="ask_question"),

    # ── Case sub-pages (sidebar nav) ──────────────────────────────────────
    path("cases/<int:case_id>/injuries/",    views.case_injuries,    name="case_injuries"),
    path("cases/<int:case_id>/treatment/",   views.case_treatment,   name="case_treatment"),
    path("cases/<int:case_id>/expenses/",    views.case_expenses,    name="case_expenses"),
    path("cases/<int:case_id>/compensation/",views.case_compensation,name="case_compensation"),
    path("cases/<int:case_id>/reports/",     views.case_reports,     name="case_reports"),
    path("cases/<int:case_id>/drafts/",      views.case_drafts,      name="case_drafts"),

    # ── AJAX endpoints ────────────────────────────────────────────────────
    path("api/chat/",                 views.api_chat,             name="api_chat"),
    path("api/save-draft/",           views.api_save_draft,       name="api_save_draft"),
    path("api/generate-draft/",       views.api_generate_draft,   name="api_generate_draft"),
    path("api/upload-document/",      views.api_upload_document,  name="api_upload_document"),
    path("api/compensation/calculate/", views.api_compensation_calculate, name="api_compensation_calculate"),
]
