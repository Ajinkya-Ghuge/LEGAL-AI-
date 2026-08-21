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
    """
    Generate content via Gemini API.
    Tries gemini-2.5-flash first, falls back to gemini-1.5-flash, then gemini-pro.
    Returns None (not a string) on error so callers can distinguish failure from empty output.
    """
    try:
        import google.generativeai as genai
    except ImportError:
        logger.error("google-generativeai not installed")
        return None

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        logger.error("GEMINI_API_KEY not set")
        return None

    # Model preference order — try lighter quota models first
    models_to_try = [
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash",
        "gemini-flash-lite-latest",
        "gemini-2.5-flash",
        "gemini-pro-latest",
    ]

    genai.configure(api_key=api_key)

    last_error = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = response.text
            if text:
                logger.info("ai_generate: success with %s (%d chars)", model_name, len(text))
                return text
        except Exception as e:
            err_str = str(e)
            last_error = err_str
            # Quota/rate-limit — try next model
            if "429" in err_str or "quota" in err_str.lower() or "rate" in err_str.lower():
                logger.warning("Gemini quota hit on %s, trying next model...", model_name)
                continue
            # Key leaked or invalid — no point retrying other models with same key
            if "leaked" in err_str.lower() or "403" in err_str or "API_KEY_INVALID" in err_str:
                logger.error("Gemini API key error: %s", err_str[:200])
                break
            # Other error — log and try next
            logger.warning("Gemini error on %s: %s", model_name, err_str[:200])
            continue

    logger.error("All Gemini models failed. Last error: %s", last_error)
    return None


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

    # Handle optional PDF upload + auto AI analysis
    if "case_pdf" in request.FILES:
        pdf_file = request.FILES["case_pdf"]
        try:
            doc = Document.objects.create(
                case          = case,
                file          = pdf_file,
                original_name = pdf_file.name,
                doc_type      = Document.DOC_TYPE_CASE_FILE,
            )
            result = extract_pdf(doc.file.path)
            if result["success"]:
                doc.pages             = result["pages"]
                doc.extracted_text    = result["full_text"]
                doc.page_texts        = result["page_texts"]
                doc.processing_status = Document.PROCESSING_DONE
                doc.save()
                logger.info("Uploaded %d page PDF for case %d", result["pages"], case.pk)

                # Auto-run AI analysis to populate all sections
                smart_text = result.get("smart_text") or result["full_text"][:50000]
                _auto_analyze_case(case, smart_text)
            else:
                doc.processing_status = Document.PROCESSING_FAILED
                doc.processing_error  = result.get("error", "Unknown error")
                doc.save()
                logger.error("PDF extraction failed: %s", result.get("error"))
        except Exception as e:
            logger.exception("PDF upload failed for case %d: %s", case.pk, str(e))
    return redirect("case_workspace", case_id=case.pk)


