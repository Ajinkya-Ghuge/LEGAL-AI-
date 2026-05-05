"""
Health check endpoint — GET /api/health/
Returns system status for monitoring.
"""
from django.urls import path
from django.http import JsonResponse
from django.db import connection
import sys


def health_check(request):
    # DB check
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False

    # PyMuPDF check
    try:
        import fitz
        fitz_ok = True
        fitz_version = fitz.__version__
    except ImportError:
        fitz_ok = False
        fitz_version = None

    # Gemini check
    try:
        import google.generativeai
        gemini_ok = True
    except ImportError:
        gemini_ok = False

    all_ok = db_ok

    return JsonResponse({
        "status":   "ok" if all_ok else "degraded",
        "database": "ok" if db_ok else "error",
        "pymupdf":  fitz_version if fitz_ok else "not installed",
        "gemini":   "ok" if gemini_ok else "not installed",
        "python":   sys.version.split()[0],
        "platform": "LegalAI Django Backend v1.0",
    }, status=200 if all_ok else 503)


urlpatterns = [
    path("", health_check),
]
