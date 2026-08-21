# MedComply AI 🏥
### Healthcare Compliance & Governance Intelligence Agent
**AgentCon 2026 — National AI Hackathon**
*Theme: Building Enterprise AI Agents, ML Systems & Workflow Automation for Bharat*

---

## The Problem

Indian hospitals spend hours manually reviewing medical documents before internal audits and regulatory inspections. A single discharge summary must be cross-checked against AIIMS SOPs, MLC protocols, assessment guidelines, and hospital policy — slow, error-prone, and leaves audit trails incomplete.

**MedComply AI** automates the entire compliance pipeline — upload a medical document, and a 4-agent LangGraph pipeline extracts structured data, checks it against a RAG-powered knowledge base, assesses risk, and generates a board-ready audit report with PASS/FAIL verdict — in under 30 seconds.

---

## Screenshots

### Compliance Dashboard
![Audit Dashboard](audit.png)

### Compliance Audit Report — Top Section
![Audit Report](audit2.png)

### Full Report — Violations & Recommendations
![Report Detail](Report.png)

---

## System Architecture

```mermaid
graph TB
    Browser["🌐 Browser\nFlask Templates"] -->|HTTP POST · PDF upload| Flask["⚙️ Flask App\napp.py · port 7000"]
    Flask -->|extract_pdf_text| PDFUtils["📄 pdf_utils.py\nPyMuPDF"]
    PDFUtils -->|document_text| Flask
    Flask -->|run_compliance_workflow| WF["🔀 LangGraph Orchestrator\nagents/workflow.py\nStateGraph"]

    WF --> A1
    A1 --> A2
    A2 --> A3
    A3 --> A4
    A4 -->|flatten_result| Flask

    Flask -->|render| Report["📊 report.html\nScore · Verdict · Violations\nChronology · Recommendations"]

    subgraph VAULT ["📚 RAG Knowledge Base"]
        V1["AIIMS SOP Manual"]
        V2["Assessment Guidelines"]
        V3["Discharge Format"]
        V4["Motor Vehicles Act"]
        V5["MACT Judgments"]
    end

    A2 <-->|load_vault_knowledge| VAULT

    subgraph AGENTS ["🤖 4-Agent Pipeline"]
        A1["🔵 Agent 1\nIntake Agent"]
        A2["🟣 Agent 2\nCompliance Agent"]
        A3["🟠 Agent 3\nRisk Agent"]
        A4["🔴 Agent 4\nAudit Agent"]
    end

    A1 & A2 & A3 & A4 <-->|call_gemini| Gemini["✨ Gemini 2.5 Flash\nAPI"]
```

---

## 4-Agent Pipeline — End to End Flow

```mermaid
flowchart TD
    START(["📎 User Uploads PDF"]) --> EXTRACT["PyMuPDF\nextract_pdf_text()"]
    EXTRACT --> CHECK{Text\nextracted?}
    CHECK -- No --> FALLBACK["Use filename\nas context"]
    CHECK -- Yes --> INIT
    FALLBACK --> INIT

    INIT["Initialize WorkflowState\ndocument_text · doc_name\nintake_result · compliance_result\nrisk_result · audit_result · agent_log"] --> AG1

    subgraph PIPELINE ["⚙️ LangGraph StateGraph"]
        direction TB

        AG1["🔵 AGENT 1\nIntake Agent\n─────────────────\nGoal: Extract entities\nfrom raw document text\n─────────────────\nPrompt → Gemini\nReturns: structured JSON"]

        AG1 -->|"intake_result ✓\npatient · doctor · diagnosis\nconsent · signature · confidence"| AG2

        AG2["🟣 AGENT 2\nCompliance Agent\n─────────────────\nGoal: RAG check vs SOPs\nand medical guidelines\n─────────────────\nLoads vault PDFs → Gemini\nReturns: score + violations"]

        AG2 -->|"compliance_result ✓\nscore · status · violations\nmissing_items · recommendations"| AG3

        AG3["🟠 AGENT 3\nRisk Agent\n─────────────────\nGoal: Classify risk level\nfrom compliance findings\n─────────────────\nPrompt → Gemini\nReturns: HIGH/MEDIUM/LOW"]

        AG3 -->|"risk_result ✓\nrisk_level · patient_safety\nlegal_risk · audit_risk"| AG4

        AG4["🔴 AGENT 4\nAudit Agent\n─────────────────\nGoal: Generate full\naudit report\n─────────────────\nPrompt → Gemini\nReturns: verdict + summary"]
    end

    AG4 -->|"audit_result ✓\nverdict · chronology\nexecutive_summary"| FLATTEN

    FLATTEN["_flatten_result()\nmerge all 4 outputs"] --> REPORT

    subgraph REPORT ["📊 Report Output"]
        direction LR
        R1["Compliance Score\n0 – 100"]
        R2["Risk Level\nHigh / Medium / Low"]
        R3["Audit Verdict\nPASS / FAIL / CONDITIONAL"]
        R4["Violations Table\ntype · severity · section"]
        R5["Medical Chronology\ntimeline of events"]
        R6["Executive Summary\nfor management"]
    end
```

