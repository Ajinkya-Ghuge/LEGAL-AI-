"""
LegalAI — Django Web Views
Renders all HTML pages directly. No Flask. No middleman.
Browser → Django → DB → Template → Browser
"""

import os
import uuid
import logging
from datetime import datetime, date

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils.decorators import method_decorator
import json

from apps.cases.models import Case
from apps.documents.models import Document
from apps.documents.services import extract_pdf, extract_text_for_ai
from apps.timeline.models import TimelineEvent, MedicalSummary
from apps.drafts.models import Draft

logger = logging.getLogger(__name__)

# ── AI helper ─────────────────────────────────────────────────────────────────

def ai_generate(prompt: str, fallback: str = "AI unavailable.") -> str:
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        return model.generate_content(prompt).text
    except ImportError:
        return fallback
    except Exception as e:
        logger.exception("Gemini error")
        return f"AI Error: {e}"


def load_vault_text(max_chars: int = 6000) -> str:
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
                        doc = fitz.open(os.path.join(root, f))
                        text = "".join(p.get_text() for p in doc)[:2000]
                        knowledge += f"\n--- {f} ---\n{text}\n"
                    except Exception:
                        pass
    except ImportError:
        pass
    return knowledge[:max_chars]


def normalize_case(case: Case) -> dict:
    """Convert Case ORM object → template-friendly dict."""
    return {
        "id":             case.pk,
        "case_no":        case.case_no or f"Case #{case.pk}",
        "name":           case.title,
        "type":           case.get_case_type_display(),
        "status":         case.get_status_display(),
        "date":           str(case.accident_date) if case.accident_date else str(case.created_at.date()),
        "petitioner":     case.client_name,
        "father_name":    case.father_name,
        "age":            case.client_age,
        "occupation":     case.occupation,
        "address":        case.client_address,
        "accident_date":  str(case.accident_date) if case.accident_date else "N/A",
        "accident_place": case.accident_place or "N/A",
        "vehicle_no":     case.vehicle_no or "N/A",
        "hospital":       case.hospital or "N/A",
        "fir_no":         case.fir_no or "N/A",
        "tribunal":       case.tribunal or "N/A",
        "claim_amount":   case.claim_amount_display,
        "injuries":       case.injuries or [],
        "compensation":   case.compensation or [],
        "document_count": case.documents.count(),
        "draft_count":    case.drafts.count(),
        "timeline_count": case.timeline_events.count(),
    }


def normalize_event(event: TimelineEvent) -> dict:
    return {
        "id":          event.pk,
        "date":        str(event.date),
        "facility":    event.title,
        "doctor":      event.doctor,
        "type":        event.get_tag_display(),
        "tag":         event.tag,
        "description": event.description,
        "medications": event.medications or [],
    }


def normalize_draft(draft: Draft) -> dict:
    # Render content as proper HTML preview
    content = draft.content or ""
    # If content looks like plain text (no HTML tags), wrap in pre for display
    if content and "<" not in content[:100]:
        preview_html = f"<pre style='white-space:pre-wrap;font-family:serif;font-size:12px;line-height:1.8;'>{content}</pre>"
    else:
        preview_html = content  # already HTML from editor

    return {
        "id":             draft.pk,
        "ref_no":         draft.ref_no or "N/A",
        "title":          draft.title,
        "draft_type":     draft.draft_type.lower(),
        "version":        draft.version,
        "status":         draft.status,
        "ai_generated":   draft.ai_generated,
        "preview_html":   preview_html,
        "editor_content": content,
        "created_at":     str(draft.created_at.date()),
    }


# ── VIEWS ─────────────────────────────────────────────────────────────────────

def index(request):
    return redirect("dashboard")


