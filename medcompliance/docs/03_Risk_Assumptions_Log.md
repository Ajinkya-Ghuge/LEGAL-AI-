# Risk & Assumptions Log
## Compliance & Governance Intelligence Agent — Nights Watch
**Version:** 1.0 | **Date:** July 16, 2026

---

## 1. Technical Risks & Mitigations

| # | Risk | Likelihood | Impact | Mitigation / Fallback |
|---|---|---|---|---|
| **TR-01** | Groq API rate limits hit during live demo | High | High | Exponential backoff (2s, 4s, 8s); switch to Gemini API (pre-configured, same LangChain interface); Ollama local (Llama 3.1 8B) as final offline fallback — demo stays live |
| **TR-02** | Render backend cold start during judge demo (~30s delay) | High | High | n8n keep-alive ping every 10 min during demo window; demo script begins with a warm-up API call 2 min before presentation |
| **TR-03** | LangGraph state graph deadlock (approval gate never resolves) | Low | Critical | Timeout check: if `approved is None` for > 10 min, surface explicit UI warning; manual override endpoint `POST /pipeline/:id/force-complete` for emergency demo use |
| **TR-04** | PyMuPDF fails to parse a scanned/image-only PDF | Medium | High | OCR fallback via `pytesseract`; demo documents pre-validated as text-native PDFs |
| **TR-05** | pgvector ivfflat index returns poor similarity results with small corpus | Medium | Medium | Demo policy corpus loaded with ≥ 20 chunked sections to ensure index quality; cosine similarity threshold tuned to 0.65 during integration testing |
| **TR-06** | scikit-learn model not trained before demo | Medium | Medium | Pre-train on synthetic labeled dataset (20 samples, 5 features) during data prep phase; model pickle committed to repo; if training fails, fall back to pure LLM-based scoring only |
| **TR-07** | Supabase free tier 500MB Postgres cap exceeded | Low | Medium | Monitor via Supabase dashboard; policy embeddings are the largest table — limit demo corpus to 30 policy sections (≈ 200KB vectors); delete test runs before demo |
| **TR-08** | React frontend fails to deploy on Vercel | Low | High | Local `vite dev` server as fallback; demo can run fully local |
| **TR-09** | CORS misconfiguration between React ↔ Node gateway | Medium | Medium | Pre-test CORS headers in integration phase; explicit `ALLOWED_ORIGINS` env var set on Render |
| **TR-10** | Groq LLM returns malformed JSON for structured extraction | Medium | Medium | Pydantic validation with retry (up to 3 attempts with corrective prompt); fallback to regex-based extraction for obligation text |

---

## 2. Assumptions

| # | Assumption | Implication if Wrong |
|---|---|---|
| **AS-01** | Demo documents are text-native PDFs (not scanned) | Need OCR pipeline (pytesseract) — add ~1 hour build time |
| **AS-02** | Groq Llama 3.3 70B produces sufficiently accurate obligation extraction without fine-tuning | May need prompt engineering iteration during build — allocated in integration phase |
| **AS-03** | Supabase pgvector performs adequately for demo corpus size (< 500 policy chunks) | No impact at this scale; risk only beyond 100K vectors |
| **AS-04** | A single Supabase project can serve both the Node gateway and the FastAPI service simultaneously | True for Supabase free tier; both services use the same Postgres connection string |
| **AS-05** | Render free tier allows two services (Node + FastAPI) on the same account | Yes, free tier allows up to 3 web services |
| **AS-06** | The hackathon demo environment has internet access for Groq/Gemini API calls | Ollama fallback is pre-loaded if demo is offline |
| **AS-07** | A 4-person team can complete the 9-hour build sequence on July 16 | Single-point risk: if a team member is unavailable, tasks re-assigned per fallback scope below |

---

## 3. Cut Priority — What Gets Dropped First

If build time runs short, features are cut in this exact order. **Never cut items marked 🔒.**

| Priority | Feature | Cut Decision |
|---|---|---|
| 🔒 **Never cut** | LangGraph orchestration with all 7 agents | Core demo value — judge scoring criterion |
| 🔒 **Never cut** | Citation trail (every claim has a source) | Audit defensibility — judge scoring criterion |
| 🔒 **Never cut** | Human approval gate | Governance requirement — unique differentiator |
| 🔒 **Never cut** | Gap classification (Covered/Partial/Gap) | Core output — demo would be meaningless without it |
| **Cut 1st** | scikit-learn risk classifier | Fall back to pure LLM-based risk scoring; output quality marginally lower, demo still works |
| **Cut 2nd** | Remediation auto-drafting | Show gap analysis + risk scores as the demo endpoint; skip remediation tasks |
| **Cut 3rd** | PDF export of audit report | Serve Markdown report via UI; skip WeasyPrint PDF generation |
| **Cut 4th** | n8n notification automation | Remove the optional automation layer; doesn't affect core agent flow |
| **Cut 5th** | Conversational Agent UI | Demo the pipeline flow; skip the Q&A chat interface |
| **Cut last** | React frontend polish | Use unstyled functional UI if Tailwind styling takes too long |

---

## 4. Dependency Risks

| Dependency | Version Pinned | Risk | Note |
|---|---|---|---|
| `langgraph` | `>=0.2.0` | API surface changed in 0.2.x | Pin to `0.2.28` |
| `langchain` | `>=0.2.0` | | Pin to `0.2.16` |
| `groq` (Python SDK) | `>=0.9.0` | | Pin to `0.9.0` |
| `fastapi` | `>=0.111.0` | | Pin to `0.111.1` |
| `scikit-learn` | `>=1.5.0` | | Pin to `1.5.1` |
| `pymupdf` | `>=1.24.0` | | Pin to `1.24.5` |
| `supabase` (Python) | `>=2.5.0` | | Pin to `2.5.3` |
| `vite` + React | `^5.x` | | Pin via `package-lock.json` |

All Python dependencies pinned in `requirements.txt`. All JS dependencies pinned via `package-lock.json` committed to repo.
