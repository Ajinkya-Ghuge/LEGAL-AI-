"""
AGENT 4: Audit Report Agent
Goal: Generate complete audit report, medical chronology, executive summary
Input: All previous agent outputs
Output: Full structured audit report
"""
import json
from datetime import datetime
from .llm import call_gemini

PROMPT_TEMPLATE = """
You are a Healthcare Audit Report Agent.

Generate a complete, professional audit report based on the analysis below.

INTAKE DATA: {intake_data}
COMPLIANCE RESULT: {compliance_data}
RISK RESULT: {risk_data}
ORIGINAL TEXT (excerpt): {doc_text}

Generate a comprehensive audit report. Return ONLY valid JSON:
{{
  "executive_summary": "3-4 sentence executive summary for hospital management",
  "medical_chronology": [
    {{"date": "date or N/A", "event": "what happened", "significance": "clinical or administrative"}}
  ],
  "compliance_report": {{
    "summary": "Compliance summary paragraph",
    "score": 0-100,
    "status": "COMPLIANT/PARTIALLY_COMPLIANT/NON_COMPLIANT",
    "key_findings": ["finding 1", "finding 2"],
    "violations_detail": "Detailed violation analysis"
  }},
  "risk_report": {{
    "summary": "Risk summary paragraph",
    "level": "HIGH/MEDIUM/LOW",
    "critical_issues": ["issue 1", "issue 2"]
  }},
  "recommendations": [
    {{"priority": "IMMEDIATE/SHORT_TERM/LONG_TERM", "action": "What to do", "rationale": "Why"}}
  ],
  "audit_verdict": "PASS or FAIL or CONDITIONAL_PASS",
  "next_audit_date": "Recommended date for next audit (e.g., 3 months)"
}}

Be professional. Be specific. Return ONLY JSON.
"""


def run(state: dict) -> dict:
    print("  [Agent 4] Audit Agent generating final report...")

    intake = state.get("intake_result", {})
    compliance = state.get("compliance_result", {})
    risk = state.get("risk_result", {})
    doc_text = state.get("document_text", "")

    prompt = PROMPT_TEMPLATE.format(
        intake_data=json.dumps(intake, indent=2)[:1000],
        compliance_data=json.dumps(compliance, indent=2)[:1500],
        risk_data=json.dumps(risk, indent=2)[:1000],
        doc_text=doc_text[:2000],
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
        audit = json.loads(raw)
    except Exception:
        score = compliance.get("compliance_score", 50)
        risk_level = risk.get("risk_level", "MEDIUM")
        verdict = "PASS" if score >= 80 else ("CONDITIONAL_PASS" if score >= 60 else "FAIL")
        audit = {
            "executive_summary": f"Document compliance audit completed. Overall score: {score}/100. Risk level: {risk_level}. Verdict: {verdict}. Immediate attention required for {len(compliance.get('violations', []))} compliance violations.",
            "medical_chronology": [
                {"date": intake.get("admission_date", "N/A"), "event": "Patient Admission", "significance": "clinical"},
                {"date": intake.get("discharge_date", "N/A"), "event": "Patient Discharge", "significance": "clinical"},
            ],
            "compliance_report": {
                "summary": f"Compliance score of {score}/100. {len(compliance.get('violations', []))} violations found.",
                "score": score,
                "status": compliance.get("overall_status", "PARTIALLY_COMPLIANT"),
                "key_findings": compliance.get("missing_items", [])[:3],
                "violations_detail": f"{len(compliance.get('violations', []))} violations identified.",
            },
            "risk_report": {
                "summary": risk.get("risk_summary", "Risk assessment completed."),
                "level": risk_level,
                "critical_issues": risk.get("immediate_actions", [])[:3],
            },
            "recommendations": [
                {"priority": "IMMEDIATE", "action": r, "rationale": "Compliance requirement"}
                for r in compliance.get("recommendations", [])[:3]
            ],
            "audit_verdict": verdict,
            "next_audit_date": "3 months",
        }

    # Add timestamp and metadata
    audit["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    audit["doc_name"] = state.get("doc_name", "Unknown Document")
    audit["agent_log"] = state.get("agent_log", [])

    state["audit_result"] = audit
    state["agent_log"].append({
        "agent": "Audit Agent",
        "status": "complete",
        "verdict": audit.get("audit_verdict"),
    })
    print(f"  [Agent 4] Done. Verdict: {audit.get('audit_verdict')}")
    return state
