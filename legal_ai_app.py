"""
LegalAI — Flask Frontend
All data comes from Django DRF backend (port 8000).
Flask only handles rendering + file uploads + AI chat.
"""

import os
import uuid
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, session

# ── Optional deps ─────────────────────────────────────────────────────────────
try:
    import fitz
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

try:
    import google.generativeai as genai
    import os
    from dotenv import load_dotenv
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
    gemini_model = None

# ── Config ────────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "legalai-secret-key-2024"

DJANGO_API   = "http://127.0.0.1:8000/api"
VAULT_PATH   = os.path.join(os.path.dirname(__file__), "vault")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Django API helpers ────────────────────────────────────────────────────────

def api_get(path, params=None):
    """GET from Django API. Returns (data, error)."""
    try:
        r = requests.get(f"{DJANGO_API}{path}", params=params, timeout=8)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Django backend is offline. Start it with: python backend/manage.py runserver 8000"
    except Exception as e:
        return None, str(e)

def api_post(path, json=None, files=None, data=None):
    """POST to Django API. Returns (data, error)."""
    try:
        r = requests.post(f"{DJANGO_API}{path}", json=json, files=files, data=data, timeout=30)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Django backend is offline."
    except requests.exceptions.HTTPError as e:
        try:
            return None, r.json()
        except Exception:
            return None, str(e)
    except Exception as e:
        return None, str(e)

def api_put(path, json=None):
    """PUT to Django API. Returns (data, error)."""
    try:
        r = requests.put(f"{DJANGO_API}{path}", json=json, timeout=15)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Django backend is offline."
    except Exception as e:
        return None, str(e)

def normalize_case(c):
    """Map Django Case model fields → template-friendly dict."""
    return {
        "id":             c.get("id"),
        "case_no":        c.get("case_no") or f"Case #{c.get('id')}",
        "name":           c.get("title", ""),
        "type":           c.get("case_type", ""),
        "status":         c.get("status", "").capitalize(),
        "date":           c.get("accident_date") or c.get("created_at", "")[:10],
        "petitioner":     c.get("client_name", ""),
        "father_name":    c.get("father_name", ""),
        "age":            c.get("client_age", ""),
        "occupation":     c.get("occupation", ""),
        "address":        c.get("client_address", ""),
        "accident_date":  c.get("accident_date") or "N/A",
        "accident_place": c.get("accident_place") or "N/A",
        "vehicle_no":     c.get("vehicle_no") or "N/A",
        "hospital":       c.get("hospital") or "N/A",
        "fir_no":         c.get("fir_no") or "N/A",
        "tribunal":       c.get("tribunal") or "N/A",
        "claim_amount":   c.get("claim_amount_display") or (
                              f"₹ {float(c['claim_amount']):,.0f}/-"
                              if c.get("claim_amount") else "N/A"
                          ),
        "injuries":       c.get("injuries") or [],
        "compensation":   c.get("compensation") or [],
        "document_count": c.get("document_count", 0),
        "draft_count":    c.get("draft_count", 0),
    }

def normalize_event(e):
    """Map Django TimelineEvent → template-friendly dict."""
    tag_map = {
        "EMERGENCY":     "Emergency",
        "SPECIALIST":    "Specialist Consult",
        "CHIROPRACTIC":  "Chiropractic",
        "SURGERY":       "Surgery",
        "FOLLOW_UP":     "Follow Up",
        "DISCHARGE":     "Discharge",
        "PHYSIOTHERAPY": "Physiotherapy",
        "INVESTIGATION": "Investigation",
        "OTHER":         "Other",
    }
    return {
        "id":          e.get("id"),
        "date":        e.get("date", ""),
        "facility":    e.get("title", ""),
        "doctor":      e.get("doctor", ""),
        "type":        tag_map.get(e.get("tag", ""), e.get("tag_display", "Other")),
        "description": e.get("description", ""),
        "medications": e.get("medications") or [],
    }

