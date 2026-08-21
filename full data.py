import fitz
import os
import google.generativeai as genai
from dotenv import load_dotenv

# ================= SETTINGS =================

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

CASE_PDF = r"C:\Users\hp\OneDrive\Documents\legal ai\sample_case_dummy.pdf"
VAULT_PATH = r"C:\Users\hp\OneDrive\Documents\legal ai\vault"

model = genai.GenerativeModel("gemini-2.5-flash")

MAX_CASE_CHARS = 12000   # Full case
MAX_TOTAL_VAULT_CHARS = 70000  # Full vault combined


# ================= PDF TEXT EXTRACTOR =================

def extract_text(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text
    except:
        return ""


# ================= LOAD FULL LEGAL VAULT =================

def load_full_vault():
    knowledge = ""

    print("\nLoading FULL Legal Vault...\n")

    for root, dirs, files in os.walk(VAULT_PATH):
        for f in files:
            if f.endswith(".pdf"):
                path = os.path.join(root, f)
                print("Including FULL Vault File:", f)

                text = extract_text(path)

                knowledge += f"\n\n================ SOURCE FILE: {f} ================\n"
                knowledge += text

    return knowledge[:MAX_TOTAL_VAULT_CHARS]


# ================= CORE AI ANALYSIS =================

def analyze(case_text, vault_text):

    prompt = f"""
You are a SENIOR INDIAN MACT ADVOCATE with 20+ years of legal and courtroom experience.

STRICT RULES:
- DO NOT hallucinate
- DO NOT guess missing facts
- If data not found write: NOT FOUND
- Use ONLY Case File + Legal Vault text
- Use Indian court tone
- Output must be extremely professional and detailed
- Treat this like a real MACT legal file, not a chatbot reply


==================== TASK ====================

Prepare a FULL MACT Injury Legal Intelligence Report:

1) MEDICAL CHRONOLOGY
   - Admission
   - Surgery
   - Hospital duration
   - Discharge
   - Follow-ups
   - Recovery timeline

2) INJURIES IDENTIFIED
   - Injury list
   - Severity classification

3) TREATMENT SUMMARY
   - Surgery
   - Medicines
   - Rehabilitation
   - Rest period

4) FINANCIAL & COMPENSATION ANALYSIS
   - Medical expenses (actual)
   - Estimated future expenses
   - Loss of income (if available)
   - Pain & suffering analysis
   - Disability compensation outlook

5) CLAIM HEADS UNDER MOTOR VEHICLES ACT
   - Medical
   - Income loss
   - Pain & suffering
   - Disability
   - Loss of amenities
   - Conveyance
   - Special diet

6) MISSING DOCUMENT CHECKLIST

7) RELEVANT LEGAL SECTIONS (EXPLAINED)
   - MV Act 166
   - MV Act 168
   - MV Act 173  or any other relevant from vault

8) LAWYER INSIGHTS
   - Case strengths
   - Case risks
   - Legal strategy
   - Settlement vs Trial recommendation

==================== LEGAL VAULT ====================
{vault_text}
=====================================================

==================== CASE FILE =======================
{case_text}
=====================================================

Produce a court-ready legal intelligence report.
"""

    response = model.generate_content(prompt)
    return response.text


# ================= RUN SYSTEM =================

print("\n=== MEDICAL LEGAL AI STARTING (FULL VAULT MODE) ===\n")

print("1) Loading case file...")
case = extract_text(CASE_PDF)[:MAX_CASE_CHARS]

print("2) Loading FULL legal vault...")
vault = load_full_vault()

print("\n3) Analyzing like Senior MACT Advocate...\n")
result = analyze(case, vault)

print("\n========== FINAL LEGAL REPORT ==========\n")
print(result)
print("\n========================================\n")
