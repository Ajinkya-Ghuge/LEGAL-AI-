# Team & Workflow Plan
## Compliance & Governance Intelligence Agent — Nights Watch
**Event:** AgentCon 2026 | **Build Date:** July 16, 2026 | **Total Build Window:** ~9 hours

---

## 1. Team Role Assignments

| Member | Role | Primary Responsibilities |
|---|---|---|
| **Member A** | Agent Backend Lead | FastAPI service, LangGraph state graph, all 7 agents, LLM integration, scikit-learn model, pgvector queries |
| **Member B** | Frontend Lead | React + Tailwind UI, all pages/components, Supabase Auth integration, API integration with Node gateway |
| **Member C** | Data Prep & Demo Lead | Demo document preparation, policy corpus chunking + embedding, prompt engineering, Ollama local setup, demo script rehearsal |
| **Member D** | Integration & DevOps Lead | Node/Express API gateway, Supabase schema + RLS setup, Render + Vercel deployment, environment config, n8n setup, end-to-end integration testing |

---

## 2. 9-Hour Build Sequence (July 16, 2026)

### Phase 0 — Setup (Hour 0, All Members, Parallel)

| Task | Owner | Duration |
|---|---|---|
| Initialize repo structure, branch strategy (`main`, `dev`, feature branches) | D | 15 min |
| Supabase project setup: run schema SQL, enable pgvector, configure RLS policies, create Storage bucket | D | 30 min |
| FastAPI project scaffold (Poetry/pip, folder structure, health endpoint) | A | 20 min |
| React + Vite + Tailwind scaffold, Supabase Auth configured | B | 20 min |
| Node/Express gateway scaffold, Supabase client, JWT middleware | D | 20 min |
| Download + test Ollama local (Llama 3.1 8B), verify Groq API key | C | 20 min |
| Prepare demo regulation PDFs (2 regulations) + 5 internal policy docs | C | 30 min |

---

### Phase 1 — Core Agent Pipeline (Hours 1–4, A + C)

| Task | Owner | Duration |
|---|---|---|
| `AgentState` TypedDict implementation | A | 15 min |
| LangGraph `StateGraph` skeleton: nodes, edges, conditional routing | A | 30 min |
| **Regulatory Intake Agent:** PyMuPDF parse + Groq structured extraction | A | 45 min |
| **Policy Mapping Agent:** pgvector similarity search + LLM classification | A | 60 min |
| Prompt engineering for obligation extraction + gap classification | C | 60 min (parallel) |
| **Gap & Risk Agent:** scikit-learn model train + LLM blend scoring | A | 45 min |
| **Remediation Planner Agent:** Pydantic structured output + DB write | A | 30 min |
| **Audit & Reporting Agent:** Jinja2 template + citation assembly | A | 30 min |
| **Conversational Agent:** LangChain retrieval chain + chat history | A | 30 min |
| Human Approval Gate: LangGraph interrupt + resume logic | A | 20 min |
| Groq → Gemini → Ollama fallback chain implementation | C | 45 min |
| Policy corpus chunking + embedding + Supabase insert script | C | 45 min |

---

### Phase 2 — Gateway & Frontend (Hours 2–5, B + D, Parallel with Phase 1)

| Task | Owner | Duration |
|---|---|---|
| All Node/Express routes: `/documents`, `/runs`, `/reports`, `/chat` | D | 90 min |
| Supabase Storage integration (upload + signed URL download) | D | 30 min |
| React pages: Login, Document Upload, Run Dashboard | B | 90 min |
| React pages: Gap Analysis View (obligation table + status badges) | B | 45 min |
| React pages: Remediation Review + Approve/Reject UI | B | 45 min |
| React pages: Audit Report View + Markdown renderer | B | 30 min |
| React pages: Chat Interface (streaming responses) | B | 30 min |
| n8n webhook setup (report-ready notification) | D | 20 min |

---

### Phase 3 — Integration & Testing (Hours 5–7, All Members)

| Task | Owner | Duration |
|---|---|---|
| Connect React ↔ Node gateway (test all endpoints) | B + D | 45 min |
| Connect Node gateway ↔ FastAPI agent service (test pipeline trigger, polling) | D + A | 45 min |
| End-to-end pipeline run with demo regulation doc #1 | All | 30 min |
| Fix integration bugs | All | 60 min (buffer) |
| Test human approval gate flow end-to-end | B + A | 20 min |
| Test Ollama fallback | C | 20 min |
| Verify citation completeness in generated report | C | 15 min |

