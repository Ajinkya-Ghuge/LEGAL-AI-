import fitz
import os
import google.generativeai as genai

# ================= SETTINGS =================

genai.configure(api_key="AIzaSyD4BMcy9_CepkclmgW_zG5CH1J7g61JsDg")  # replace with your key

CASE_PDF = r"C:\Users\hp\OneDrive\Documents\legal ai\sample_case_dummy.pdf"
VAULT_PATH = r"C:\Users\hp\OneDrive\Documents\legal ai\vault"

model = genai.GenerativeModel("gemini-2.5-flash")

MAX_CASE_CHARS = 8000
MAX_VAULT_CHARS_PER_FILE = 3500


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


# ================= SMART VAULT LOADER (RAG-LIKE) =================

def load_relevant_vault(case_text):
    knowledge = ""
    case_keywords = ["accident", "motor", "injury", "medical", "hospital", "mact"]

    for root, dirs, files in os.walk(VAULT_PATH):
        for f in files:
            if f.endswith(".pdf"):
                path = os.path.join(root, f)
                text = extract_text(path)

                if any(k in text.lower() for k in case_keywords):
                    print("Using Vault File:", f)

                    knowledge += f"\n--- SOURCE: {f} ---\n"
                    knowledge += text[:MAX_VAULT_CHARS_PER_FILE]

    return knowledge


# ================= CORE AI ANALYSIS =================

def analyze(case_text, vault_text):

    prompt = f"""
You are a SENIOR INDIAN MACT ADVOCATE with 20+ years of courtroom experience.

STRICT RULES:
- DO NOT guess facts
- If information is missing, write: NOT FOUND
- Use ONLY given Case + Vault
- Use Indian legal tone (court style)
- Output must be VERY DETAILED and PROFESSIONAL

==================== TASK ====================

Generate a FULL professional MACT injury case report with:

1) MEDICAL CHRONOLOGY
   - Admission date
   - Surgery date
   - Hospital stay
   - Discharge date
   - Follow-ups
   - Recovery timeline

2) INJURIES IDENTIFIED
   - List injuries
   - Severity assessment

3) TREATMENT SUMMARY
   - Surgery details
   - Medicines
   - Rehabilitation

4) FINANCIAL & COMPENSATION ANALYSIS
   - Actual medical costs
   - Estimated future expenses
   - Loss of income (if found)
   - Pain & suffering estimate
   - Disability compensation estimate

5) CLAIM HEADS UNDER MOTOR VEHICLES ACT
   - Medical expenses
   - Loss of income
   - Pain & suffering
   - Future disability
   - Loss of amenities
   - Conveyance & diet

6) MISSING DOCUMENTS CHECKLIST

7) RELEVANT LEGAL SECTIONS (with explanation)


8) LAWYER INSIGHTS
   - Strength of claim
   - Risks
   - Recommended legal strategy

==================== LEGAL VAULT ====================
{vault_text}
=====================================================

==================== CASE FILE =======================
{case_text}
=====================================================
"""

    response = model.generate_content(prompt)
    return response.text


# ================= RUN SYSTEM =================

print("\n=== MEDICAL LEGAL AI STARTING ===\n")

print("1) Loading case file...")
case = extract_text(CASE_PDF)[:MAX_CASE_CHARS]

print("2) Loading relevant legal vault...")
vault = load_relevant_vault(case)

print("\n3) Analyzing like Senior MACT Advocate...\n")
result = analyze(case, vault)

print("\n========== FINAL LEGAL REPORT ==========\n")
print(result)
print("\n========================================\n")



import sys
sys.stdout.reconfigure(encoding='utf-8')  # ✅ Fix for Unicode error in Windows terminal

import fitz  # PyMuPDF
import os
import google.generativeai as genai

# ================= SETTINGS =================

genai.configure(api_key="YOUR_API_KEY_HERE")  # 🔴 Put your API key here

CASE_PDF = r"C:\Users\hp\OneDrive\Documents\legal ai\sample_case_dummy.pdf"
VAULT_PATH = r"C:\Users\hp\OneDrive\Documents\legal ai\vault"

model = genai.GenerativeModel("gemini-2.5-flash")

MAX_CASE_CHARS = 8000
MAX_VAULT_CHARS_PER_FILE = 3500

# ================= PDF TEXT EXTRACTOR =================

def extract_text(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text
    except Exception as e:
        print("Error reading PDF:", e)
        return ""

# ================= SMART VAULT LOADER (RAG-LIKE) =================

def load_relevant_vault(case_text):
    knowledge = ""
    case_keywords = ["accident", "motor", "injury", "medical", "hospital", "mact"]

    for root, dirs, files in os.walk(VAULT_PATH):
        for f in files:
            if f.endswith(".pdf"):
                path = os.path.join(root, f)
                text = extract_text(path)

                if any(k in text.lower() for k in case_keywords):
                    print("Using Vault File:", f)

                    knowledge += f"\n--- SOURCE: {f} ---\n"
                    knowledge += text[:MAX_VAULT_CHARS_PER_FILE] + "\n"

    return knowledge

# ================= CORE AI ANALYSIS =================

def analyze(case_text, vault_text):

    prompt = f"""
You are a SENIOR INDIAN MACT ADVOCATE with 20+ years of courtroom experience.

STRICT RULES:
- DO NOT guess facts
- If information is missing, write: NOT FOUND
- Use ONLY given Case + Vault
- Use Indian legal tone (court style)
- Output must be VERY DETAILED and PROFESSIONAL

==================== TASK ====================

Generate a FULL professional MACT injury case report with:

1) MEDICAL CHRONOLOGY
   - Admission date
   - Surgery date
   - Hospital stay
   - Discharge date
   - Follow-ups
   - Recovery timeline

2) INJURIES IDENTIFIED
   - List injuries
   - Severity assessment

3) TREATMENT SUMMARY
   - Surgery details
   - Medicines
   - Rehabilitation

4) FINANCIAL & COMPENSATION ANALYSIS
   - Actual medical costs
   - Estimated future expenses
   - Loss of income (if found)
   - Pain & suffering estimate
   - Disability compensation estimate

5) CLAIM HEADS UNDER MOTOR VEHICLES ACT
   - Medical expenses
   - Loss of income
   - Pain & suffering
   - Future disability
   - Loss of amenities
   - Conveyance & diet

6) MISSING DOCUMENTS CHECKLIST

7) RELEVANT LEGAL SECTIONS (with explanation)

8) LAWYER INSIGHTS
   - Strength of claim
   - Risks
   - Recommended legal strategy

==================== LEGAL VAULT ====================
{vault_text}
=====================================================

==================== CASE FILE =======================
{case_text}
=====================================================
"""

    response = model.generate_content(prompt)
    return response.text

# ================= RUN SYSTEM =================

print("\n=== MEDICAL LEGAL AI STARTING ===\n")

print("1) Loading case file...")
case = extract_text(CASE_PDF)[:MAX_CASE_CHARS]

print("2) Loading relevant legal vault...")
vault = load_relevant_vault(case)

print("\n3) Analyzing like Senior MACT Advocate...\n")
result = analyze(case, vault)

print("\n========== FINAL LEGAL REPORT ==========\n")

# ✅ Print safely
print(result)

print("\n========================================\n")

# ✅ Also save to file (recommended)
output_file = "final_legal_report.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(result)

print(f" Report saved to: {output_file}")