---

## Agent State Flow

```mermaid
stateDiagram-v2
    direction LR

    [*] --> WorkflowState : PDF uploaded

    state WorkflowState {
        [*] --> Initialized
        Initialized --> AfterIntake : Agent 1 populates intake_result
        AfterIntake --> AfterCompliance : Agent 2 populates compliance_result
        AfterCompliance --> AfterRisk : Agent 3 populates risk_result
        AfterRisk --> AfterAudit : Agent 4 populates audit_result
        AfterAudit --> [*]
    }

    WorkflowState --> [*] : flatten_result → report
```

---

## Agent 1 — Intake Agent

```mermaid
flowchart LR
    IN["document_text\nraw PDF content"] --> PROMPT["Build intake prompt\nmax 6000 chars"]
    PROMPT --> GEMINI["✨ Gemini API\ncall_gemini()"]
    GEMINI --> PARSE["Parse JSON\nclean markdown fences"]
    PARSE --> CHECK{Valid JSON?}
    CHECK -- Yes --> OUT
    CHECK -- No --> FALLBACK2["Fallback structure\nconfidence = 0.3"]
    FALLBACK2 --> OUT

    OUT["intake_result\n─────────────────────\npatient_name · age · gender\ndoctor_name · hospital_name\nadmission_date · discharge_date\ndiagnosis list · treatments list\nmedicines · consent_present\nsignature_present · dates_present\ndocument_type · confidence"]
```

**Example output:**
```json
{
  "patient_name": "Dummy Kumar",
  "doctor_name": "Dr. Sharma",
  "hospital_name": "City Hospital",
  "diagnosis": ["Fracture of right femur", "Minor head injury"],
  "consent_present": false,
  "signature_present": false,
  "extraction_confidence": 0.92
}
```

---

## Agent 2 — Compliance Agent (RAG)

```mermaid
flowchart TB
    INTAKE["intake_result\n+ document_text"] --> BUILD["Build compliance prompt"]

    VAULT_LOAD["load_vault_knowledge()\nwalk /vault directory"] --> PDF1["AIIMS SOP Manual\n.pdf → PyMuPDF"]
    VAULT_LOAD --> PDF2["Assessment Guidelines\n.pdf → PyMuPDF"]
    VAULT_LOAD --> PDF3["Discharge Format\n.pdf → PyMuPDF"]
    VAULT_LOAD --> PDF4["Motor Vehicles Act\n.pdf → PyMuPDF"]
    VAULT_LOAD --> PDF5["MACT Judgments\n.pdf → PyMuPDF"]

    PDF1 & PDF2 & PDF3 & PDF4 & PDF5 --> CONCAT["Concatenate text\nmax 4000 chars\nvault_knowledge string"]
    CONCAT --> BUILD
    INTAKE --> BUILD

    BUILD --> GEMINI["✨ Gemini API"]
    GEMINI --> RESULT["compliance_result\n─────────────────────\ncompliance_score  0–100\noverall_status\nviolations list\ncompliant_items list\nmissing_items list\nrecommendations list\nreasoning"]

    subgraph CHECKS ["Compliance Checks"]
        C1["Missing Consent"]
        C2["Missing Signature"]
        C3["Missing Diagnosis"]
        C4["Missing Sections"]
        C5["Policy Violations"]
        C6["Documentation Gaps"]
    end

    RESULT --> CHECKS
```

