# 🤖 AI System Improvement Plan

## 🔴 **CURRENT LIMITATIONS** (Identified)

### 1. PDF Processing
- ❌ Truncates to 50K chars (~40 pages) even for 500-page files
- ❌ Basic keyword matching misses medical context
- ❌ No OCR - scanned PDFs completely fail
- ❌ Doesn't extract tables (lab results, medication lists)
- ❌ No prioritization of discharge summaries, final diagnostic reports

### 2. AI Context Awareness
- ❌ Chatbot doesn't know which page user is on
- ❌ No awareness of case documents beyond summary
- ❌ Generic responses - not case-specific enough
- ❌ Can't cite specific pages/sections
- ❌ Limited to 8K context window (vault + case)

### 3. Output Quality
- ❌ Plain text blob - no structure
- ❌ No formatting (headings, bullets, tables)
- ❌ No source citations
- ❌ No confidence scores (what's certain vs guessed)
- ❌ Not in legal document format

### 4. Reliability
- ❌ No validation - AI can hallucinate
- ❌ Single point of failure (Gemini API)
- ❌ No retry logic
- ❌ No progress tracking (user waits in dark)
- ❌ All-or-nothing (no partial results)

---

## ✅ **SOLUTION: 4-Phase Improvement Plan**

---

## **PHASE 1: Enhanced PDF Processing** (High Priority)

### 1.1 Full Document Processing
**Current:** Truncates to 50K chars
**New:** Process ALL pages, store intelligently

```python
# New approach:
- Extract full text from ALL pages (no truncation)
- Store summary per page in JSON
- Tag pages by type (admission, surgery, discharge, lab results)
- Create semantic chunks (not just first N chars)
```

### 1.2 Intelligent Page Classification
```python
PAGE_TYPES = {
    "ADMISSION": ["admitted", "admission date", "presenting complaints"],
    "DISCHARGE": ["discharge summary", "final diagnosis", "condition at discharge"],
    "SURGERY": ["operative notes", "procedure", "surgeon", "anesthesia"],
    "LAB_RESULTS": ["blood test", "x-ray", "mri", "ct scan", "pathology"],
    "PRESCRIPTION": ["prescribed", "medication", "dosage", "rx"],
    "CONSULTATION": ["consultation", "specialist", "referred to"],
}
```

### 1.3 OCR Support (Gemini Vision)
```python
def extract_with_ocr(pdf_path):
    """Use Gemini Vision for scanned PDFs"""
    for page in pdf_pages:
        if is_scanned(page):
            image = page_to_image(page)
            text = gemini_vision.extract_text(image)
        else:
            text = page.get_text()  # standard PyMuPDF
    return text
```

### 1.4 Table Extraction
```python
# Use PyMuPDF table detection
tables = page.find_tables()
for table in tables:
    df = table.to_pandas()  # Convert to structured data
    # Store in JSON for AI consumption
```

---

## **PHASE 2: Context-Aware Chatbot** (High Priority)

### 2.1 Page-Aware Context
```python
# Track user's current page
session["current_page"] = {
    "route": "/case/123/timeline",
    "case_id": 123,
    "section": "timeline",
    "visible_events": [1, 2, 3]  # IDs of visible timeline events
}

# Chatbot uses this context
def chat_with_context(message, session_data):
    current_page = session_data.get("current_page", {})
    case_id = current_page.get("case_id")
    section = current_page.get("section")
    
    # Load relevant data
    case = Case.objects.get(pk=case_id)
    context = build_context(case, section)
    
    prompt = f"""
    USER IS VIEWING: {section} page of Case #{case.case_no}
    VISIBLE DATA: {context}
    USER QUESTION: {message}
    """
```

### 2.2 Document-Aware Responses
```python
# Chatbot can reference specific documents
def get_document_context(case_id):
    docs = Document.objects.filter(case_id=case_id)
    context = ""
    for doc in docs:
        # Include page summaries, not full text
        context += f"\n--- {doc.original_name} ({doc.pages} pages) ---\n"
        context += doc.page_summaries[:500]  # Brief overview per doc
    return context
```

### 2.3 Citation Support
```python
# AI must cite sources
prompt = f"""
Answer the question and CITE SOURCES using this format:
[Source: discharge_summary.pdf, Page 12]

Example:
"The patient was diagnosed with compound fracture [Source: medical_report.pdf, Page 3]"
"""
```

---

## **PHASE 3: Structured AI Output** (Medium Priority)

### 3.1 Markdown Formatting
```python
prompt = f"""
Return output in MARKDOWN format with:
## Headings
### Subheadings
- Bullet points
**Bold** for emphasis
| Tables | when | needed |

This will be displayed in a rich text viewer.
"""
```

### 3.2 JSON Schema Validation
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class MedicalSummary(BaseModel):
    injuries: List[str] = Field(description="List of injuries")
    timeline: List[TimelineEvent]
    treatments: List[Treatment]
    missing_docs: List[str]
    case_strength: Literal["Strong", "Moderate", "Weak"]
    confidence: float = Field(ge=0, le=1)  # 0-1 confidence score
    
# Validate AI output
try:
    validated = MedicalSummary(**ai_response)
except ValidationError:
    # Retry or ask user to review
```

### 3.3 Confidence Scores
```python
# AI indicates confidence per fact
{
    "injury": "Compound fracture of tibia",
    "confidence": 0.95,  # High - found in multiple pages
    "source": "discharge_summary.pdf:12, xray_report.pdf:3"
},
{
    "income": "₹30,000/month",
    "confidence": 0.60,  # Low - inferred, not explicitly stated
    "source": "Inferred from occupation: software engineer"
}
```

---

## **PHASE 4: Reliability & UX** (Medium Priority)

### 4.1 Progress Tracking
```python
# Real-time progress updates via WebSocket or polling
def generate_with_progress(case_id):
    update_status(case_id, "Extracting PDF text... 10%")
    text = extract_pdf()
    
    update_status(case_id, "Loading legal vault... 30%")
    vault = load_vault()
    
    update_status(case_id, "Analyzing injuries... 50%")
    injuries = ai_analyze_injuries()
    
    update_status(case_id, "Generating timeline... 70%")
    timeline = ai_generate_timeline()
    
    update_status(case_id, "Complete! 100%")
```

### 4.2 Retry Logic with Fallback
```python
MODELS_TO_TRY = [
    "gemini-2.5-flash",     # Fastest
    "gemini-1.5-pro",       # More accurate
    "gpt-4o-mini",          # Fallback (if configured)
]

for model in MODELS_TO_TRY:
    try:
        result = model.generate(prompt)
        if validate(result):
            return result
    except QuotaError:
        continue  # Try next model
    except APIError:
        continue
        
# Ultimate fallback: partial results
return {
    "status": "partial",
    "message": "Could not complete full analysis due to API limits. Showing extracted data only.",
    "injuries": extracted_injuries,  # From regex/NLP
    "timeline": basic_timeline,      # From dates found
}
```

### 4.3 Fact Validation
```python
def validate_facts(ai_output, source_text):
    """Cross-check AI claims against source text"""
    for claim in ai_output["injuries"]:
        if claim.lower() not in source_text.lower():
            flag_for_review(claim, confidence="LOW")
    
    # Check dates are realistic
    for event in ai_output["timeline"]:
        if event["date"] > datetime.now():
            flag_for_review(event, reason="Future date")
```

---

## 📋 **IMPLEMENTATION PRIORITY**

### Week 1: Critical Fixes
1. ✅ Full PDF processing (no truncation)
2. ✅ Context-aware chatbot (page tracking)
3. ✅ Markdown output formatting

### Week 2: Quality Improvements
4. ✅ OCR support (Gemini Vision)
5. ✅ JSON schema validation
6. ✅ Progress tracking UI

### Week 3: Reliability
7. ✅ Retry logic + fallback models
8. ✅ Confidence scores
9. ✅ Citation support

### Week 4: Polish
10. ✅ Table extraction
11. ✅ Fact validation
12. ✅ Better error messages

---

## 🎯 **SUCCESS METRICS**

### Before Improvements:
- ❌ PDF: 40 pages processed from 500-page file
- ❌ Chat: Generic responses, no context
- ❌ Output: Plain text, hard to read
- ❌ Reliability: 60% success rate

### After Improvements:
- ✅ PDF: ALL 500 pages processed + classified
- ✅ Chat: Page-aware, cites sources
- ✅ Output: Structured markdown, tables, citations
- ✅ Reliability: 95% success rate with fallbacks

---

## 🔧 **TECHNICAL CHANGES NEEDED**

### New Dependencies:
```txt
pydantic==2.5.0          # Data validation
markdown==3.5.1          # Markdown rendering
Pillow==10.1.0           # Image processing for OCR
pandas==2.1.4            # Table handling
```

### New Database Fields:
```python
# Document model
page_classifications = JSONField(default=dict)  # {1: "ADMISSION", 2: "LAB"}
page_summaries = JSONField(default=list)        # [{page: 1, summary: "..."}]
has_tables = BooleanField(default=False)
extracted_tables = JSONField(default=list)

# ChatMessage model (new)
class ChatMessage(models.Model):
    case = ForeignKey(Case)
    role = CharField(choices=[("user", "User"), ("ai", "AI")])
    content = TextField()
    page_context = JSONField()  # Where user was when asking
    sources = JSONField()        # Citations
    confidence = FloatField(null=True)
    created_at = DateTimeField(auto_now_add=True)
```

### New API Endpoints:
```python
# Track user's current page
POST /api/track-page/
  {case_id: 123, route: "/timeline", section: "visits"}

# Context-aware chat
POST /api/chat/
  {message: "...", case_id: 123, page_context: {...}}

# Progress polling
GET /api/analysis-status/<task_id>/
  → {status: "processing", progress: 45, message: "Analyzing injuries..."}
```

---

## 📝 **NEXT STEPS**

1. Review this plan
2. Prioritize which phase to start with
3. I'll implement the changes file-by-file
4. Test with real 500-page PDFs
5. Deploy improved version

**Want me to start implementing Phase 1 (Enhanced PDF Processing) now?**
