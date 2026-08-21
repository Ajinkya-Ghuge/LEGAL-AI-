# 🏛️ LegalAI — Project Progress

> Indian Legal Case Management Platform with AI assistance
> Targeting MACT, Property, Consumer, Criminal cases

---

## ✅ Phase 1: AI Scripts (Original Python Tools)

| Script | Status | Description |
|--------|--------|-------------|
| `main.py` | ✅ Done | PDF extraction + Ollama/Phi3 legal analysis |
| `brain.py` | ✅ Done | Case analysis with Mistral via Ollama |
| `medical_v1.py` | ✅ Done | Full MACT medical report via Gemini |
| `ingest.py` | ✅ Done | Vault loader + Gemini analysis |
| `draft.py` | ✅ Done | AI draft generator + PDF export via fpdf |
| `verifier.py` | ✅ Done | MACT analysis via Ollama + vault RAG |
| `rag.py` | ✅ Done | FAISS vector search + LangChain RAG |
| `DRAFT GENERATOR/` | ✅ Done | ReportLab PDF drafts (claim petition, legal notice, affidavit, compensation) |

---

## ✅ Phase 2: Django Backend (REST API)

### Setup
- Django 6.0.4 + DRF 3.17.1 ✅
- SQLite database ✅
- CORS headers configured ✅
- Admin panel at `/admin/` (admin / admin123) ✅
- Seed data (3 demo cases, 8 timeline events) ✅

### Models
| Model | App | Status |
|-------|-----|--------|
| `Case` | cases | ✅ Done |
| `Document` | documents | ✅ Done |
| `TimelineEvent` | timeline | ✅ Done |
| `MedicalSummary` | timeline | ✅ Done |
| `Draft` | drafts | ✅ Done |

### REST API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/cases/` | List + create cases |
| GET/PUT/DELETE | `/api/cases/<id>/` | Case detail |
| GET | `/api/cases/stats/` | Dashboard stats |
| GET | `/api/cases/<id>/summary/` | Case with related counts |
| POST | `/api/documents/upload/` | Upload PDF + auto-extract text |
| POST | `/api/documents/process/` | Re-process document |
| GET | `/api/documents/?case_id=X` | List documents for case |
| GET | `/api/timeline/?case_id=X` | Timeline events for case |
| POST | `/api/timeline/` | Add timeline event |
| GET | `/api/timeline/summary/<case_id>/` | Get medical summary |
| POST | `/api/timeline/summary/generate/` | AI-generate medical summary |
| GET | `/api/drafts/?case_id=X` | List drafts for case |
| POST | `/api/drafts/generate/` | AI-generate legal draft |
| PUT | `/api/drafts/<id>/` | Save/update draft |
| GET | `/api/drafts/<id>/versions/` | All versions of a draft |
| GET | `/api/health/` | System health check |

---

## ✅ Phase 3: Web Frontend (Django Templates)

### Architecture
```
Browser → Django (port 8000) → ORM → SQLite
                             → Gemini API (AI)
                             → PyMuPDF (PDF)
```
Single server. One command to run.

### Pages
| Page | URL | Status |
|------|-----|--------|
| Dashboard | `/dashboard/` | ✅ Done |
| Cases List | `/cases/` | ✅ Done |
| Case Workspace | `/cases/<id>/` | ✅ Done |
| Medical Timeline | `/timeline/` | ✅ Done |
| Draft Editor | `/draft-editor/` | ✅ Done |
| Medical Analysis | `/medical-analysis/` | ✅ Done |
| AI Q&A Result | `/ask/` | ✅ Done |
| Error Page | auto | ✅ Done |

### Frontend Tech
- Django Templates (server-side rendering)
- Tailwind CSS via CDN
- Vanilla JavaScript (AJAX, chat, editor)
- No React, No Node.js required

### Features Working
- ✅ Real-time AI chat (per case context)
- ✅ Draft editor with AI generation (5 draft types)
- ✅ PDF upload + text extraction
- ✅ Medical timeline (table + timeline view)
- ✅ Case creation with PDF upload
- ✅ Compensation table
- ✅ CSRF protection on all forms
- ✅ Auto-save drafts every 30 seconds
- ✅ Toast notifications

