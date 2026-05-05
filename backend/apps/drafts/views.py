"""
Drafts views.

GET    /api/drafts/              — list drafts (filter by case_id)
POST   /api/drafts/generate/     — AI-generate a draft
GET    /api/drafts/<id>/         — retrieve draft
PUT    /api/drafts/<id>/         — save edited content (optionally as new version)
DELETE /api/drafts/<id>/         — delete draft
GET    /api/drafts/<id>/versions/ — list all versions of a draft
"""
import logging
from datetime import date

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.cases.models import Case
from apps.documents.models import Document
from apps.documents.services import extract_text_preview
from .models import Draft
from .serializers import (
    DraftListSerializer,
    DraftDetailSerializer,
    DraftUpdateSerializer,
    DraftGenerateSerializer,
)

logger = logging.getLogger(__name__)

# ── Draft type → prompt template mapping ─────────────────────────────────────
DRAFT_PROMPTS = {
    Draft.CLAIM_PETITION: """
Generate a PROFESSIONAL COURT-READY MACT Claim Petition under Section 166 of the Motor Vehicles Act, 1988.

Include ALL of the following sections:
1. Tribunal Heading (BEFORE THE HON'BLE MOTOR ACCIDENT CLAIMS TRIBUNAL)
2. Case Number
3. Parties (Petitioner vs Respondents — Driver, Owner, Insurance Company)
4. Facts of the Accident (date, time, place, vehicle number, manner of accident)
5. Medical History & Injuries (admission, surgery, discharge, injuries list)
6. Compensation Table (all heads: medical, income loss, pain & suffering, disability, amenities, diet)
7. Legal Grounds (Section 166, 168, 173 MV Act; negligence; vicarious liability)
8. Prayer Clause (specific amount with interest and costs)
9. Verification (signed by petitioner)

Use Indian court drafting tone. Times New Roman style. Formal legal language.
""",

    Draft.LEGAL_NOTICE: """
Generate a PROFESSIONAL LEGAL NOTICE to the Insurance Company and Vehicle Owner.

Include:
1. Advocate Header (Name, Address, Contact)
2. Date
3. "BY REGD. POST WITH ACK. DUE"
4. To: (Owner + Insurance Company)
5. Subject: Legal Notice for compensation under MV Act
6. Numbered paragraphs covering:
   - Accident facts
   - Injuries sustained
   - FIR details
   - Medical treatment
   - Liability of respondents
7. Demand clause (specific amount, 15-day deadline)
8. Legal warning (MACT proceedings)
9. Advocate signature

Use formal Indian legal notice format.
""",

    Draft.AFFIDAVIT: """
Generate a PROFESSIONAL AFFIDAVIT OF THE CLAIMANT for a MACT case.

Include:
1. Title: AFFIDAVIT OF THE CLAIMANT
2. Deponent details (name, age, address, occupation)
3. Numbered paragraphs:
   - Identity as petitioner
   - Truth of petition contents
   - Accident circumstances
   - Injuries and treatment
   - Financial losses
   - No contribution to accident
4. Verification clause
5. Deponent signature line
6. Notary/Oath Commissioner section

Use formal Indian affidavit format.
""",

    Draft.COMPENSATION: """
Generate a PROFESSIONAL STATEMENT OF COMPENSATION for a MACT case.

Include:
1. Title: STATEMENT OF COMPENSATION
2. Reference to Claim Petition u/s 166 MV Act
3. Introduction paragraph
4. Detailed compensation table with ALL heads:
   - Hospital Bills & Medical Expenses
   - Future Medical Expenses
   - Loss of Income during Treatment
   - Pain and Suffering
   - Loss of Amenities of Life
   - Special Diet, Attendant & Conveyance
   - Future Loss of Earning Capacity (if disability)
   - TOTAL
5. Note about revision based on medical evidence
6. Petitioner signature

Use Indian court format with proper rupee amounts.
""",

    Draft.WRITTEN_ARGS: """
Generate WRITTEN ARGUMENTS ON COMPENSATION for a MACT case.

Include:
1. Case heading
2. Arguments on:
   - Negligence of respondent
   - Medical expenses (with bills)
   - Loss of income (with calculation)
   - Pain & suffering (case law references)
   - Disability compensation (Sarla Verma formula)
   - Future medical expenses
3. Relevant case law:
   - Sarla Verma vs DTC (2009)
   - National Insurance vs Pranay Sethi (2017)
   - Raj Kumar vs Ajay Kumar (2011)
4. Prayer for enhanced compensation

Use Indian Supreme Court citation format.
""",
}


def _ai_generate(prompt: str) -> str:
    """Call Gemini — graceful fallback."""
    try:
        import google.generativeai as genai
        from django.conf import settings
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model    = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except ImportError:
        return "[AI unavailable — install: pip install google-generativeai]"
    except Exception as exc:
        logger.exception("Gemini call failed")
        return f"[AI Error: {exc}]"


class DraftViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for Drafts + generate + versioning.
    """
    queryset         = Draft.objects.select_related("case").all()
    filter_backends  = [filters.SearchFilter, filters.OrderingFilter]
    search_fields    = ["title", "content"]
    ordering_fields  = ["created_at", "version"]
    ordering         = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return DraftListSerializer
        return DraftDetailSerializer

    def get_queryset(self):
        qs = Draft.objects.select_related("case").all()
        case_id    = self.request.query_params.get("case_id")
        draft_type = self.request.query_params.get("draft_type")
        if case_id:
            qs = qs.filter(case_id=case_id)
        if draft_type:
            qs = qs.filter(draft_type=draft_type.upper())
        return qs

    # ── PUT /api/drafts/<id>/ — save edited content ───────────────────────
    def update(self, request, *args, **kwargs):
        draft      = self.get_object()
        serializer = DraftUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data    = serializer.validated_data
        content = data["content"]

        if data.get("save_as_new_version"):
            # Create new version, keep old one intact
            new_draft = draft.save_new_version(content)
            if data.get("title"):
                new_draft.title = data["title"]
            if data.get("status"):
                new_draft.status = data["status"]
            new_draft.save()
            return Response(DraftDetailSerializer(new_draft).data)
        else:
            # Update in place
            draft.content = content
            if data.get("title"):
                draft.title = data["title"]
            if data.get("status"):
                draft.status = data["status"]
            draft.save()
            return Response(DraftDetailSerializer(draft).data)

    # ── POST /api/drafts/generate/ ────────────────────────────────────────
    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        """
        AI-generate a legal draft for a case.
        """
        serializer = DraftGenerateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data        = serializer.validated_data
        case_id     = data["case_id"]
        draft_type  = data["draft_type"]
        document_id = data.get("document_id")
        case_text   = data.get("case_text", "")
        extra_notes = data.get("extra_notes", "")

        # Validate case
        try:
            case = Case.objects.get(pk=case_id)
        except Case.DoesNotExist:
            return Response({"error": f"Case {case_id} not found."}, status=404)

        # Get case text from document
        if document_id:
            try:
                doc = Document.objects.get(pk=document_id, case=case)
                case_text = doc.extracted_text or extract_text_preview(doc.file.path)
            except Document.DoesNotExist:
                return Response({"error": "Document not found."}, status=404)

        # Fall back to latest processed document
        if not case_text:
            latest = (
                case.documents
                .filter(processing_status=Document.PROCESSING_DONE)
                .order_by("-uploaded_at")
                .first()
            )
            if latest:
                case_text = latest.extracted_text[:8000]

        # Build case context from DB fields
        case_context = f"""
CASE DETAILS:
- Case: {case.case_no or 'N/A'} — {case.title}
- Petitioner: {case.client_name}, Age: {case.client_age or 'N/A'}
- Address: {case.client_address or 'N/A'}
- Father's Name: {case.father_name or 'N/A'}
- Accident Date: {case.accident_date or 'N/A'}
- Accident Place: {case.accident_place or 'N/A'}
- Vehicle No: {case.vehicle_no or 'N/A'}
- Hospital: {case.hospital or 'N/A'}
- FIR No: {case.fir_no or 'N/A'}
- Tribunal: {case.tribunal or 'N/A'}
- Claim Amount: {case.claim_amount_display}
- Injuries: {', '.join(case.injuries) if case.injuries else 'N/A'}
"""

        # Get draft-type-specific prompt
        type_prompt = DRAFT_PROMPTS.get(draft_type, "Generate a professional Indian legal document.")

        full_prompt = f"""
You are a SENIOR INDIAN MACT LAWYER with 20+ years of courtroom experience.

{type_prompt}

STRICT RULES:
- Use ONLY the case data provided below
- If any field is missing, write the appropriate blank (e.g., "____")
- Use Indian court drafting tone
- Write in formal legal language
- Do NOT add any commentary or explanations outside the document

{extra_notes and f'ADDITIONAL INSTRUCTIONS: {extra_notes}' or ''}

==================== CASE DATA ====================
{case_context}
===================================================

==================== CASE FILE TEXT ==============
{case_text[:6000] if case_text else 'Not provided'}
===================================================

Generate the complete {dict(Draft.DRAFT_TYPE_CHOICES).get(draft_type, 'document')} now:
"""

        ai_content = _ai_generate(full_prompt)

        # Generate ref number
        today   = date.today()
        ref_no  = f"{today.year}-{case.id}-{draft_type[:3]}"

        # Get next version number
        latest_version = (
            Draft.objects.filter(case=case, draft_type=draft_type)
            .order_by("-version")
            .values_list("version", flat=True)
            .first()
        ) or 0

        draft = Draft.objects.create(
            case         = case,
            title        = f"{dict(Draft.DRAFT_TYPE_CHOICES).get(draft_type)} — {case.title}",
            draft_type   = draft_type,
            content      = ai_content,
            version      = latest_version + 1,
            ai_generated = True,
            ai_prompt    = full_prompt[:500],
            ref_no       = ref_no,
        )

        return Response(
            DraftDetailSerializer(draft).data,
            status=status.HTTP_201_CREATED,
        )

    # ── GET /api/drafts/<id>/versions/ ────────────────────────────────────
    @action(detail=True, methods=["get"], url_path="versions")
    def versions(self, request, pk=None):
        """List all versions of a draft (same case + draft_type)."""
        draft = self.get_object()
        all_versions = (
            Draft.objects.filter(case=draft.case, draft_type=draft.draft_type)
            .order_by("-version")
        )
        return Response(DraftListSerializer(all_versions, many=True).data)
