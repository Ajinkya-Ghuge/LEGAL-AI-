import fitz
import ollama

PDF_PATH = r"C:\Users\hp\OneDrive\Documents\legal ai\4. Moot Problem Preliminary and Semi Final Round.pdf"

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def analyze_case(case_text):
    prompt = f"""
You are a senior Indian advocate.

Analyze this case file and provide:

 Markout the legal problems in above case
 And what section will be filed by police




CASE FILE:
{case_text}
"""

    response = ollama.chat(
        model="phi3",
        messages=[
            {"role": "system", "content": "You are a senior Indian advocate."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["message"]["content"]

print("Loading case file...")
case_text = extract_text(PDF_PATH)

print("Thinking like a senior lawyer. Please wait...\n")
result = analyze_case(case_text)

print("\n========== LEGAL ANALYSIS ==========\n")
print(result)
print("\n===================================\n")