def dashboard(request):
    recent_cases = [normalize_case(c) for c in Case.objects.order_by("-created_at")[:3]]

    total   = Case.objects.count()
    stats   = {
        "total":     total,
        "by_status": {
            "active":  Case.objects.filter(status="ACTIVE").count(),
            "pending": Case.objects.filter(status="PENDING").count(),
            "closed":  Case.objects.filter(status="CLOSED").count(),
        }
    }
    return render(request, "dashboard.html", {
        "recent_cases": recent_cases,
        "stats":        stats,
    })


def cases_list(request):
    qs = Case.objects.all().order_by("-created_at")

    status_filter = request.GET.get("status", "")
    type_filter   = request.GET.get("case_type", "")
    search        = request.GET.get("search", "")

    if status_filter:
        qs = qs.filter(status=status_filter.upper())
    if type_filter:
        qs = qs.filter(case_type=type_filter.upper())
    if search:
        qs = qs.filter(title__icontains=search) | qs.filter(client_name__icontains=search) | qs.filter(case_no__icontains=search)

    cases = [normalize_case(c) for c in qs]
    stats = {
        "total":     Case.objects.count(),
        "by_status": {
            "active":  Case.objects.filter(status="ACTIVE").count(),
            "pending": Case.objects.filter(status="PENDING").count(),
            "closed":  Case.objects.filter(status="CLOSED").count(),
        }
    }
    return render(request, "cases_list.html", {"cases": cases, "stats": stats})


def new_case(request):
    if request.method != "POST":
        return redirect("cases_list")

    # Map form → model
    type_map = {
        "MACT": "MACT", "Property Dispute": "PROPERTY",
        "Criminal": "CRIMINAL", "Civil": "CIVIL",
        "Consumer": "CONSUMER", "Labour": "LABOUR", "Family": "FAMILY",
    }
    status_map = {"Active": "ACTIVE", "Pending": "PENDING", "Closed": "CLOSED"}

    raw_amount = request.POST.get("claim_amount", "").replace("₹", "").replace(",", "").strip()
    try:
        claim_amount = float(raw_amount) if raw_amount else None
    except ValueError:
        claim_amount = None

    raw_date = request.POST.get("accident_date", "").strip()
    accident_date = raw_date if raw_date else None

    case = Case.objects.create(
        title         = request.POST.get("name", "New Case"),
        case_type     = type_map.get(request.POST.get("type", "MACT"), "MACT"),
        status        = status_map.get(request.POST.get("status", "Active"), "ACTIVE"),
        client_name   = request.POST.get("petitioner", ""),
        accident_date = accident_date,
        claim_amount  = claim_amount,
        injuries      = [],
        compensation  = [],
    )

    # Handle optional PDF upload
    if "case_pdf" in request.FILES:
        pdf_file = request.FILES["case_pdf"]
        doc = Document.objects.create(
            case          = case,
            file          = pdf_file,
            original_name = pdf_file.name,
            doc_type      = Document.DOC_TYPE_CASE_FILE,
        )
        result = extract_pdf(doc.file.path)
        if result["success"]:
            doc.pages             = result["pages"]
            doc.extracted_text    = result["full_text"]   # capped at 500K chars
            doc.page_texts        = result["page_texts"]  # first 200 pages
            doc.processing_status = Document.PROCESSING_DONE
            logger.info("Uploaded %d page PDF for case %d", result["pages"], case.pk)
        else:
            doc.processing_status = Document.PROCESSING_FAILED
            doc.processing_error  = result["error"]
        doc.save()
    return redirect("case_workspace", case_id=case.pk)


def case_workspace(request, case_id):
    case_obj = get_object_or_404(Case, pk=case_id)
    case     = normalize_case(case_obj)
    active_tab = request.GET.get("tab", "summary")

    documents = list(case_obj.documents.order_by("-uploaded_at").values(
        "id", "original_name", "doc_type", "pages", "processing_status", "uploaded_at"
    ))
    drafts = [normalize_draft(d) for d in case_obj.drafts.order_by("-version")[:10]]

    # Chat history from session
    chat_history = request.session.get(f"chat_{case_id}", [])

    return render(request, "case_workspace.html", {
        "case":        case,
        "active_tab":  active_tab,
        "documents":   documents,
        "drafts":      drafts,
        "chat_history": chat_history,
    })