def normalize_draft(d):
    """Map Django Draft → template-friendly dict."""
    type_map = {
        "CLAIM_PETITION": "claim_petition",
        "LEGAL_NOTICE":   "legal_notice",
        "AFFIDAVIT":      "affidavit",
        "COMPENSATION":   "compensation",
        "WRITTEN_ARGS":   "written_args",
    }
    return {
        "id":             d.get("id"),
        "ref_no":         d.get("ref_no") or "N/A",
        "title":          d.get("title", "Untitled Draft"),
        "draft_type":     type_map.get(d.get("draft_type", ""), "other"),
        "version":        d.get("version", 1),
        "status":         d.get("status", "DRAFT"),
        "ai_generated":   d.get("ai_generated", False),
        "preview_html":   f"<pre style='white-space:pre-wrap;font-family:serif;font-size:12px;line-height:1.8'>{d.get('content','')}</pre>",
        "editor_content": d.get("content", ""),
        "created_at":     d.get("created_at", ""),
    }

def ai_generate(prompt, fallback="AI unavailable."):
    if not HAS_GEMINI:
        return fallback
    try:
        return gemini_model.generate_content(prompt).text
    except Exception as e:
        return f"AI Error: {e}"

def load_vault_text(max_chars=6000):
    if not HAS_FITZ or not os.path.exists(VAULT_PATH):
        return ""
    knowledge = ""
    for root, _, files in os.walk(VAULT_PATH):
        for f in files:
            if f.endswith(".pdf"):
                try:
                    doc = fitz.open(os.path.join(root, f))
                    text = "".join(p.get_text() for p in doc)[:2000]
                    knowledge += f"\n--- {f} ---\n{text}\n"
                except Exception:
                    pass
    return knowledge[:max_chars]

# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    data, err = api_get("/cases/", {"page_size": 3, "ordering": "-created_at"})
    if err or not data:
        recent = []
    else:
        results = data.get("results", data) if isinstance(data, dict) else data
        recent  = [normalize_case(c) for c in results[:3]]

    stats, _ = api_get("/cases/stats/")
    return render_template("dashboard.html",
                           recent_cases=recent,
                           stats=stats or {},
                           backend_error=err)


@app.route("/cases")
def cases_list():
    status_filter = request.args.get("status", "")
    type_filter   = request.args.get("case_type", "")
    search        = request.args.get("search", "")

    params = {"page_size": 50, "ordering": "-created_at"}
    if status_filter:
        params["status"] = status_filter
    if type_filter:
        params["case_type"] = type_filter
    if search:
        params["search"] = search

    data, err = api_get("/cases/", params)
    if err or not data:
        cases = []
    else:
        results = data.get("results", data) if isinstance(data, dict) else data
        cases   = [normalize_case(c) for c in results]

    stats, _ = api_get("/cases/stats/")
    return render_template("cases_list.html",
                           cases=cases,
                           stats=stats or {},
                           backend_error=err)


@app.route("/cases/new", methods=["POST"])
def new_case():
    # Map form → Django field names
    payload = {
        "title":          request.form.get("name", "New Case"),
        "case_type":      request.form.get("type", "MACT").upper().replace(" ", "_"),
        "status":         request.form.get("status", "ACTIVE").upper(),
        "client_name":    request.form.get("petitioner", ""),
        "accident_date":  request.form.get("accident_date") or None,
        "claim_amount":   request.form.get("claim_amount", "").replace("₹", "").replace(",", "").strip() or None,
        "injuries":       [],
        "compensation":   [],
    }
    data, err = api_post("/cases/", json=payload)
    if err or not data:
        return redirect(url_for("cases_list"))
    return redirect(url_for("case_workspace", case_id=data["id"]))


