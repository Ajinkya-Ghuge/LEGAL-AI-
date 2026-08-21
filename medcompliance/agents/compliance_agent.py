"""
AGENT 2: Compliance Intelligence Agent
Goal: Check document against medical rules, SOPs, and guidelines using RAG
Input: Intake result + vault knowledge
Output: Compliance score, violations, recommendations
"""
import json, os
from .llm import call_gemini
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from utils.pdf_utils import load_vault_knowledge

VAULT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "vault"
)

PROMPT_TEMPLATE = """
You are a Healthcare Compliance Intelligence Agent with expertise in medical documentation standards.

COMPLIANCE KNOWLEDGE BASE (Hospital SOPs, Medical Rules, Assessment Guidelines):
{vault_knowledge}

EXTRACTED DOCUMENT DATA:
{intake_data}

ORIGINAL DOCUMENT TEXT (first 3000 chars):
{doc_text}

Perform a thorough compliance check. Return ONLY valid JSON:
{{
  "compliance_score": 0 to 100,
  "overall_status": "COMPLIANT" or "PARTIALLY_COMPLIANT" or "NON_COMPLIANT",
  "violations": [
    {{
      "type": "MISSING_CONSENT" or "MISSING_SIGNATURE" or "MISSING_DIAGNOSIS" or "MISSING_SECTION" or "POLICY_VIOLATION" or "DOCUMENTATION_GAP",
      "severity": "HIGH" or "MEDIUM" or "LOW",
      "description": "What is missing or violated",
      "section": "Which section/requirement this relates to"
    }}
  ],
  "compliant_items": ["list of things that ARE compliant"],
  "missing_items": ["list of missing required items"],
  "policy_violations": ["list of specific policy violations found"],
  "recommendations": ["actionable recommendation 1", "recommendation 2"],
  "reasoning": "Brief explanation of the compliance assessment"
}}

Be specific. Reference the knowledge base standards. Return ONLY JSON.
"""


def run(state: dict) -> dict:
    print("  [Agent 2] Compliance Agent checking against vault knowledge...")

    intake = state.get("intake_result", {})
    doc_text = state.get("document_text", "")

    vault_knowledge = load_vault_knowledge(VAULT_PATH, max_chars=4000)
    if not vault_knowledge:
        vault_knowledge = """
Hospital SOP Standards:
- Patient name, age, gender must be documented
- Admission and discharge dates required
- Diagnosis must be clearly stated
- Treating doctor signature required
- Informed consent must be obtained and documented
- All medications must be listed with dosage
- Treatment plan must be documented
- Follow-up instructions required
"""

    prompt = PROMPT_TEMPLATE.format(
        vault_knowledge=vault_knowledge,
        intake_data=json.dumps(intake, indent=2)[:2000],
        doc_text=doc_text[:3000],
    )

    raw = call_gemini(prompt)
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip().rstrip("```").strip()

    try:
        compliance = json.loads(raw)
    except Exception:
        # Fallback
        consent = intake.get("consent_present", False)
        sig = intake.get("signature_present", False)
        score = 50 + (20 if consent else 0) + (20 if sig else 0)
        violations = []
        if not consent:
            violations.append({"type": "MISSING_CONSENT", "severity": "HIGH",
                                "description": "Informed consent not documented", "section": "Consent Section"})
        if not sig:
            violations.append({"type": "MISSING_SIGNATURE", "severity": "HIGH",
                                "description": "Doctor signature missing", "section": "Authorization"})

        compliance = {
            "compliance_score": score,
            "overall_status": "PARTIALLY_COMPLIANT" if score >= 50 else "NON_COMPLIANT",
            "violations": violations,
            "compliant_items": ["Patient identification present"] if intake.get("patient_name") else [],
            "missing_items": ["Consent documentation", "Doctor signature"] if not consent else [],
            "policy_violations": [],
            "recommendations": ["Obtain signed consent form", "Ensure doctor countersignature"],
            "reasoning": "Basic compliance check performed based on available data.",
        }

    state["compliance_result"] = compliance
    state["agent_log"].append({
        "agent": "Compliance Agent",
        "status": "complete",
        "score": compliance.get("compliance_score", 0),
        "violations": len(compliance.get("violations", [])),
    })
    print(f"  [Agent 2] Done. Score: {compliance.get('compliance_score')} | Violations: {len(compliance.get('violations', []))}")
    return state
