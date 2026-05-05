import fitz
import os
import google.generativeai as genai

# ======== SETTINGS ========

genai.configure(api_key="AIzaSyD4BMcy9_CepkclmgW_zG5CH1J7g61JsDg")

CASE_PDF = r"C:\Users\hp\OneDrive\Documents\legal ai\sample_case_dummy.pdf"
VAULT_PATH = r"C:\Users\hp\OneDrive\Documents\legal ai\vault"

model = genai.GenerativeModel("gemini-2.5-flash")


# ======== PDF READER ========

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text


# ======== LOAD VAULT ========

def load_vault():
    knowledge = ""

    for root, dirs, files in os.walk(VAULT_PATH):
        for f in files:
            if f.endswith(".pdf"):
                print("Reading:", f)
                text = extract_text(os.path.join(root, f))

                knowledge += f"\n--- FROM {f} ---\n"
                knowledge += text

    return knowledge


# ======== ANALYSIS ========

def analyze(case_text, vault_text):

    prompt = f"""

ROLE: SENIOR INDIAN MACT ADVOCATE AI  
PURPOSE: Produce COURT-USABLE medical-legal report.

CRITICAL RULES:
- NEVER invent facts  
- Use ONLY provided CASE + VAULT  
- If data missing → write: NOT FOUND  
- Indian context only  
- Do NOT repeat instructions in output  

YOU MUST ANSWER EVERY SECTION BELOW.

================ REQUIRED OUTPUT ================

1) MEDICAL CHRONOLOGY
- Admission:
- Surgery:
- Discharge:
- Follow ups:

2) INJURIES LIST
- 
- 

3) TREATMENT SUMMARY
- 

4) FINANCIAL CALCULATION
- Hospital:
- Medicines:
- Scan:
- Physiotherapy:
- TOTAL:

5) CLAIM HEADS (MV ACT)
- Medical expenses:
- Loss of income:
- Pain & suffering:
- Future disability:

6) MISSING DOCUMENTS
- FIR:
- Income proof:
- Disability certificate:
- Insurance papers:

7) RELEVANT SECTIONS
- 166:
- 168:
- 173:

8) DRAFT DEMAND NOTE (5–6 lines)

=================================================

VAULT KNOWLEDGE:
{vault_text}

CASE FILE:
{case_text}

ANSWER NOW:

"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.05,
            "max_output_tokens": 2800,
            
        }
    )

    return response.text


# ======== RUN ========

print("Loading case...")
case = extract_text(CASE_PDF)

print("Loading vault...")
vault = load_vault()

print("Analyzing with GEMINI...\n")
result = analyze(case, vault)

print("\n===== RESULT =====\n")
print(result)
