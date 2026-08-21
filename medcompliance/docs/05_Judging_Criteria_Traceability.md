# Judging Criteria Traceability Matrix
## Compliance & Governance Intelligence Agent — Nights Watch
**Event:** AgentCon 2026 | **Total Marks:** 100

This matrix maps every rubric line item to the specific document, section, diagram, or code artifact that proves it. Use this as the pre-submission checklist.

---

## Traceability Table

| # | Judging Criterion | Marks | Proof Artifact | Location | Checklist |
|---|---|---|---|---|---|
| **1** | **Problem Understanding & Business Relevance** | **15** | | | |
| 1.1 | Clear articulation of the problem in Indian enterprise context | 5 | PRD §1 Problem Statement | `docs/01_PRD.md` | ☐ |
| 1.2 | Target users and use cases well-defined | 5 | PRD §2 Target Users + §3 User Stories | `docs/01_PRD.md` | ☐ |
| 1.3 | Business relevance — why this matters for Bharat | 5 | PRD §1 (BFSI/fintech/healthcare framing) + README intro | `docs/01_PRD.md`, `READMEmd` | ☐ |
| **2** | **AI Agent Architecture & Design** | **20** | | | |
| 2.1 | Multi-agent architecture clearly designed | 8 | System Design §2 Agent Architecture (LangGraph state graph Mermaid) + §2 Agent Descriptions table | `docs/02_System_Design.md` | ☐ |
| 2.2 | Agent roles, responsibilities, and routing logic | 6 | System Design §2 Agent Descriptions table + §4 Shared State Schema | `docs/02_System_Design.md` | ☐ |
| 2.3 | Orchestration pattern (supervisor/state graph) | 6 | System Design §2 stateDiagram + §7 Sequence Diagram + LangGraph code | `docs/02_System_Design.md`, `agent_service/` | ☐ |
| **3** | **ML/AI Integration** | **15** | | | |
| 3.1 | LLM used meaningfully (not just a chatbot) | 5 | System Design §2 (7 agents each use LLM for distinct tasks) + §7 Sequence Diagram LLM call steps | `docs/02_System_Design.md` | ☐ |
| 3.2 | ML model integrated (scikit-learn risk classifier) | 5 | System Design §2 Gap & Risk Agent description + §4 RiskScore.ml_score + §4 final_score formula | `docs/02_System_Design.md` | ☐ |
| 3.3 | RAG / embeddings / vector search used | 5 | System Design §3 Data Flow Diagram (pgvector path) + §5 DB Schema (policy_embeddings table) + §2 Policy Mapping Agent | `docs/02_System_Design.md` | ☐ |
| **4** | **Workflow Automation & Orchestration** | **15** | | | |
| 4.1 | Automated end-to-end pipeline (not manual steps) | 8 | System Design §7 Sequence Diagram (full automated flow) + §3 Data Flow Diagram | `docs/02_System_Design.md` | ☐ |
| 4.2 | Conditional routing / branching logic | 4 | System Design §2 stateDiagram (skip reporting if 0 obligations; skip remediation if 0 gaps) | `docs/02_System_Design.md` | ☐ |
| 4.3 | n8n / external automation integration | 3 | System Design §1 HLA diagram (n8n notification layer) + Team Plan #23 n8n webhook ticket | `docs/02_System_Design.md`, `docs/04_Team_Workflow_Plan.md` | ☐ |
| **5** | **Technical Implementation** | **15** | | | |
| 5.1 | Clean, working code across the full stack | 6 | All source code in `agent_service/`, `gateway/`, `frontend/` directories | Repo root | ☐ |
| 5.2 | Correct use of chosen frameworks (LangGraph, FastAPI, React) | 5 | System Design §2 + §6 API Contract + code | `docs/02_System_Design.md` | ☐ |
| 5.3 | Database schema well-designed | 4 | System Design §5 Database Schema (9 tables, pgvector index, RLS) | `docs/02_System_Design.md` | ☐ |
| **6** | **Scalability & Enterprise Readiness** | **10** | | | |
| 6.1 | Architecture can scale beyond hackathon demo | 4 | System Design §8.3 Latency Expectations + §8.1 Citation Requirement (audit defensibility) + pgvector trade-off note | `docs/02_System_Design.md` | ☐ |
| 6.2 | Security / auth / governance considered | 3 | System Design §8.5 Security + §5 DB Schema (RLS) + PRD §4 human approval gate | `docs/02_System_Design.md`, `docs/01_PRD.md` | ☐ |
| 6.3 | NFRs documented (latency, rate limits, resource constraints) | 3 | System Design §8.4 Free-Tier Constraints table + Risk Log §1 TR-01 through TR-04 | `docs/02_System_Design.md`, `docs/03_Risk_Assumptions_Log.md` | ☐ |
| **7** | **Demo & Presentation** | **5** | | | |
| 7.1 | Live demo runs end-to-end without failure | 3 | Demo script (Team Plan §2 Phase 4) + Ollama offline fallback (Risk Log TR-01) | `docs/04_Team_Workflow_Plan.md`, `docs/03_Risk_Assumptions_Log.md` | ☐ |
| 7.2 | Presentation clearly explains the system | 2 | README + all docs + demo talking points (Team Plan Phase 4) | `READMEmd`, `docs/` | ☐ |
| **8** | **Innovation & Originality** | **5** | | | |
| 8.1 | Novel application of AI agents to a real Indian regulatory problem | 3 | PRD §1 (specific Indian regulations named: RBI, SEBI, DPDP, GST) + System Design §8.1 citation requirement as differentiator | `docs/01_PRD.md`, `docs/02_System_Design.md` | ☐ |
| 8.2 | Unique design choices worth defending | 2 | System Design §8.1 (citation enforcement at ARA layer) + §8.2 (hard approval gate via LangGraph interrupt) + trade-off note (pgvector vs. dedicated vector DB) | `docs/02_System_Design.md` | ☐ |

