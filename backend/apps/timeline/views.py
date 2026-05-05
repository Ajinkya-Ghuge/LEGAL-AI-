"""
Timeline views.

GET  /api/timeline/<case_id>/          — list timeline events for a case
POST /api/timeline/                    — create timeline event
PUT  /api/timeline/<id>/               — update event
DELETE /api/timeline/<id>/             — delete event

GET  /api/timeline/summary/<case_id>/  — get medical summary
POST /api/timeline/summary/generate/   — AI-generate medical summary
"""
import logging

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.cases.models import Case
from apps.documents.models import Document
from apps.documents.services import extract_text_preview
from .models import TimelineEvent, MedicalSummary
from .serializers import (
    TimelineEventSerializer,
    MedicalSummarySerializer,
    MedicalSummaryCreateSerializer,
)

logger = logging.getLogger(__name__)


def _ai_generate(prompt: str) -> str:
    """Call Gemini — graceful fallback if not installed."""
    try:
        import google.generativeai as genai
        from django.conf import settings
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model    = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except ImportError:
        return "[AI unavailable — install google-generativeai]"
    except Exception as exc:
        logger.exception("Gemini call failed")
        return f"[AI Error: {exc}]"


class TimelineEventViewSet(viewsets.ModelViewSet):
    """
    CRUD for timeline events.
    Filter by case: GET /api/timeline/?case_id=<id>
    """
    queryset         = TimelineEvent.objects.select_related("case").all()
    serializer_class = TimelineEventSerializer
    filter_backends  = [filters.OrderingFilter]
    ordering_fields  = ["date", "order", "created_at"]
    ordering         = ["date", "order"]

    def get_queryset(self):
        qs = TimelineEvent.objects.select_related("case").all()
        case_id = self.request.query_params.get("case_id")
        if case_id:
            qs = qs.filter(case_id=case_id)
        tag = self.request.query_params.get("tag")
        if tag:
            qs = qs.filter(tag=tag.upper())
        return qs

    # ── GET /api/timeline/summary/<case_id>/ ─────────────────────────────
    @action(detail=False, methods=["get"], url_path="summary/(?P<case_id>[0-9]+)")
    def get_summary(self, request, case_id=None):
        try:
            summary = MedicalSummary.objects.get(case_id=case_id)
            return Response(MedicalSummarySerializer(summary).data)
        except MedicalSummary.DoesNotExist:
            return Response(
                {"detail": "No medical summary found for this case."},
                status=status.HTTP_404_NOT_FOUND,
            )

    # ── POST /api/timeline/summary/generate/ ─────────────────────────────
    @action(detail=False, methods=["post"], url_path="summary/generate")
    def generate_summary(self, request):
        """
        AI-generate a medical summary for a case.
        Uses uploaded documents or provided text.
        """
        serializer = MedicalSummaryCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        case_id     = serializer.validated_data["case_id"]
        document_id = serializer.validated_data.get("document_id")
        case_text   = serializer.validated_data.get("case_text", "")

        # Validate case
        try:
            case = Case.objects.get(pk=case_id)
        except Case.DoesNotExist:
            return Response({"error": f"Case {case_id} not found."}, status=404)

        # Get text from document if provided
        if document_id:
            try:
                doc = Document.objects.get(pk=document_id, case=case)
                case_text = doc.extracted_text or extract_text_preview(doc.file.path)
            except Document.DoesNotExist:
                return Response({"error": "Document not found."}, status=404)

        # Fall back to most recent processed document
        if not case_text:
            latest_doc = (
                case.documents
                .filter(processing_status=Document.PROCESSING_DONE)
                .order_by("-uploaded_at")
                .first()
            )
            if latest_doc:
                case_text = latest_doc.extracted_text[:8000]

        if not case_text:
            return Response(
                {"error": "No case text available. Upload a document first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Load vault context
        vault_text = _load_vault()

        prompt = f"""
You are a SENIOR INDIAN MACT ADVOCATE with 20+ years of courtroom experience.

STRICT RULES:
- DO NOT guess facts. If information is missing, write: NOT FOUND
- Use ONLY given Case + Vault text
- Use Indian legal tone (court style)
- Output must be VERY DETAILED and PROFESSIONAL

Generate a FULL professional MACT injury case report with:

1) MEDICAL CHRONOLOGY
   - Admission date, Surgery date, Hospital stay, Discharge date, Follow-ups

2) INJURIES IDENTIFIED
   - List injuries with severity assessment

3) TREATMENT SUMMARY
   - Surgery details, Medicines, Rehabilitation

4) FINANCIAL & COMPENSATION ANALYSIS
   - Actual medical costs, Future expenses, Loss of income, Pain & suffering

5) CLAIM HEADS UNDER MOTOR VEHICLES ACT
   - Medical expenses, Loss of income, Pain & suffering, Future disability,
     Loss of amenities, Conveyance & diet

6) MISSING DOCUMENTS CHECKLIST
   - FIR, Income proof, Disability certificate, Insurance papers

7) RELEVANT LEGAL SECTIONS (with explanation)
   - MV Act 166, 168, 173

8) LAWYER INSIGHTS
   - Strength of claim (Strong/Moderate/Weak)
   - Risks
   - Recommended legal strategy

==================== LEGAL VAULT ====================
{vault_text}
=====================================================

==================== CASE FILE =======================
{case_text}
=====================================================
"""
        ai_output = _ai_generate(prompt)

        # Upsert MedicalSummary
        summary, _ = MedicalSummary.objects.update_or_create(
            case=case,
            defaults={
                "notes":         ai_output,
                "ai_raw_output": ai_output,
                "injuries":      case.injuries or [],
            },
        )

        return Response({
            "success": True,
            "summary": MedicalSummarySerializer(summary).data,
        })


def _load_vault(max_chars: int = 6000) -> str:
    """Load vault PDFs for RAG context."""
    from django.conf import settings
    import os

    vault_path = settings.VAULT_PATH
    if not os.path.exists(vault_path):
        return ""

    knowledge = ""
    try:
        import fitz
        for root, _, files in os.walk(vault_path):
            for f in files:
                if f.endswith(".pdf"):
                    try:
                        doc  = fitz.open(os.path.join(root, f))
                        text = "".join(p.get_text() for p in doc)[:2000]
                        knowledge += f"\n--- SOURCE: {f} ---\n{text}\n"
                    except Exception:
                        pass
    except ImportError:
        pass

    return knowledge[:max_chars]