def _auto_analyze_case(case: Case, case_text: str):
    """
    Run AI analysis on uploaded PDF text and populate:
    - Case injuries list
    - Medical timeline events
    - Medical summary (injuries, treatments, notes)
    Called automatically after PDF upload.
    """
    import json as _json

    vault_text = load_vault_text(3000)

    prompt = f"""
You are a SENIOR INDIAN MACT ADVOCATE analyzing a medical case file.

Extract structured data from this case. Return ONLY valid JSON, no other text.

Return this exact JSON structure:
{{
  "injuries": ["injury 1", "injury 2"],
  "timeline": [
    {{
      "date": "YYYY-MM-DD",
      "facility": "Hospital/Clinic name",
      "doctor": "Dr. Name",
      "type": "EMERGENCY",
      "description": "What happened",
      "medications": ["med1", "med2"]
    }}
  ],
  "treatments": [
    {{"type": "Surgery", "detail": "ORIF procedure"}}
  ],
  "medications": ["Gabapentin 300mg", "Medrol"],
  "missing_docs": ["FIR copy", "Disability certificate"],
  "case_strength": "Strong",
  "legal_strategy": "Brief strategy note",
  "summary_notes": "Full professional medical-legal summary in 3-4 paragraphs"
}}

RULES:
- date format must be YYYY-MM-DD (use 2024-01-01 if unknown)
- type must be one of: EMERGENCY, SPECIALIST, SURGERY, CHIROPRACTIC, FOLLOW_UP, DISCHARGE, PHYSIOTHERAPY, OTHER
- case_strength must be: Strong, Moderate, or Weak
- Return ONLY the JSON object, nothing else

CASE FILE:
{case_text[:8000]}

VAULT CONTEXT:
{vault_text}
"""

    try:
        raw = ai_generate(prompt, fallback="")
        if not raw:
            logger.warning("Auto-analysis: AI returned no content for case %d", case.pk)
            return

        # Clean up response — remove markdown code blocks if present
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip().rstrip("```").strip()

        data = _json.loads(raw)

        # 1. Update case injuries
        injuries = data.get("injuries", [])
        if injuries:
            case.injuries = injuries
            case.save(update_fields=["injuries"])

        # 2. Create timeline events
        timeline_items = data.get("timeline", [])
        for i, item in enumerate(timeline_items[:20]):  # max 20 events
            try:
                from datetime import datetime as _dt
                date_str = item.get("date", "2024-01-01")
                try:
                    event_date = _dt.strptime(date_str, "%Y-%m-%d").date()
                except Exception:
                    event_date = _dt.now().date()

                tag = item.get("type", "OTHER").upper()
                valid_tags = ["EMERGENCY", "SPECIALIST", "SURGERY", "CHIROPRACTIC",
                              "FOLLOW_UP", "DISCHARGE", "PHYSIOTHERAPY", "INVESTIGATION", "OTHER"]
                if tag not in valid_tags:
                    tag = "OTHER"

                TimelineEvent.objects.create(
                    case        = case,
                    date        = event_date,
                    title       = item.get("facility", "Medical Visit"),
                    doctor      = item.get("doctor", ""),
                    description = item.get("description", ""),
                    tag         = tag,
                    medications = item.get("medications", []),
                    order       = i,
                )
            except Exception as ev_err:
                logger.warning("Failed to create timeline event: %s", ev_err)

        # 3. Create/update medical summary
        summary_notes = data.get("summary_notes", "")
        MedicalSummary.objects.update_or_create(
            case=case,
            defaults={
                "injuries":      injuries,
                "treatments":    data.get("treatments", []),
                "medications":   data.get("medications", []),
                "missing_docs":  data.get("missing_docs", []),
                "case_strength": data.get("case_strength", ""),
                "legal_strategy": data.get("legal_strategy", ""),
                "notes":         summary_notes,
                "ai_raw_output": raw,
            }
        )

        logger.info("Auto-analysis complete for case %d: %d injuries, %d timeline events",
                    case.pk, len(injuries), len(timeline_items))

    except _json.JSONDecodeError as je:
        logger.error("AI returned invalid JSON for case %d: %s", case.pk, str(je))
        # Fallback: save raw text as notes only
        try:
            MedicalSummary.objects.update_or_create(
                case=case,
                defaults={"notes": raw, "ai_raw_output": raw}
            )
        except Exception:
            pass
    except Exception as e:
        logger.exception("Auto-analysis failed for case %d: %s", case.pk, str(e))


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

    # Check API key is configured
    if not settings.GEMINI_API_KEY:
        error = (
            "Gemini API key is not configured. "
            "Please add your API key to backend/legalai/settings.py (GEMINI_API_KEY) "
            "or set the GEMINI_API_KEY environment variable. "
            "Get a free key at: https://aistudio.google.com/app/apikey"
        )

    # Load existing summary if case_id given
    if case_id and request.method == "GET":
        try:
            summary = MedicalSummary.objects.get(case_id=case_id)
        except MedicalSummary.DoesNotExist:
            pass

    if request.method == "POST" and not error:
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
            else:
                # PDF extraction failed — set an error so user sees it
                error = f"Could not extract text from the uploaded PDF. Error: {result_pdf.get('error', 'Unknown error')}. Please ensure the PDF is not password-protected and is a valid PDF file."
                logger.error("PDF extraction failed in medical_analysis: %s", result_pdf.get('error'))

            try:
                os.remove(tmp_path)
            except Exception:
                pass

        if not case_text:
            case_text = request.POST.get("case_text", "").strip()

        if not case_text:
            error = "Please upload a PDF or provide case text."
        else:
            # Quick sanity check — if text is suspiciously short, warn but continue
            if len(case_text.strip()) < 50:
                error = "The uploaded PDF appears to have very little readable text. Please check the file and try again."
            else:
                pass  # continue below

        if not error and case_text:
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

            if not result:
                error = (
                    "AI analysis failed. This is usually caused by an API quota limit or "
                    "an invalid/expired API key. Please check your GEMINI_API_KEY and try again."
                )
                result = None
            else:
                # Save to DB if case_id provided
                if case_id:
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