---

## Pre-Submission Checklist

Before submitting, verify the following are true:

### Documentation
- [ ] All 5 docs committed to `docs/` in the public repo
- [ ] README updated with project summary, architecture diagram, and setup instructions
- [ ] No secrets or API keys in any committed file

### Code Artifacts
- [ ] `agent_service/` — FastAPI + LangGraph agent service running
- [ ] `gateway/` — Node/Express API gateway running
- [ ] `frontend/` — React + Tailwind app deployed to Vercel
- [ ] `agent_service/models/risk_classifier.pkl` — scikit-learn model committed
- [ ] `agent_service/requirements.txt` — all deps pinned
- [ ] `gateway/package.json` + `package-lock.json` — all deps pinned
- [ ] `supabase/schema.sql` — full DB schema committed

### Live System
- [ ] FastAPI service deployed and healthy on Render (`GET /health` returns 200)
- [ ] Node gateway deployed and healthy on Render
- [ ] React frontend deployed and accessible on Vercel
- [ ] Supabase project has demo data loaded (policy corpus embedded)
- [ ] Ollama local running and tested as fallback

### Demo Flow
- [ ] End-to-end pipeline run completed successfully on production URLs
- [ ] Human approval gate tested (approve + reject flows)
- [ ] Audit report downloads with full citation trail
- [ ] Conversational agent returns cited answers
- [ ] Demo script rehearsed — 5-minute run-through completed

---

## Scoring Projection

| Criterion | Max | Confidence | Notes |
|---|---|---|---|
| Problem Understanding | 15 | High | Strong Indian regulatory context; specific acts named |
| AI Agent Architecture | 20 | High | 7-agent LangGraph graph with conditional routing is clearly differentiated |
| ML/AI Integration | 15 | High | RAG + scikit-learn + LLM blend is a genuine hybrid approach |
| Workflow Automation | 15 | High | Fully automated pipeline; n8n adds external automation layer |
| Technical Implementation | 15 | Medium-High | Risk: integration bugs under time pressure — buffer allocated |
| Scalability | 10 | Medium | NFRs documented; RLS + auth in place; may lack production load testing |
| Demo | 5 | High | Ollama fallback + Render keep-alive mitigates demo failure risk |
| Innovation | 5 | High | Citation enforcement + hard approval gate are genuinely novel governance features |
| **Total** | **100** | | **Projected: 88–95 / 100** |
