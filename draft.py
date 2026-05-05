import fitz
import os
import google.generativeai as genai
from datetime import datetime
from fpdf import FPDF

# ==============================
# CONFIG
# ==============================

genai.configure(api_key="AIzaSyD4BMcy9_CepkclmgW_zG5CH1J7g61JsDg")

CASE_PDF = r"C:\Users\hp\OneDrive\Documents\legal ai\sample_case_dummy.pdf"

model = genai.GenerativeModel("gemini-2.5-flash")


# ==============================
# PDF TEXT EXTRACTOR
# ==============================

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text


# ==============================
# AI LEGAL DRAFT GENERATOR
# ==============================

def generate_drafts(case_text):

    prompt = f"""
You are a SENIOR INDIAN MACT LAWYER.

Generate PROFESSIONAL COURT-READY LEGAL DRAFTS.

CASE DATA:
{case_text}

OUTPUT IN EXACT LEGAL FORMAT:

--------------------------------------
1) MACT CLAIM PETITION DRAFT
--------------------------------------
Include:
- Tribunal Heading
- Parties Details
- Facts of Accident
- Medical History & Injuries
- Compensation Table
- Legal Grounds (MV Act)
- Prayer Clause
- Verification

--------------------------------------
2) LEGAL NOTICE DRAFT (INSURANCE)
--------------------------------------
Include:
- Advocate Header
- Client Details
- Legal Grounds
- Demand Clause
- Legal Warning

--------------------------------------
3) WRITTEN ARGUMENTS ON COMPENSATION
--------------------------------------
Include:
- Medical Expenses
- Loss of Income
- Pain & Suffering
- Disability Compensation
- Case Law References

Use Indian court drafting tone.
Write like a senior advocate.
"""

    response = model.generate_content(prompt)
    return response.text


# ==============================
# PDF EXPORT FUNCTION
# ==============================

def save_as_pdf(text):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", size=11)

    for line in text.split("\n"):
        pdf.multi_cell(0, 7, line)

    timestamp = datetime.now().strftime("%d%m_%H%M")
    filename = f"legal_draft_{timestamp}.pdf"

    pdf.output(filename)

    return filename


# ==============================
# RUN SYSTEM
# ==============================

print("\n=== AUTO LEGAL DRAFT GENERATOR STARTED ===\n")

print("Loading case file...")
case_text = extract_text(CASE_PDF)

print("Generating legal drafts using AI...")
draft_text = generate_drafts(case_text)

print("\n========== GENERATED LEGAL DRAFT ==========\n")
print(draft_text)

print("\nSaving PDF...")
pdf_file = save_as_pdf(draft_text)

print(f"\n PDF Generated Successfully: {pdf_file}")
print("\n=== READY FOR LAWYER USE ===\n")
