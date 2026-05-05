"""
LegalAI — Root URL Configuration

Web pages:  /  /dashboard/  /cases/  /timeline/  /draft-editor/  etc.
REST API:   /api/cases/  /api/documents/  /api/timeline/  /api/drafts/
Admin:      /admin/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ── Admin ──────────────────────────────────────────────────────────────
    path("admin/", admin.site.urls),

    # ── REST API (DRF) ─────────────────────────────────────────────────────
    path("api/cases/",      include("apps.cases.urls")),
    path("api/documents/",  include("apps.documents.urls")),
    path("api/timeline/",   include("apps.timeline.urls")),
    path("api/drafts/",     include("apps.drafts.urls")),
    path("api/health/",     include("legalai.health")),

    # ── Web pages (HTML) — must be last ────────────────────────────────────
    path("", include("apps.web.urls")),
]

# Serve media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = "apps.web.views.error_404"
handler500 = "apps.web.views.error_500"