def api_case_text(request):
    """Return extracted text from a case's most recent document."""
    case_id = request.GET.get("case_id")
    if not case_id:
        return JsonResponse({"text": "", "pages": 0, "doc_name": ""})
    try:
        case = Case.objects.get(pk=case_id)
        doc = case.documents.filter(
            processing_status=Document.PROCESSING_DONE
        ).order_by("-uploaded_at").first()
        if doc and doc.extracted_text:
            return JsonResponse({
                "text":     doc.extracted_text[:50000],
                "pages":    doc.pages,
                "doc_name": doc.original_name,
            })
        return JsonResponse({"text": "", "pages": 0, "doc_name": ""})
    except Case.DoesNotExist:
        return JsonResponse({"text": "", "pages": 0, "doc_name": ""})


@csrf_exempt
@require_http_methods(["POST"])
def api_analyze_case(request):
    """
    Trigger AI analysis on a case's uploaded documents.
    Called from the case workspace "Analyze" button.
    """
    try:
        body    = json.loads(request.body)
    except Exception:
        body    = {}

    case_id = body.get("case_id")
    if not case_id:
        return JsonResponse({"error": "case_id required"}, status=400)

    try:
        case = Case.objects.get(pk=case_id)
    except Case.DoesNotExist:
        return JsonResponse({"error": "Case not found"}, status=404)

    # Get latest document text
    doc = case.documents.filter(
        processing_status=Document.PROCESSING_DONE
    ).order_by("-uploaded_at").first()

    if not doc or not doc.extracted_text:
        return JsonResponse({"error": "No processed documents found. Upload a PDF first."}, status=400)

    case_text = doc.extracted_text[:50000]

    try:
        _auto_analyze_case(case, case_text)
        return JsonResponse({
            "success": True,
            "message": f"Analysis complete. Found {case.injuries|length if case.injuries else 0} injuries and {case.timeline_events.count()} timeline events.",
            "injuries": case.injuries or [],
            "timeline_count": case.timeline_events.count(),
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ── PRECEDENT FINDER ──────────────────────────────────────────────────────────

def precedent_finder(request):
    result      = None
    error       = None
    query       = ""
    all_cases   = [normalize_case(c) for c in Case.objects.order_by("-created_at")]

    if request.method == "POST":
        query       = request.POST.get("query", "").strip()
        case_id     = request.POST.get("case_id", "")
        injury_type = request.POST.get("injury_type", "")
        location    = request.POST.get("location", "")
        age         = request.POST.get("age", "")
        income      = request.POST.get("income", "")

        # Build context from case if selected
        case_context = ""
        if case_id:
            try:
                c = Case.objects.get(pk=case_id)
                case_context = f"""
Case: {c.title}
Injuries: {', '.join(c.injuries) if c.injuries else 'Not specified'}
Claim Amount: {c.claim_amount_display}
Location: {c.accident_place or 'Not specified'}
"""
            except Case.DoesNotExist:
                pass

        vault_text = load_vault_text(8000)

        search_query = query or f"{injury_type} injury {location} MACT compensation"

        prompt = f"""
You are a SENIOR INDIAN MACT ADVOCATE and legal researcher.

Find relevant Supreme Court and High Court precedents for this case.

CASE DETAILS:
{case_context if case_context else f"Injury: {injury_type}, Location: {location}, Age: {age}, Income: ₹{income}/month"}

SEARCH QUERY: {search_query}

Using the legal vault and your knowledge of Indian case law, provide:

1. TOP 5 RELEVANT PRECEDENTS
   For each case cite:
   - Case name and citation (e.g., Sarla Verma vs DTC, (2009) 6 SCC 121)
   - Court and year
   - Key facts (injury type, victim age, income)
   - Compensation awarded
   - Why it's relevant to this case

2. COMPENSATION RANGE ANALYSIS
   Based on similar cases:
   - Minimum compensation awarded: ₹X
   - Maximum compensation awarded: ₹X
   - Typical/median: ₹X
   - Recommended claim for this case: ₹X

3. KEY LEGAL PRINCIPLES
   - Which principles from these cases apply here
   - Which multiplier to use (Sarla Verma table)
   - Any recent changes in law that affect this case

4. STRATEGIC INSIGHT
   - Strongest precedent to cite in court
   - How to distinguish unfavorable precedents
   - Expected judicial approach in this jurisdiction

LEGAL VAULT (use these judgments):
{vault_text}

Provide specific citations. Do not make up case names.
"""
        result = ai_generate(prompt)
        if not result:
            error = "AI unavailable. Please try again."

    return render(request, "precedent_finder.html", {
        "result":     result,
        "error":      error,
        "query":      query,
        "all_cases":  all_cases,
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_precedent_search(request):
    """AJAX precedent search for inline use."""
    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    case_id = body.get("case_id")
    query   = body.get("query", "")

    case_context = ""
    if case_id:
        try:
            c = Case.objects.get(pk=case_id)
            case_context = f"Case: {c.title}, Injuries: {', '.join(c.injuries or [])}, Claim: {c.claim_amount_display}"
        except Case.DoesNotExist:
            pass

    vault_text = load_vault_text(5000)
    prompt = f"""
Find 3 most relevant Indian Supreme Court/High Court MACT precedents for:
{case_context or query}

For each: case name, citation, compensation awarded, why relevant.
Be concise. Use real citations only.

VAULT: {vault_text}
"""
    result = ai_generate(prompt, fallback="AI unavailable.")
    return JsonResponse({"result": result})


# ── MISSING DOCUMENTS CHECKER ─────────────────────────────────────────────────

def missing_docs(request):
    all_cases = [normalize_case(c) for c in Case.objects.order_by("-created_at")]
    selected_case = None
    doc_checklist = None
    case_id = request.GET.get("case_id", "") or request.POST.get("case_id", "")

    if case_id:
        try:
            case_obj = Case.objects.get(pk=case_id)
            selected_case = normalize_case(case_obj)

            # Get AI-identified missing docs from medical summary
            ai_missing = []
            try:
                summary = case_obj.medical_summary
                ai_missing = summary.missing_docs or []
            except Exception:
                pass

            # Standard MACT document checklist
            standard_docs = [
                {"id": "fir",         "name": "FIR / Police Report",           "category": "Police",    "required": True},
                {"id": "chargesheet", "name": "Charge Sheet",                  "category": "Police",    "required": False},
                {"id": "panchnama",   "name": "Spot Panchnama",                "category": "Police",    "required": True},
                {"id": "discharge",   "name": "Hospital Discharge Summary",    "category": "Medical",   "required": True},
                {"id": "bills",       "name": "All Hospital Bills & Receipts", "category": "Medical",   "required": True},
                {"id": "prescription","name": "Doctor Prescriptions",          "category": "Medical",   "required": True},
                {"id": "mlc",         "name": "MLC (Medico-Legal Certificate)","category": "Medical",   "required": True},
                {"id": "disability",  "name": "Disability Certificate",        "category": "Medical",   "required": False},
                {"id": "xray",        "name": "X-Ray / MRI / CT Scan Reports", "category": "Medical",   "required": False},
                {"id": "insurance",   "name": "Insurance Policy Copy",         "category": "Insurance", "required": True},
                {"id": "rc",          "name": "RC Book of Offending Vehicle",  "category": "Insurance", "required": True},
                {"id": "dl",          "name": "Driving Licence of Driver",     "category": "Insurance", "required": True},
                {"id": "income",      "name": "Income Proof (Salary Slip/ITR)","category": "Financial", "required": False},
                {"id": "id_proof",    "name": "Petitioner ID Proof (Aadhaar)", "category": "Identity",  "required": True},
                {"id": "photo",       "name": "Passport Size Photographs",     "category": "Identity",  "required": True},
                {"id": "affidavit",   "name": "Affidavit of Claimant",         "category": "Court",     "required": True},
                {"id": "vakalatnama", "name": "Vakalatnama",                   "category": "Court",     "required": True},
            ]

            # Load saved status from DB (stored in case description as JSON hack, or use session)
            saved_status = request.session.get(f"docs_status_{case_id}", {})

            # Mark AI-identified missing docs
            for doc in standard_docs:
                doc["status"] = saved_status.get(doc["id"], "pending")
                # If AI said it's missing, mark as missing if not already received
                for ai_doc in ai_missing:
                    if any(word in ai_doc.lower() for word in doc["name"].lower().split()):
                        if doc["status"] == "pending":
                            doc["status"] = "missing"

            doc_checklist = standard_docs

        except Case.DoesNotExist:
            pass

    return render(request, "missing_docs.html", {
        "all_cases":     all_cases,
        "selected_case": selected_case,
        "doc_checklist": doc_checklist,
        "case_id":       case_id,
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_missing_docs_update(request):
    """Update document status for a case."""
    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    case_id = body.get("case_id")
    doc_id  = body.get("doc_id")
    status  = body.get("status")  # "received", "missing", "pending", "not_applicable"

    if not all([case_id, doc_id, status]):
        return JsonResponse({"error": "case_id, doc_id, status required"}, status=400)

    valid_statuses = ["received", "missing", "pending", "not_applicable"]
    if status not in valid_statuses:
        return JsonResponse({"error": f"status must be one of {valid_statuses}"}, status=400)

    # Store in session (simple approach — no new DB model needed)
    key = f"docs_status_{case_id}"
    # We need to use a different approach since we can't access session in csrf_exempt easily
    # Return success and let frontend handle localStorage
    return JsonResponse({"success": True, "doc_id": doc_id, "status": status})