@app.route("/cases/<int:case_id>")
def case_workspace(case_id):
    data, err = api_get(f"/cases/{case_id}/summary/")
    if err or not data:
        return render_template("error.html", message=err or "Case not found"), 404

    case         = normalize_case(data)
    active_tab   = request.args.get("tab", "summary")
    chat_history = session.get(f"chat_{case_id}", [])

    # Load documents for this case
    docs_data, _ = api_get("/documents/", {"case_id": case_id})
    documents = []
    if docs_data:
        results = docs_data.get("results", docs_data) if isinstance(docs_data, dict) else docs_data
        documents = results

    # Load drafts for this case
    drafts_data, _ = api_get("/drafts/", {"case_id": case_id})
    drafts = []
    if drafts_data:
        results = drafts_data.get("results", drafts_data) if isinstance(drafts_data, dict) else drafts_data
        drafts = [normalize_draft(d) for d in results]

    return render_template("case_workspace.html",
                           case=case,
                           active_tab=active_tab,
                           chat_history=chat_history,
                           documents=documents,
                           drafts=drafts)


@app.route("/timeline")
def timeline():
    case_id        = request.args.get("case_id", "")
    active_section = request.args.get("section", "visits")

    params = {"ordering": "date"}
    if case_id:
        params["case_id"] = case_id

    data, err = api_get("/timeline/", params)
    events = []
    if data:
        results = data.get("results", data) if isinstance(data, dict) else data
        events  = [normalize_event(e) for e in results]

    # Load cases for selector
    cases_data, _ = api_get("/cases/", {"page_size": 50})
    all_cases = []
    if cases_data:
        results   = cases_data.get("results", cases_data) if isinstance(cases_data, dict) else cases_data
        all_cases = [normalize_case(c) for c in results]

    return render_template("timeline.html",
                           timeline=events,
                           active_section=active_section,
                           all_cases=all_cases,
                           selected_case_id=case_id,
                           backend_error=err)


@app.route("/draft-editor")
def draft_editor():
    draft_id   = request.args.get("draft_id")
    draft_type = request.args.get("type", "claim_petition")
    case_id    = request.args.get("case_id", "")

    draft = None

    # Load specific draft from Django
    if draft_id:
        data, _ = api_get(f"/drafts/{draft_id}/")
        if data:
            draft = normalize_draft(data)

    # Load latest draft of this type for this case
    if not draft and case_id:
        type_map_rev = {
            "claim_petition": "CLAIM_PETITION",
            "legal_notice":   "LEGAL_NOTICE",
            "affidavit":      "AFFIDAVIT",
            "compensation":   "COMPENSATION",
            "written_args":   "WRITTEN_ARGS",
        }
        params = {"case_id": case_id, "draft_type": type_map_rev.get(draft_type, "CLAIM_PETITION")}
        data, _ = api_get("/drafts/", params)
        if data:
            results = data.get("results", data) if isinstance(data, dict) else data
            if results:
                draft = normalize_draft(results[0])

    # Fallback placeholder
    if not draft:
        draft = {
            "id":             None,
            "ref_no":         "NEW",
            "title":          "New Draft",
            "draft_type":     draft_type,
            "version":        1,
            "status":         "DRAFT",
            "ai_generated":   False,
            "preview_html":   "<p class='text-gray-400 text-sm'>No content yet. Use AI Generate to create a draft.</p>",
            "editor_content": "",
        }

    # Load cases for the generate modal
    cases_data, _ = api_get("/cases/", {"page_size": 50})
    all_cases = []
    if cases_data:
        results   = cases_data.get("results", cases_data) if isinstance(cases_data, dict) else cases_data
        all_cases = [normalize_case(c) for c in results]

    return render_template("draft_editor.html",
                           draft=draft,
                           active_draft=draft_type,
                           all_cases=all_cases,
                           selected_case_id=case_id)