---

## Agent 3 — Risk Assessment Agent

```mermaid
flowchart LR
    IN["compliance_result\n+ intake_result"] --> PROMPT["Build risk prompt"]
    PROMPT --> GEMINI["✨ Gemini API"]
    GEMINI --> PARSE{Valid JSON?}

    PARSE -- Yes --> RESULT
    PARSE -- No --> FALLBACK3["Heuristic fallback\nscore lt 40 → HIGH\nscore lt 70 → MEDIUM\nelse → LOW"]
    FALLBACK3 --> RESULT

    RESULT["risk_result\n─────────────────────────\nrisk_level  HIGH/MEDIUM/LOW\nrisk_score  0–100\npatient_safety_risk\nlegal_risk\naudit_risk\nrisk_summary\nimmediate_actions list\nrisk_factors list"]

    subgraph DIMENSIONS ["Risk Dimensions"]
        D1["Patient Safety Risk\nGaps that harm patients"]
        D2["Legal Risk\nLiability from missing docs"]
        D3["Audit Risk\nChance of inspection failure"]
    end

    RESULT --> DIMENSIONS
```

---

## Agent 4 — Audit Report Agent

```mermaid
flowchart TB
    IN["intake_result\ncompliance_result\nrisk_result\n+ document_text"] --> PROMPT["Build audit prompt"]
    PROMPT --> GEMINI["✨ Gemini API"]
    GEMINI --> PARSE2{Valid JSON?}

    PARSE2 -- Yes --> RESULT2
    PARSE2 -- No --> FALLBACK4["Structured fallback\nfrom compliance + risk data"]
    FALLBACK4 --> RESULT2

    RESULT2["audit_result\n─────────────────────────\nexecutive_summary\nmedical_chronology list\ncompliance_report\nrisk_report\nrecommendations list\naudit_verdict\nnext_audit_date\ntimestamp"]

    RESULT2 --> VD{Verdict}
    VD -- score ≥ 80 --> PASS["✅ PASS"]
    VD -- score 60–79 --> COND["⚠️ CONDITIONAL PASS"]
    VD -- score lt 60 --> FAIL["❌ FAIL"]
```

---

## Full Sequence Diagram

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as Flask app.py
    participant P as pdf_utils.py
    participant W as Workflow Orchestrator
    participant A1 as Agent 1 Intake
    participant A2 as Agent 2 Compliance
    participant V as Vault PDFs
    participant A3 as Agent 3 Risk
    participant A4 as Agent 4 Audit
    participant G as ✨ Gemini API

    U->>F: POST /analyze (PDF)
    F->>P: extract_pdf_text(path)
    P-->>F: document_text

    F->>W: run_compliance_workflow(text, name)
    W->>A1: run(state)
    A1->>G: intake prompt
    G-->>A1: structured JSON
    A1-->>W: state + intake_result

    W->>A2: run(state)
    A2->>V: load_vault_knowledge()
    V-->>A2: vault_knowledge string
    A2->>G: compliance prompt + vault
    G-->>A2: compliance JSON
    A2-->>W: state + compliance_result

    W->>A3: run(state)
    A3->>G: risk prompt
    G-->>A3: risk JSON
    A3-->>W: state + risk_result

    W->>A4: run(state)
    A4->>G: audit prompt
    G-->>A4: audit JSON
    A4-->>W: state + audit_result

    W-->>F: flatten_result dict
    F->>U: render report.html
```

---

## LangGraph Graph

```mermaid
graph LR
    S([START]) --> A1
    A1["🔵 intake\nagent"] --> A2
    A2["🟣 compliance\nagent"] --> A3
    A3["🟠 risk\nagent"] --> A4
    A4["🔴 audit\nagent"] --> E([END])

    style S fill:#1a2332,color:#fff,stroke:none
    style E fill:#1a2332,color:#fff,stroke:none
    style A1 fill:#3b82f6,color:#fff,stroke:none
    style A2 fill:#8b5cf6,color:#fff,stroke:none
    style A3 fill:#f59e0b,color:#fff,stroke:none
    style A4 fill:#ef4444,color:#fff,stroke:none