def timeline(request):
    case_id        = request.GET.get("case_id", "")
    active_section = request.GET.get("section", "visits")

    qs = TimelineEvent.objects.select_related("case").order_by("date", "order")
    if case_id:
        qs = qs.filter(case_id=case_id)

    events    = [normalize_event(e) for e in qs]
    all_cases = [normalize_case(c) for c in Case.objects.order_by("-created_at")]

    return render(request, "timeline.html", {
        "timeline":          events,
        "active_section":    active_section,
        "all_cases":         all_cases,
        "selected_case_id":  case_id,
    })


def draft_editor(request):
    draft_id   = request.GET.get("draft_id")
    draft_type = request.GET.get("type", "claim_petition")
    case_id    = request.GET.get("case_id", "")

    draft = None

    if draft_id:
        try:
            draft = normalize_draft(Draft.objects.get(pk=draft_id))
        except Draft.DoesNotExist:
            pass

    if not draft and case_id:
        type_map = {
            "claim_petition": "CLAIM_PETITION",
            "legal_notice":   "LEGAL_NOTICE",
            "affidavit":      "AFFIDAVIT",
            "compensation":   "COMPENSATION",
            "written_args":   "WRITTEN_ARGS",
        }
        qs = Draft.objects.filter(
            case_id=case_id,
            draft_type=type_map.get(draft_type, "CLAIM_PETITION")
        ).order_by("-version")
        if qs.exists():
            draft = normalize_draft(qs.first())

    if not draft:
        draft = {
            "id":             None,
            "ref_no":         "NEW",
            "title":          "New Draft",
            "draft_type":     draft_type,
            "version":        1,
            "status":         "DRAFT",
            "ai_generated":   False,
            "preview_html":   "<p class='text-gray-400 text-sm italic'>No content yet. Click AI Generate to create a draft.</p>",
            "editor_content": "",
        }

    all_cases = [normalize_case(c) for c in Case.objects.order_by("-created_at")]

    return render(request, "draft_editor.html", {
        "draft":            draft,
        "active_draft":     draft_type,
        "all_cases":        all_cases,
        "selected_case_id": case_id,
    })


def medical_analysis(request):
    result   = None
    error    = None
    summary  = None
    case_id  = request.GET.get("case_id", "") or request.POST.get("case_id_hidden", "")

    # Load existing summary if case_id given
    if case_id and request.method == "GET":
        try:
            summary = MedicalSummary.objects.get(case_id=case_id)
        except MedicalSummary.DoesNotExist:
            pass

    if request.method == "POST":
        case_text = ""
        case_id   = request.POST.get("case_id_hidden", "")

        # Handle PDF upload
        if "case_pdf" in request.FILES:
            pdf_file = request.FILES["case_pdf"]
            upload_dir = os.path.join(settings.BASE_DIR.parent, "output")
            os.makedirs(upload_dir, exist_ok=True)
            tmp_path = os.path.join(upload_dir, f"tmp_{uuid.uuid4().hex[:8]}.pdf")

            with open(tmp_path, "wb") as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)

            result_pdf = extract_pdf(tmp_path)
            if result_pdf["success"]:
                # Use smart_text for AI (relevant pages, not just first N chars)
                case_text = result_pdf.get("smart_text") or result_pdf["full_text"][:50000]

                # Save document to DB if case_id provided
                if case_id:
                    try:
                        case_obj = Case.objects.get(pk=case_id)
                        pdf_file.seek(0)
                        doc = Document.objects.create(
                            case           = case_obj,
                            file           = pdf_file,
                            original_name  = pdf_file.name,
                            doc_type       = Document.DOC_TYPE_CASE_FILE,
                            pages          = result_pdf["pages"],
                            extracted_text = result_pdf["full_text"],   # full stored
                            page_texts     = result_pdf["page_texts"],
                            processing_status = Document.PROCESSING_DONE,
                        )
                        logger.info(
                            "Saved %d page PDF for case %d, smart_text=%d chars",
                            result_pdf["pages"], case_obj.pk, len(case_text)
                        )
                    except Case.DoesNotExist:
                        pass

            try:
                os.remove(tmp_path)
            except Exception:
                pass

        if not case_text:
            case_text = request.POST.get("case_text", "").strip()

        if not case_text:
            error = "Please upload a PDF or provide case text."
        else:
            vault_text = load_vault_text()
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
            result = ai_generate(prompt)

            # Save to DB if case_id provided
            if case_id and result:
                try:
                    case_obj = Case.objects.get(pk=case_id)
                    summary, _ = MedicalSummary.objects.update_or_create(
                        case=case_obj,
                        defaults={
                            "notes":         result,
                            "ai_raw_output": result,
                            "injuries":      case_obj.injuries or [],
                        }
                    )
                except Case.DoesNotExist:
                    pass

    all_cases = [normalize_case(c) for c in Case.objects.order_by("-created_at")]

    return render(request, "medical_analysis.html", {
        "result":           result,
        "error":            error,
        "summary":          summary,
        "all_cases":        all_cases,
        "selected_case_id": case_id,
    })


