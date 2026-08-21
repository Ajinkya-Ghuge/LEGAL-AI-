"""
AGENT 3: Risk Assessment Agent
Goal: Determine risk level based on compliance results
Input: Compliance result
Output: Risk level (HIGH/MEDIUM/LOW), risk summary, risk factors
"""
import json
from .llm import call_gemini

PROMPT_TEMPLATE = """
You are a Healthcare Risk Assessment Agent.

Based on the compliance analysis below, determine the risk level for this medical document.

COMPLIANCE RESULT:
{compliance_data}

INTAKE DATA:
{intake_data}

Assess risk considering:
- Patient safety implications
- Legal liability exposure
- Audit failure risk
- Regulatory penalties
- Documentation completeness

Return ONLY valid JSON:
{{
  "risk_level": "HIGH" or "MEDIUM" or "LOW",
  "risk_score": 0 to 100,
  "risk_factors": [
    {{
      "factor": "Risk factor name",
      "impact": "HIGH" or "MEDIUM" or "LOW",
      "explanation": "Why this is a risk"
    }}
  ],
  "immediate_actions": ["Action needed immediately"],
  "risk_summary": "2-3 sentence executive summary of the risk",
  "patient_safety_risk": "HIGH" or "MEDIUM" or "LOW",
  "legal_risk": "HIGH" or "MEDIUM" or "LOW",
  "audit_risk": "HIGH" or "MEDIUM" or "LOW"
}}

Return ONLY JSON.
"""


def run(state: dict) -> dict:
    print("  [Agent 3] Risk Agent assessing...")

    compliance = state.get("compliance_result", {})
    intake = state.get("intake_result", {})
    score = compliance.get("compliance_score", 50)
    violations = compliance.get("violations", [])

    prompt = PROMPT_TEMPLATE.format(
        compliance_data=json.dumps(compliance, indent=2)[:2000],
        intake_data=json.dumps(intake, indent=2)[:1000],
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
        risk = json.loads(raw)
    except Exception:
        # Fallback risk calculation
        high_violations = sum(1 for v in violations if v.get("severity") == "HIGH")
        if score < 40 or high_violations >= 3:
            level, risk_score = "HIGH", 85
        elif score < 70 or high_violations >= 1:
            level, risk_score = "MEDIUM", 55
        else:
            level, risk_score = "LOW", 20

        risk = {
            "risk_level": level,
            "risk_score": risk_score,
            "risk_factors": [
                {"factor": "Compliance Score", "impact": level,
                 "explanation": f"Compliance score of {score}/100 indicates {'significant' if score < 50 else 'moderate'} gaps"}
            ],
            "immediate_actions": ["Review all high-severity violations", "Obtain missing documentation"],
            "risk_summary": f"Document has {len(violations)} compliance violations with an overall score of {score}/100. Risk level assessed as {level}.",
            "patient_safety_risk": "HIGH" if not intake.get("consent_present") else "MEDIUM",
            "legal_risk": "HIGH" if high_violations >= 2 else "MEDIUM",
            "audit_risk": "HIGH" if score < 50 else "MEDIUM",
        }

    state["risk_result"] = risk
    state["agent_log"].append({
        "agent": "Risk Agent",
        "status": "complete",
        "risk_level": risk.get("risk_level"),
    })
    print(f"  [Agent 3] Done. Risk Level: {risk.get('risk_level')}")
    return state
