"""
AGENT 1: Intake Agent
Goal: Extract structured medical data from document text
Input: Raw document text
Output: Structured JSON with patient, doctor, diagnosis, treatment, etc.
"""
import json
from .llm import call_gemini

GOAL = "Extract structured medical entities from unstructured document text"

PROMPT_TEMPLATE = """
You are a Medical Document Intake Agent.
Extract ALL available structured information from this medical document.

Return ONLY valid JSON with this exact structure:
{{
  "patient_name": "string or null",
  "age": "string or null",
  "gender": "string or null",
  "doctor_name": "string or null",
  "hospital_name": "string or null",
  "admission_date": "string or null",
  "discharge_date": "string or null",
  "diagnosis": ["list", "of", "diagnoses"],
  "treatments": ["list", "of", "treatments"],
  "medicines": ["list", "of", "medicines"],
  "surgeries": ["list"],
  "consent_present": true or false,
  "signature_present": true or false,
  "dates_present": true or false,
  "sections_found": ["list", "of", "sections"],
  "document_type": "discharge_summary or medical_record or prescription or other",
  "extraction_confidence": 0.0 to 1.0
}}

DOCUMENT:
{text}

Return ONLY the JSON object. No explanation.
"""


def run(state: dict) -> dict:
    text = state.get("document_text", "")
    doc_name = state.get("doc_name", "unknown")

    print(f"  [Agent 1] Intake Agent processing: {doc_name}")

    prompt = PROMPT_TEMPLATE.format(text=text[:6000])
    raw = call_gemini(prompt)

    # Clean markdown fences
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip().rstrip("```").strip()

    try:
        extracted = json.loads(raw)
    except Exception:
        # Fallback structured data
        extracted = {
            "patient_name": "Not found",
            "doctor_name": "Not found",
            "hospital_name": "Not found",
            "diagnosis": ["Unable to extract"],
            "treatments": [],
            "medicines": [],
            "consent_present": False,
            "signature_present": False,
            "dates_present": False,
            "sections_found": [],
            "document_type": "unknown",
            "extraction_confidence": 0.3,
        }

    state["intake_result"] = extracted
    state["agent_log"] = state.get("agent_log", [])
    state["agent_log"].append({
        "agent": "Intake Agent",
        "status": "complete",
        "confidence": extracted.get("extraction_confidence", 0.5),
    })
    print(f"  [Agent 1] Done. Confidence: {extracted.get('extraction_confidence', 0.5)}")
    return state