def ask_question(request):
    if request.method != "POST":
        return redirect("dashboard")

    question = request.POST.get("question", "").strip()
    if not question:
        return redirect("dashboard")

    vault_text = load_vault_text(4000)
    answer = ai_generate(f"""
You are a senior Indian legal AI assistant.
Answer this legal question concisely and professionally.
Cite relevant Indian law sections where applicable.

VAULT CONTEXT:
{vault_text}

QUESTION: {question}
""", fallback="AI unavailable. Install google-generativeai.")

    return render(request, "ask_result.html", {
        "question": question,
        "answer":   answer,
    })


# ── AJAX / API VIEWS ──────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def api_chat(request):
    try:
        body    = json.loads(request.body)
    except Exception:
        body    = {}

    message = body.get("message", "")
    case_id = body.get("case_id", "")

    case_context = ""
    if case_id:
        try:
            c = Case.objects.get(pk=case_id)
            case_context = (
                "CASE CONTEXT:\n"
                f"Case: {c.case_no} — {c.title}\n"
                f"Petitioner: {c.client_name}, Age: {c.client_age}\n"
                f"Accident: {c.accident_date} at {c.accident_place}\n"
                f"Injuries: {', '.join(c.injuries or [])}\n"
                f"Claim: {c.claim_amount_display}"
            )
        except Case.DoesNotExist:
            pass

    reply = ai_generate(f"""
You are LegalAI, a senior Indian legal assistant specializing in MACT and Indian law.
Be concise, professional, and helpful. Answer in 2-4 sentences max.

{case_context}

USER: {message}
""", fallback="AI unavailable. Install google-generativeai.")

    # Persist to session
    if case_id:
        key     = f"chat_{case_id}"
        history = request.session.get(key, [])
        now     = datetime.now().strftime("%I:%M %p")
        history.append({"role": "user", "content": message, "time": now})
        history.append({"role": "ai",   "content": reply,   "time": now})
        request.session[key] = history[-20:]
        request.session.modified = True

    return JsonResponse({"reply": reply})