@app.route("/medical-analysis", methods=["GET", "POST"])
def medical_analysis():
    result    = None
    error     = None
    case_id   = request.args.get("case_id", "")
    summary   = None

    # Load existing summary from Django if case_id provided
    if case_id and request.method == "GET":
        s_data, _ = api_get(f"/timeline/summary/{case_id}/")
        if s_data:
            summary = s_data

    if request.method == "POST":
        case_text = ""
        pdf_path  = None

        # Handle PDF upload — send to Django for extraction
        if "case_pdf" in request.files and request.files["case_pdf"].filename:
            pdf_file = request.files["case_pdf"]
            pdf_path = os.path.join(UPLOAD_FOLDER, f"upload_{uuid.uuid4().hex[:8]}.pdf")
            pdf_file.save(pdf_path)

            # Try Django extraction first
            post_case_id = request.form.get("case_id_hidden") or case_id
            if post_case_id:
                with open(pdf_path, "rb") as f:
                    doc_data, doc_err = api_post(
                        "/documents/upload/",
                        files={"file": (pdf_file.filename, f, "application/pdf")},
                        data={"case_id": post_case_id, "doc_type": "CASE_FILE"}
                    )
                if doc_data:
                    case_text = doc_data.get("extracted_text", "")

            # Fallback: local PyMuPDF
            if not case_text and HAS_FITZ:
                try:
                    doc = fitz.open(pdf_path)
                    case_text = "".join(p.get_text() for p in doc)[:10000]
                except Exception:
                    pass

            try:
                os.remove(pdf_path)
            except Exception:
                pass

        if not case_text:
            case_text = request.form.get("case_text", "").strip()

        if not case_text:
            error = "Please upload a PDF or provide case text."
        else:
            # Try Django AI generation first
            post_case_id = request.form.get("case_id_hidden") or case_id
            if post_case_id:
                gen_data, gen_err = api_post(
                    "/timeline/summary/generate/",
                    json={"case_id": int(post_case_id), "case_text": case_text}
                )
                if gen_data and gen_data.get("success"):
                    result = gen_data["summary"].get("notes", "")
                    summary = gen_data["summary"]
                elif gen_err:
                    # Fallback to local Gemini
                    vault_text = load_vault_text()
                    result = ai_generate(f"""
You are a SENIOR INDIAN MACT ADVOCATE.
Generate a FULL professional MACT injury case report.

VAULT:
{vault_text}

CASE:
{case_text}
""")
            else:
                vault_text = load_vault_text()
                result = ai_generate(f"""
You are a SENIOR INDIAN MACT ADVOCATE.
Generate a FULL professional MACT injury case report.

VAULT:
{vault_text}

CASE:
{case_text}
""")

    # Load cases for selector
    cases_data, _ = api_get("/cases/", {"page_size": 50})
    all_cases = []
    if cases_data:
        results   = cases_data.get("results", cases_data) if isinstance(cases_data, dict) else cases_data
        all_cases = [normalize_case(c) for c in results]

    return render_template("medical_analysis.html",
                           result=result,
                           error=error,
                           summary=summary,
                           all_cases=all_cases,
                           selected_case_id=case_id)


@app.route("/ask", methods=["POST"])
def ask_question():
    question = request.form.get("question", "").strip()
    if not question:
        return redirect(url_for("dashboard"))

    vault_text = load_vault_text(4000)
    answer = ai_generate(f"""
You are a senior Indian legal AI assistant.
Answer this legal question concisely and professionally.
Cite relevant Indian law sections where applicable.

VAULT CONTEXT:
{vault_text}

QUESTION: {question}
""", fallback="AI unavailable. Install google-generativeai.")

    return render_template("ask_result.html", question=question, answer=answer)