---

## 🚀 How to Run

```bash
python backend/manage.py runserver 8000
```

Open → **http://127.0.0.1:8000**

Admin → **http://127.0.0.1:8000/admin/** (admin / admin123)

---

## 📦 Full Tech Stack

### Backend
| Tech | Version | Use |
|------|---------|-----|
| Python | 3.12 | Core language |
| Django | 6.0.4 | Web framework |
| Django REST Framework | 3.17.1 | REST API |
| django-cors-headers | 4.9.0 | CORS |
| SQLite | built-in | Database |

### AI / ML
| Tech | Use |
|------|-----|
| Google Gemini 2.5 Flash | Drafts, medical analysis, chat |
| google-generativeai | Gemini Python SDK |
| Ollama + Mistral/Phi3 | Local LLM (early scripts) |
| LangChain | RAG pipeline |
| FAISS | Vector store |
| HuggingFace sentence-transformers | Embeddings |

### Document Processing
| Tech | Use |
|------|-----|
| PyMuPDF (fitz) | PDF text extraction |
| ReportLab | PDF generation |
| python-docx | Word document generation |
| fpdf | PDF export |

### Frontend
| Tech | Use |
|------|-----|
| Django Templates | Server-side HTML |
| Tailwind CSS (CDN) | Styling |
| Vanilla JavaScript | Interactivity |
| Google Fonts (Inter) | Typography |

---

## 🔮 Phase 4: Next.js Frontend Migration (FUTURE)

When ready to upgrade to production-grade frontend:

**Prompt to use:**
```
We are building LegalAI — an Indian legal case management platform.

The Django REST API backend is already built at http://127.0.0.1:8000
All API endpoints are documented in progress.md

Now build the complete Next.js frontend:

Tech stack:
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS (compiled, not CDN)
- shadcn/ui components
- Zustand for state management
- TanStack Query for API calls
- Axios for HTTP

Design system (match exactly):
- Background: #F8F6F4
- Primary: #7B2C2C
- Accent: #C86F6F
- Font: Inter

Pages to build (match current Django templates exactly):
1. /dashboard
2. /cases
3. /cases/[id]
4. /timeline
5. /draft-editor
6. /medical-analysis
7. /ask

Connect all pages to Django API at http://127.0.0.1:8000/api/
Read templates/ folder for exact UI reference.
Read progress.md for full API endpoint list.
Create frontend in folder: frontend/
```

**What changes:** `templates/` → `frontend/` Next.js app
**What stays:** Django backend, SQLite, all AI logic, all API endpoints

---

## 📋 Known Limitations (Current)

| Limitation | Impact | Fix in Phase 4 |
|------------|--------|----------------|
| Tailwind via CDN (3MB) | Slow first load | Compiled Tailwind |
| Full page reloads | Less smooth UX | React SPA |
| No TypeScript | No type safety | TypeScript |
| No component reuse | Duplicate HTML | React components |
| No real-time updates | Manual refresh | WebSockets/SWR |

---

## 🗂️ Project Structure

```
legal ai/
├── backend/                    # Django project
│   ├── apps/
│   │   ├── cases/              # Case model + API
│   │   ├── documents/          # Document model + PDF extraction
│   │   ├── timeline/           # Timeline + Medical Summary
│   │   ├── drafts/             # Draft model + AI generation
│   │   └── web/                # HTML page views
│   ├── legalai/                # Django settings + URLs
│   ├── db.sqlite3              # Database
│   └── manage.py
├── templates/                  # Django HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── cases_list.html
│   ├── case_workspace.html
│   ├── timeline.html
│   ├── draft_editor.html
│   ├── medical_analysis.html
│   ├── ask_result.html
│   └── error.html
├── vault/                      # Legal knowledge base (PDFs)
│   ├── judgments/
│   ├── laws/
│   ├── medical_rules/
│   └── medical_templates/
├── DRAFT GENERATOR/            # ReportLab PDF generators
├── output/                     # Generated files
└── progress.md                 # This file
```


