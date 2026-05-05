import fitz
import ollama

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    return "".join([p.get_text() for p in doc])

def analyze_case(text):
    prompt = f"""
You are a senior Indian advocate.

Analyze the following case file and provide:

1. Case Summary
2. Key Facts
3. Sections Involved
4. Strong & Weak Points
5. Legal Strategy

CASE FILE:
{text}
"""
    return ollama.generate(model="mistral", prompt=prompt)["response"]

print("\n=== INDIAN LEGAL AI ===")
path = input("Enter PDF path: ")
case_text = extract_text(path)
result = analyze_case(case_text)

print("\n===== LEGAL ANALYSIS =====\n")
print(result)
