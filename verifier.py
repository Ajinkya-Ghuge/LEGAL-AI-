# ==========================================
# MEDICAL + ACCIDENT LEGAL AI (V1)
# Powered by your own Legal Vault
# ==========================================

import fitz        # PyMuPDF for PDF reading
import ollama      # Local LLM
import os

# ----------- PATH SETTINGS -----------

CASE_PDF = r"C:\Users\hp\OneDrive\Documents\legal ai\sample_case_dummy.pdf"

VAULT_PATH = r"C:\Users\hp\OneDrive\Documents\legal ai\vault"

# ----------- PDF READER -----------

def extract_text(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text

    except Exception as e:
        return f"Error reading PDF: {e}"


# ----------- LOAD YOUR LEGAL VAULT -----------

def load_vault():
    knowledge = ""

    for root, dirs, files in os.walk(VAULT_PATH):
        for file in files:
            if file.endswith(".pdf"):
                path = os.path.join(root, file)

                print(f"Reading vault file: {file}")

                text = extract_text(path)

                knowledge += f"\n\n--- KNOWLEDGE FROM: {file} ---\n"
                knowledge += text

    return knowledge


# ----------- CORE ANALYSIS -----------

def analyze_medical_case(case_text, vault_text):

    prompt = f"""

You are an EXPERT INDIAN MACT ADVOCATE.

Use ONLY the knowledge provided below.
Do NOT use general internet knowledge.

TASK:

1) Create MEDICAL CHRONOLOGY
   - admission date
   - surgeries
   - discharge
   - follow ups

2) Identify INJURIES & TREATMENT

3) CLAIM HEADS under Motor Vehicles Act
   - medical expenses
   - loss of income
   - pain & suffering
   - disability / future loss

4) MISSING DOCUMENT CHECK

5) Relevant SECTIONS from MV Act


-------------------------------------
LEGAL VAULT KNOWLEDGE:
{vault_text}
-------------------------------------

CASE FILE:
{case_text}

"""

    response = ollama.chat(
        model="mistral"
,
        messages=[
            {"role": "system", "content": "You are a senior Indian accident claim lawyer."},
            {"role": "user", "content": prompt}
        ]
    )

    return response["message"]["content"]


# ----------- RUN SYSTEM -----------

print("\n=== MEDICAL LEGAL AI STARTING ===\n")

print("1) Loading Case File...")
case_text = extract_text(CASE_PDF)

print("2) Loading Legal Vault...")
vault_text = load_vault()

print("\n3) Thinking like MACT Advocate...\n")
result = analyze_medical_case(case_text, vault_text)

print("\n========== MEDICAL LEGAL ANALYSIS ==========\n")
print(result)
print("\n============================================\n")