```

---

## RAG Knowledge Base

| # | File | Category | Used For |
|---|---|---|---|
| 1 | `sop-manual-for-mlcs-aiimsk-fmt.pdf` | Medical Rules | AIIMS MLC SOP — required documentation standards |
| 2 | `assessment_guidelines (1).pdf` | Medical Rules | Disability & injury assessment protocols |
| 3 | `D.-E-Mitra_FORMAT-04_Hospital-Discharge-Summary-Format.pdf` | Templates | Required sections in discharge summaries |
| 4 | `motor vehcle act.pdf` | Laws | MV Act sections for MACT compliance |
| 5 | `AWARDINMOTORACCIDENTCASES.pdf` | Judgments | Precedents for compensation computation |

---

## Project Structure

```
medcompliance/
├── app.py                     Flask app — routes, session, .env loading
├── agents/
│   ├── llm.py                 Gemini wrapper — loads key from .env, model fallback
│   ├── intake_agent.py        Agent 1 — entity extraction
│   ├── compliance_agent.py    Agent 2 — RAG compliance check
│   ├── risk_agent.py          Agent 3 — risk classification
│   ├── audit_agent.py         Agent 4 — audit report generation
│   └── workflow.py            LangGraph StateGraph orchestrator
├── utils/
│   └── pdf_utils.py           PyMuPDF extraction + vault loader
├── templates/
│   ├── landing.html           Landing page (dark maroon)
│   ├── base.html              Nav + shared styles
│   ├── dashboard.html         Reports dashboard
│   ├── analyze.html           Upload form + agent progress
│   └── report.html            Full audit report view
├── vault/
│   ├── medical_rules/         SOP manuals · assessment guidelines
│   ├── medical_templates/     Hospital discharge formats
│   ├── laws/                  Motor Vehicles Act
│   └── judgments/             MACT award judgments
├── uploads/                   Temp PDF storage (gitignored)
├── docs/                      PRD · System Design · Team Plan
├── .gitignore                 Blocks .env · __pycache__ · uploads
└── readme1.md                 This file
```

---

## Setup & Run

### 1. Clone
```bash
git clone https://github.com/Kunalkandke/Nights_Watch_AgentCon.git
cd Nights_Watch_AgentCon
```

### 2. Install
```bash
pip install flask google-generativeai PyMuPDF langgraph
```

### 3. Configure API key
```bash
# Create medcompliance/.env  (never commit this file)
GEMINI_API_KEY=your_gemini_api_key_here
```
Get a free key → https://aistudio.google.com/app/apikey

### 4. Run
```bash
cd medcompliance
python app.py
# Open http://127.0.0.1:7000
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph `StateGraph` |
| AI Model | Gemini 2.5 Flash → 1.5 Flash (auto fallback) |
| PDF Processing | PyMuPDF (fitz) |
| RAG | Vault PDFs injected into compliance prompt |
| Backend | Flask (Python) |
| Frontend | Jinja2 templates + inline CSS |
| Knowledge Base | AIIMS SOPs · MLC Manual · Assessment Guidelines |

---

## Hackathon Criteria

| Criteria | Implementation |
|---|---|
| ✅ AI Agents | 4 specialised agents — distinct goal, input, output, prompt |
| ✅ Agentic Workflow | LangGraph `StateGraph` with typed `WorkflowState` |
| ✅ Workflow Automation | Upload → audit report, zero manual steps |
| ✅ Decision Support | PASS/FAIL verdict + prioritised action items |
| ✅ Enterprise Intelligence | Compliance scoring, risk matrix, executive summary |
| ✅ RAG | 5 vault PDFs loaded and grounded into compliance prompt |
| ✅ Multi-Agent Collaboration | All 4 agents share and enrich a single state object |
| ✅ LangGraph | `StateGraph` nodes + edges + sequential execution |

---

**Team — Nights Watch · AgentCon 2026 · July 16, 2026**