@csrf_exempt
@require_http_methods(["POST"])
def api_save_draft(request):
    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    title    = body.get("title", "Untitled")
    content  = body.get("content", "")
    draft_id = body.get("draft_id")

    if draft_id:
        try:
            draft = Draft.objects.get(pk=draft_id)
            if body.get("new_version"):
                draft = draft.save_new_version(content)
                if title:
                    draft.title = title
                    draft.save()
            else:
                draft.content = content
                if title:
                    draft.title = title
                draft.save()
            return JsonResponse({"status": "saved", "draft_id": draft.pk, "version": draft.version})
        except Draft.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Draft not found"}, status=404)

    # No draft_id — save to output folder as fallback
    output_dir = os.path.join(settings.BASE_DIR.parent, "output")
    os.makedirs(output_dir, exist_ok=True)
    filename = f"draft_{datetime.now().strftime('%d%m_%H%M')}.html"
    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        f.write(f"<h1>{title}</h1>\n{content}")

    return JsonResponse({"status": "saved", "file": filename})


@csrf_exempt
@require_http_methods(["POST"])
def api_generate_draft(request):
    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    case_id    = body.get("case_id")
    draft_type = body.get("draft_type", "CLAIM_PETITION").upper()
    extra      = body.get("extra_notes", "")

    if not case_id:
        return JsonResponse({"error": "case_id required"}, status=400)

    try:
        case = Case.objects.get(pk=case_id)
    except Case.DoesNotExist:
        return JsonResponse({"error": f"Case {case_id} not found"}, status=404)

    # Build case context
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

    # Get latest document text
    case_text = ""
    latest_doc = case.documents.filter(
        processing_status=Document.PROCESSING_DONE
    ).order_by("-uploaded_at").first()
    if latest_doc:
        case_text = latest_doc.extracted_text[:6000]

    type_labels = {
        "CLAIM_PETITION": "MACT Claim Petition under Section 166 of the Motor Vehicles Act, 1988",
        "LEGAL_NOTICE":   "Legal Notice to Insurance Company and Vehicle Owner",
        "AFFIDAVIT":      "Affidavit of the Claimant",
        "COMPENSATION":   "Statement of Compensation",
        "WRITTEN_ARGS":   "Written Arguments on Compensation",
    }

    prompt = f"""
You are a SENIOR INDIAN MACT LAWYER with 20+ years of courtroom experience.

Generate a PROFESSIONAL COURT-READY {type_labels.get(draft_type, 'Legal Document')}.

STRICT RULES:
- Use ONLY the case data provided
- If any field is missing, write the appropriate blank (e.g., "____")
- Use Indian court drafting tone
- Write in formal legal language
- Do NOT add commentary outside the document

{f'ADDITIONAL INSTRUCTIONS: {extra}' if extra else ''}

==================== CASE DATA ====================
{case_context}
===================================================

==================== CASE FILE TEXT ==============
{case_text if case_text else 'Not provided'}
===================================================

Generate the complete document now:
"""

    content = ai_generate(prompt)

    # Get next version
    latest_version = Draft.objects.filter(
        case=case, draft_type=draft_type
    ).order_by("-version").values_list("version", flat=True).first() or 0

    today  = date.today()
    ref_no = f"{today.year}-{case.pk}-{draft_type[:3]}"

    draft = Draft.objects.create(
        case         = case,
        title        = f"{dict(Draft.DRAFT_TYPE_CHOICES).get(draft_type, draft_type)} — {case.title}",
        draft_type   = draft_type,
        content      = content,
        version      = latest_version + 1,
        ai_generated = True,
        ai_prompt    = prompt[:500],
        ref_no       = ref_no,
    )

    return JsonResponse({
        "draft_id": draft.pk,
        "content":  content,
        "title":    draft.title,
        "ref_no":   ref_no,
        "version":  draft.version,
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_upload_document(request):
    case_id  = request.POST.get("case_id")
    doc_type = request.POST.get("doc_type", Document.DOC_TYPE_CASE_FILE)

    if not case_id:
        return JsonResponse({"error": "case_id required"}, status=400)
    if "file" not in request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)

    try:
        case = Case.objects.get(pk=case_id)
    except Case.DoesNotExist:
        return JsonResponse({"error": "Case not found"}, status=404)

    pdf_file = request.FILES["file"]
    doc = Document.objects.create(
        case          = case,
        file          = pdf_file,
        original_name = pdf_file.name,
        doc_type      = doc_type,
    )

    if pdf_file.name.lower().endswith(".pdf"):
        result = extract_pdf(doc.file.path)
        if result["success"]:
            doc.pages             = result["pages"]
            doc.extracted_text    = result["full_text"]
            doc.page_texts        = result["page_texts"]
            doc.processing_status = Document.PROCESSING_DONE
        else:
            doc.processing_status = Document.PROCESSING_FAILED
            doc.processing_error  = result["error"]
        doc.save()

    return JsonResponse({
        "id":               doc.pk,
        "original_name":    doc.original_name,
        "pages":            doc.pages,
        "processing_status": doc.processing_status,
        "extracted_text":   doc.extracted_text[:500] + "..." if doc.extracted_text else "",
    })


def error_404(request, exception=None):
    return render(request, "error.html", {"message": "Page not found"}, status=404)


def error_500(request):
    return render(request, "error.html", {"message": "Server error"}, status=500)


# ── COMPENSATION PAGE ─────────────────────────────────────────────────────────

def compensation(request):
    all_cases = [normalize_case(c) for c in Case.objects.order_by("-created_at")]
    result = None
    error = None

    multiplier_table = [
        ("15–20", 16), ("20–25", 18), ("25–30", 17), ("30–35", 16),
        ("35–40", 15), ("40–45", 14), ("45–50", 13), ("50–55", 11),
        ("55–60", 9),  ("60–65", 7),  ("65+", 5),
    ]

    if request.method == "POST":
        case_id = request.POST.get("case_id", "")
        # Manual inputs
        age             = request.POST.get("age", "")
        monthly_income  = request.POST.get("monthly_income", "")
        disability_pct  = request.POST.get("disability_pct", "")
        medical_bills   = request.POST.get("medical_bills", "")
        treatment_years = request.POST.get("treatment_years", "")
        injury_type     = request.POST.get("injury_type", "")

        prompt = f"""
You are a SENIOR INDIAN MACT ADVOCATE and compensation calculation expert.

Calculate detailed compensation for this motor accident case using Indian Supreme Court formulas.

CASE DETAILS:
- Age of victim: {age or 'NOT PROVIDED'}
- Monthly income: ₹{monthly_income or 'NOT PROVIDED'}
- Disability percentage: {disability_pct or 'NOT PROVIDED'}%
- Medical bills incurred: ₹{medical_bills or 'NOT PROVIDED'}
- Expected treatment years: {treatment_years or 'NOT PROVIDED'}
- Injury type: {injury_type or 'NOT PROVIDED'}

CALCULATE ALL HEADS:

1. MEDICAL EXPENSES
   - Actual bills: ₹{medical_bills or 0}
   - Future medical expenses (estimate)

2. LOSS OF INCOME
   - Using Sarla Verma formula (multiplier method)
   - Monthly income × 12 × multiplier (based on age)
   - Show multiplier used

3. PAIN & SUFFERING
   - General damages estimate

4. DISABILITY COMPENSATION
   - Permanent disability calculation
   - Loss of earning capacity

5. LOSS OF AMENITIES
   - Standard estimate

6. ATTENDANT CHARGES & CONVEYANCE
   - Standard estimate

7. TOTAL COMPENSATION
   - Sum of all heads
   - With interest @ 9% p.a. from date of accident

ALSO CITE:
- Sarla Verma vs DTC (2009) — multiplier table
- National Insurance vs Pranay Sethi (2017) — conventional heads
- Applicable multiplier for age {age or 'unknown'}

Format as a professional compensation statement.
"""
        result = ai_generate(prompt)

        # If case_id given, save to case compensation
        if case_id and result:
            try:
                case_obj = Case.objects.get(pk=case_id)
                MedicalSummary.objects.update_or_create(
                    case=case_obj,
                    defaults={"notes": result, "ai_raw_output": result}
                )
            except Case.DoesNotExist:
                pass

    return render(request, "compensation.html", {
        "all_cases":        all_cases,
        "result":           result,
        "error":            error,
        "multiplier_table": multiplier_table,
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_compensation_calculate(request):
    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    age            = body.get("age", 30)
    monthly_income = body.get("monthly_income", 0)
    disability_pct = body.get("disability_pct", 0)
    medical_bills  = body.get("medical_bills", 0)

    # Sarla Verma multiplier table
    multiplier_table = {
        (0, 15): 15, (15, 20): 16, (20, 25): 18, (25, 30): 17,
        (30, 35): 16, (35, 40): 15, (40, 45): 14, (45, 50): 13,
        (50, 55): 11, (55, 60): 9, (60, 65): 7, (65, 200): 5
    }
    multiplier = 10
    for (low, high), m in multiplier_table.items():
        if low <= int(age) < high:
            multiplier = m
            break

    try:
        income       = float(monthly_income)
        disability   = float(disability_pct) / 100
        bills        = float(medical_bills)
        annual       = income * 12
        loss_earning = annual * multiplier * disability
        pain         = min(max(bills * 0.5, 50000), 500000)
        amenities    = 50000
        attendant    = 36000
        total        = bills + loss_earning + pain + amenities + attendant
    except Exception:
        return JsonResponse({"error": "Invalid numbers"}, status=400)

    return JsonResponse({
        "multiplier":     multiplier,
        "medical_bills":  bills,
        "loss_earning":   round(loss_earning, 2),
        "pain_suffering": round(pain, 2),
        "amenities":      amenities,
        "attendant":      attendant,
        "total":          round(total, 2),
        "with_interest":  round(total * 1.09, 2),
    })


# ── CASE SUB-PAGES (sidebar nav) ─────────────────────────────────────────────

def _case_base(request, case_id):
    """Helper — returns normalized case dict or 404."""
    case_obj = get_object_or_404(Case, pk=case_id)
    return case_obj, normalize_case(case_obj)


def case_injuries(request, case_id):
    case_obj, case = _case_base(request, case_id)
    # Try to get medical summary
    try:
        summary = case_obj.medical_summary
    except Exception:
        summary = None
    return render(request, "case_injuries.html", {
        "case":       case,
        "active_tab": "injuries",
        "summary":    summary,
    })


def case_treatment(request, case_id):
    case_obj, case = _case_base(request, case_id)
    try:
        summary = case_obj.medical_summary
    except Exception:
        summary = None
    return render(request, "case_treatment.html", {
        "case":       case,
        "active_tab": "treatment",
        "summary":    summary,
    })


def case_expenses(request, case_id):
    case_obj, case = _case_base(request, case_id)
    documents = list(case_obj.documents.order_by("-uploaded_at").values(
        "id", "original_name", "doc_type", "pages", "processing_status", "uploaded_at"
    ))
    return render(request, "case_expenses.html", {
        "case":       case,
        "active_tab": "expenses",
        "documents":  documents,
    })


def case_compensation(request, case_id):
    case_obj, case = _case_base(request, case_id)
    return render(request, "case_compensation.html", {
        "case":       case,
        "active_tab": "compensation",
    })


def case_reports(request, case_id):
    case_obj, case = _case_base(request, case_id)
    try:
        summary = case_obj.medical_summary
    except Exception:
        summary = None
    return render(request, "case_reports.html", {
        "case":       case,
        "active_tab": "reports",
        "summary":    summary,
    })


def case_drafts(request, case_id):
    case_obj, case = _case_base(request, case_id)
    drafts = [normalize_draft(d) for d in case_obj.drafts.order_by("-version")]
    return render(request, "case_drafts.html", {
        "case":       case,
        "active_tab": "drafts",
        "drafts":     drafts,
    })