---

### Phase 4 — Demo Prep & Polish (Hours 7–9)

| Task | Owner | Duration |
|---|---|---|
| Deploy FastAPI to Render, Node gateway to Render, React to Vercel | D | 45 min |
| Load production demo data (regulation + policy docs) | C | 30 min |
| Full end-to-end demo run on production URLs | All | 20 min |
| Demo script: 5-min narration, screen flow, talking points per judge criterion | C | 30 min |
| README polish, architecture diagram screenshots in README | C + D | 20 min |
| Final commit + push, verify public repo is clean (no secrets) | D | 10 min |
| Buffer for unexpected issues | All | 30 min |

---

## 3. GitHub Projects Board Structure

### Columns

| Column | Meaning |
|---|---|
| **Backlog** | All tasks not yet started |
| **In Progress** | Active work (WIP limit: 2 per person) |
| **Blocked** | Waiting on another task or person |
| **Review / Testing** | Code written, needs integration test |
| **Done** | Merged to `dev` branch, tested |

---

### Initial Ticket List

```
EPIC: Infrastructure & Setup
  #1  Supabase schema setup + RLS policies              [D]  Phase 0
  #2  FastAPI scaffold + health endpoint                [A]  Phase 0
  #3  Node/Express scaffold + JWT middleware            [D]  Phase 0
  #4  React + Vite + Supabase Auth scaffold             [B]  Phase 0
  #5  Ollama local setup + Groq API key verification    [C]  Phase 0

EPIC: Agent Pipeline
  #6  AgentState TypedDict                              [A]  Phase 1
  #7  LangGraph StateGraph skeleton + routing           [A]  Phase 1
  #8  Regulatory Intake Agent                           [A]  Phase 1
  #9  Policy Mapping Agent (RAG + LLM classify)         [A]  Phase 1
  #10 Gap & Risk Agent (ML + LLM blend)                 [A]  Phase 1
  #11 Remediation Planner Agent                         [A]  Phase 1
  #12 Audit & Reporting Agent (Jinja2 + citations)      [A]  Phase 1
  #13 Conversational Agent (LangChain retrieval)        [A]  Phase 1
  #14 Human Approval Gate (LangGraph interrupt)         [A]  Phase 1
  #15 Groq → Gemini → Ollama fallback chain             [C]  Phase 1
  #16 Prompt engineering: extraction + gap classify     [C]  Phase 1
  #17 Policy corpus embedding + Supabase insert         [C]  Phase 1

EPIC: API Gateway
  #18 Document upload + storage endpoint               [D]  Phase 2
  #19 Pipeline run trigger + polling endpoints         [D]  Phase 2
  #20 Approval endpoint                                [D]  Phase 2
  #21 Report download endpoint                         [D]  Phase 2
  #22 Chat endpoint                                    [D]  Phase 2
  #23 n8n notification webhook                         [D]  Phase 2

EPIC: Frontend
  #24 Login / Signup page                              [B]  Phase 2
  #25 Document upload + management page                [B]  Phase 2
  #26 Run dashboard (status + progress)                [B]  Phase 2
  #27 Gap analysis view (obligation table)             [B]  Phase 2
  #28 Remediation review + approve/reject UI           [B]  Phase 2
  #29 Audit report view + Markdown renderer            [B]  Phase 2
  #30 Chat interface                                   [B]  Phase 2

EPIC: Integration & Demo
  #31 End-to-end pipeline integration test             [All] Phase 3
  #32 Deployment: Render (FastAPI + Node) + Vercel     [D]   Phase 4
  #33 Demo data load (regulations + policies)          [C]   Phase 4
  #34 Demo script + talking points                     [C]   Phase 4
  #35 README polish + diagram screenshots              [C+D] Phase 4
  #36 Final repo audit (no secrets, public, clean)     [D]   Phase 4
```

---

## 4. Branching Strategy

```
main          ← stable, deployed, only merged from dev after full integration
dev           ← integration branch; all feature branches merge here
feature/agent-pipeline      (A)
feature/gateway-api         (D)
feature/frontend            (B)
feature/data-and-prompts    (C)
```

PR rule: minimum 1 reviewer approval before merging to `dev`. No direct pushes to `main`.
