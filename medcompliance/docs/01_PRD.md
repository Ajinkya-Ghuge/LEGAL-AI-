# Product Requirements Document (PRD)
## Compliance & Governance Intelligence Agent
**Project:** Nights Watch | **Event:** AgentCon 2026 | **Date:** July 16, 2026

---

## 1. Problem Statement

Indian enterprises in BFSI, healthcare, and fintech are required to continuously track and comply with an ever-expanding corpus of regulatory mandates — RBI Master Directions, SEBI LODR, DPDP Act 2023, GST notifications, and more. Today, compliance officers manually:

1. Read and parse new regulatory circulars (often 50–200 page PDFs)
2. Cross-reference each obligation against internal policy documents
3. Identify gaps and assign remediation owners
4. Compile audit-ready reports with full citation trails

This process takes **days to weeks per circular**, is **error-prone under time pressure**, and creates **audit risk** when the citation trail between a regulatory obligation and the internal policy response is incomplete or undocumented.

**Nights Watch** automates this entire pipeline. A compliance officer uploads a new regulation; the system autonomously extracts obligations, maps them to existing policies, identifies gaps, scores risk, drafts a remediation plan, and produces a citation-traced audit report — with a mandatory human approval gate before any action is finalized.

---

## 2. Target Users

| Persona | Role | Primary Need |
|---|---|---|
| **Compliance Officer** | Owns regulatory adherence | Fast gap analysis, audit-ready output |
| **Risk Manager** | Quantifies and tracks org risk | Risk scores, remediation owners, deadlines |
| **Legal/Policy Team** | Maintains internal policy corpus | Know which policies need updating and why |
| **Internal Auditor** | Reviews compliance posture | Full citation trail: regulation clause → policy section → action taken |
| **CTO / CRO** | Executive oversight | Dashboard summary, approval workflow |

---

## 3. User Stories

### Core Flow
- **US-01** As a Compliance Officer, I can upload a new regulatory PDF so the system extracts all obligations automatically, without manual reading.
- **US-02** As a Compliance Officer, I can see which extracted obligations are already covered by existing policy, which are partially covered, and which are gaps — with the exact source clause cited for each.
- **US-03** As a Risk Manager, I can see a risk score (0–100) for each compliance gap, with an explanation of why the score was assigned.
- **US-04** As a Compliance Officer, I can review an AI-drafted remediation plan (action items, suggested owners, deadlines) before it is finalized.
- **US-05** As an Internal Auditor, I can download a PDF/Markdown audit report where every claim links back to the exact regulation clause and internal policy section that was assessed.
- **US-06** As any user, I can ask natural-language questions about any regulation or internal policy in the knowledge base and receive cited answers.

### Secondary
- **US-07** As a Compliance Officer, I can upload internal policy documents to build/update the policy knowledge base.
- **US-08** As an Admin, I can manage users and control who can approve remediation plans.
- **US-09** As a Compliance Officer, I receive a notification (email/webhook via n8n) when a new report is ready for review.

---

## 4. In-Scope for Hackathon MVP

| Feature | In Scope |
|---|---|
| PDF upload & structured obligation extraction | ✅ |
| RAG-based policy mapping (Covered / Partial / Gap) | ✅ |
| Risk scoring (LLM reasoning + scikit-learn classifier) | ✅ |
| AI-drafted remediation plan (owner, deadline, action) | ✅ |
| Citation-traced audit report (Markdown + PDF export) | ✅ |
| Human approval gate before report finalization | ✅ |
| Conversational Q&A over the knowledge base | ✅ |
| Supabase Auth (email/password) | ✅ |
| Document management UI (upload, list, status) | ✅ |
| n8n notification trigger (report ready webhook) | ✅ |

---

## 5. Out of Scope for MVP

| Feature | Reason |
|---|---|
| Real-time regulatory feed ingestion (auto-pull from MCA, RBI portal) | API access complexity; manual upload sufficient for demo |
| Multi-tenant org isolation | Single-org demo scope |
| Fine-tuned domain LLM | Zero-cost constraint; Llama 3.3 70B via Groq sufficient |
| Mobile app | Web-first for hackathon |
| Integrations with GRC tools (ServiceNow, Archer) | Post-MVP |
| Version control / diff of policy documents across uploads | Post-MVP |

---

## 6. Success Metrics (MVP Demo)

| Metric | Target |
|---|---|
| Obligation extraction accuracy (manual spot-check on demo docs) | ≥ 90% of obligations correctly identified |
| Gap classification accuracy (Covered / Partial / Gap) | ≥ 85% agreement with human reviewer |
| End-to-end pipeline latency (upload → report ready) | < 3 minutes for a 20-page circular |
| Citation completeness | 100% of gap/covered claims have a source clause |
| Human approval gate | 0 reports finalized without explicit user approval |
| Live demo uptime | System runs fully offline via Ollama fallback if API limits hit |

---

## 7. Constraints

- **Zero cost:** All infrastructure must run on free tiers (Groq, Supabase, Render, Vercel)
- **Public repo:** Per hackathon rules; no secrets committed
- **Build window:** ~9 hours on July 16, 2026
- **Team size:** 4 members