---

## ✅ Phase 4: New Features

| Feature | URL | Status |
|---------|-----|--------|
| Precedent Finder | /precedent-finder/ | ✅ Done |
| Missing Documents Checker | /missing-docs/ | ✅ Done |
| Demand Letter (draft type) | /draft-editor/ → AI Generate | ✅ Done |
| Settlement Letter (draft type) | /draft-editor/ → AI Generate | ✅ Done |

### Precedent Finder (`/precedent-finder/`)
- Search by case, injury type, location, age, income
- Returns top 5 relevant SC/HC judgments with citations
- Compensation range analysis (min/max/recommended)
- Legal strategy recommendations
- Quick reference landmark cases panel (Sarla Verma, Pranay Sethi, Raj Kumar, Reshma Kumari)

### Missing Documents Checker (`/missing-docs/`)
- 17-document MACT checklist across 6 categories
- Categories: Police, Medical, Insurance, Financial, Identity, Court
- Per-document status: Received ✓ / Missing ✗ / Pending ⏳ / N/A
- Progress bar showing filing readiness %
- AI-identified missing docs auto-marked from medical summary
- Status saved in localStorage (persists across sessions)
- "Ready to file" banner when all required docs received
- "Mark all received" per category button

### Draft Generator — 2 New Types
- 📨 Demand Letter to Insurance Company
- 🤝 Settlement Letter / Compromise Proposal
- Both in tab bar + AI Generate modal dropdown


---

## ✅ Phase 5: MedComply AI — AgentCon 2026

> Separate project inside `medcompliance/` folder
> **Run:** `python medcompliance/app.py`
> **Open:** http://127.0.0.1:7000

### Architecture
```
Upload PDF
    ↓ [LangGraph StateGraph]
Agent 1: Intake Agent        → extracts patient, doctor, diagnosis, consent, signatures
    ↓
Agent 2: Compliance Agent    → RAG against vault (SOPs, guidelines, medical rules)
    ↓
Agent 3: Risk Agent          → HIGH/MEDIUM/LOW risk with factor analysis
    ↓
Audit Agent                  → chronology, report, executive summary, verdict
    ↓
Compliance Dashboard + Report
```

### Files Created
| File | Purpose |
|------|---------|
| `medcompliance/app.py` | Flask app — routes, upload, session |
| `medcompliance/agents/workflow.py` | LangGraph StateGraph orchestrator |
| `medcompliance/agents/intake_agent.py` | Agent 1 — document extraction |
| `medcompliance/agents/compliance_agent.py` | Agent 2 — RAG compliance check |
| `medcompliance/agents/risk_agent.py` | Agent 3 — risk classification |
| `medcompliance/agents/audit_agent.py` | Agent 4 — audit report generation |
| `medcompliance/agents/llm.py` | Shared Gemini 2.5 Flash |
| `medcompliance/utils/pdf_utils.py` | PDF extraction + vault loader |
| `medcompliance/templates/base.html` | Dark navy theme, no CDN needed |
| `medcompliance/templates/dashboard.html` | Agent pipeline + recent reports |
| `medcompliance/templates/analyze.html` | Upload page with live agent steps |
| `medcompliance/templates/report.html` | Full compliance report UI |

### Features
- ✅ LangGraph orchestration (falls back to sequential if not available)
- ✅ 4 specialized AI agents
- ✅ RAG from existing vault PDFs (assessment guidelines, SOPs, discharge format)
- ✅ Compliance score 0–100
- ✅ Risk level HIGH/MEDIUM/LOW
- ✅ Violations table with severity
- ✅ Medical chronology
- ✅ Recommendations
- ✅ Audit verdict (PASS/CONDITIONAL_PASS/FAIL)
- ✅ Agent pipeline progress animation
- ✅ Self-contained CSS (no internet needed)
- ✅ Reuses existing vault + PDF utils