# ── AJAX API ENDPOINTS ────────────────────────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
def api_chat():
    body    = request.get_json() or {}
    message = body.get("message", "")
    case_id = body.get("case_id", "")

    case_context = ""
    if case_id:
        c_data, _ = api_get(f"/cases/{case_id}/")
        if c_data:
            c = normalize_case(c_data)
            case_context = (
                f"Case: {c['case_no']} — {c['name']}\n"
                f"Petitioner: {c['petitioner']}, Age: {c['age']}\n"
                f"Accident: {c['accident_date']} at {c['accident_place']}\n"
                f"Injuries: {', '.join(c['injuries'])}\n"
                f"Claim: {c['claim_amount']}"
            )

    reply = ai_generate(f"""
You are LegalAI, a senior Indian legal assistant specializing in MACT and Indian law.
Be concise, professional, and helpful. Answer in 2-4 sentences max.

{('CASE CONTEXT:\n' + case_context) if case_context else ''}

USER: {message}
""", fallback="AI unavailable. Install google-generativeai.")

    # Persist to session
    if case_id:
        key     = f"chat_{case_id}"
        history = session.get(key, [])
        now     = datetime.now().strftime("%I:%M %p")
        history.append({"role": "user", "content": message, "time": now})
        history.append({"role": "ai",   "content": reply,   "time": now})
        session[key] = history[-20:]

    return jsonify({"reply": reply})


@app.route("/api/save-draft", methods=["POST"])
def api_save_draft():
    body     = request.get_json() or {}
    title    = body.get("title", "Untitled")
    content  = body.get("content", "")
    draft_id = body.get("draft_id")

    if draft_id:
        # Update existing draft in Django
        data, err = api_put(f"/drafts/{draft_id}/", json={
            "content":             content,
            "title":               title,
            "save_as_new_version": body.get("new_version", False),
        })
        if err:
            return jsonify({"status": "error", "message": str(err)}), 500
        return jsonify({"status": "saved", "draft": data})

    # No draft_id — save locally as fallback
    filename = f"draft_{datetime.now().strftime('%d%m_%H%M')}.html"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"<h1>{title}</h1>\n{content}")
    return jsonify({"status": "saved", "file": filename})


@app.route("/api/generate-draft", methods=["POST"])
def api_generate_draft():
    """AJAX endpoint — generate draft via Django, return content."""
    body       = request.get_json() or {}
    case_id    = body.get("case_id")
    draft_type = body.get("draft_type", "CLAIM_PETITION")
    extra      = body.get("extra_notes", "")

    if not case_id:
        return jsonify({"error": "case_id required"}), 400

    data, err = api_post("/drafts/generate/", json={
        "case_id":    case_id,
        "draft_type": draft_type,
        "extra_notes": extra,
    })

    if err:
        return jsonify({"error": str(err)}), 500

    return jsonify({
        "draft_id": data.get("id"),
        "content":  data.get("content", ""),
        "title":    data.get("title", ""),
        "ref_no":   data.get("ref_no", ""),
    })


@app.route("/api/upload-document", methods=["POST"])
def api_upload_document():
    """Upload a PDF to Django and get extracted text back."""
    case_id  = request.form.get("case_id")
    doc_type = request.form.get("doc_type", "CASE_FILE")

    if not case_id:
        return jsonify({"error": "case_id required"}), 400

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    f = request.files["file"]
    data, err = api_post(
        "/documents/upload/",
        files={"file": (f.filename, f.stream, f.content_type)},
        data={"case_id": case_id, "doc_type": doc_type}
    )

    if err:
        return jsonify({"error": str(err)}), 500

    return jsonify(data)


@app.route("/api/backend-status")
def backend_status():
    """Check if Django backend is alive."""
    data, err = api_get("/health/")
    if err:
        return jsonify({"online": False, "error": err}), 503
    return jsonify({"online": True, **data})


# ── ERROR PAGE ────────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", message="Page not found"), 404


# ── RUN ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 54)
    print("  🏛️  LegalAI Platform — Full Stack")
    print("=" * 54)
    print("  Flask Frontend  →  http://127.0.0.1:5000")
    print("  Django Backend  →  http://127.0.0.1:8000")
    print("  Django Admin    →  http://127.0.0.1:8000/admin/")
    print("=" * 54)
    print("  Make sure Django is running:")
    print("  python backend/manage.py runserver 8000")
    print("=" * 54 + "\n")
    app.run(debug=True, port=5000)
