"""
Document processing services.
PDF text extraction via PyMuPDF (fitz).
Handles large files (1000+ pages) with smart chunking.
✅ ENHANCED: Now processes ALL pages with intelligent classification
"""
import logging
import os
import re

logger = logging.getLogger(__name__)

# ── Limits ────────────────────────────────────────────────────────────────────
MAX_FULL_TEXT_CHARS  = 2_000_000  # Store up to 2M chars in DB (~1600 pages) ✅ INCREASED
MAX_AI_CHARS         = 100_000    # Send up to 100K chars to Gemini (~80 pages) ✅ DOUBLED
MAX_PAGE_TEXTS_STORE = 500        # Store page-by-page for first 500 pages ✅ INCREASED

# Keywords that indicate medically/legally relevant pages
RELEVANT_KEYWORDS = [
    "admission", "discharge", "diagnosis", "injury", "fracture", "surgery",
    "operation", "treatment", "medicine", "prescription", "hospital", "doctor",
    "accident", "police", "fir", "insurance", "claim", "compensation",
    "income", "salary", "disability", "certificate", "report", "mri", "xray",
    "x-ray", "scan", "blood", "test", "result", "patient", "ward", "icu",
    "emergency", "ortho", "neuro", "physiotherapy", "rehabilitation",
    "section 166", "motor vehicle", "mact", "tribunal", "petitioner",
    # ✅ Added more medical terms
    "radiology", "pathology", "biopsy", "medication", "dosage", "anesthesia",
    "post-operative", "recovery", "complications", "follow-up", "consultation",
    "referral", "specialist", "surgeon", "physician", "nurse", "symptoms",
    "pain", "swelling", "bleeding", "infection", "wound", "dressing",
]

# Page type classification keywords
PAGE_TYPE_KEYWORDS = {
    "ADMISSION": ["admitted", "admission", "presenting complaints", "history of present illness"],
    "DISCHARGE": ["discharge summary", "final diagnosis", "condition at discharge", "discharge date"],
    "SURGERY": ["operative notes", "procedure performed", "surgeon", "anesthesia", "operation theatre"],
    "LAB_RESULTS": ["laboratory", "blood test", "urine test", "pathology", "report", "values", "normal range"],
    "RADIOLOGY": ["x-ray", "xray", "mri", "ct scan", "ultrasound", "radiology", "imaging"],
    "PRESCRIPTION": ["prescribed", "medication", "drug", "dosage", "rx", "pharmacy"],
    "CONSULTATION": ["consultation", "specialist opinion", "referred to", "opd", "out-patient"],
}


def extract_pdf(file_path: str) -> dict:
    """
    Extract text from a PDF file page by page.
    Handles large files gracefully — stores all pages but caps DB storage.

    Returns:
        {
            "success":    bool,
            "pages":      int,       # total pages in PDF
            "full_text":  str,       # capped at MAX_FULL_TEXT_CHARS
            "page_texts": list,      # first MAX_PAGE_TEXTS_STORE pages with classification
            "smart_text": str,       # best pages for AI (MAX_AI_CHARS)
            "page_types": dict,      # Count of each page type found
            "error":      str
        }
    """
    # Use enhanced version
    return extract_pdf_enhanced(file_path)


def _fail(error: str) -> dict:
    return {
        "success":    False,
        "pages":      0,
        "full_text":  "",
        "page_texts": [],
        "smart_text": "",
        "error":      error,
    }


def _smart_extract(page_texts: list, total_pages: int) -> str:
    """
    For large PDFs, intelligently select the most relevant pages
    instead of just taking the first N characters.

    Strategy:
    1. Always include first 10 pages (cover, admission, FIR)
    2. Always include last 5 pages (discharge summary, final report)
    3. Score remaining pages by keyword relevance
    4. Fill remaining budget with highest-scoring pages
    """
    if not page_texts:
        return ""

    # For small PDFs — just return everything
    full = "\n\n".join(page_texts)
    if len(full) <= MAX_AI_CHARS:
        return full

    budget      = MAX_AI_CHARS
    selected    = []
    used_chars  = 0
    n           = len(page_texts)

    # Always take first 10 pages
    first_pages = page_texts[:min(10, n)]
    for text in first_pages:
        if used_chars + len(text) <= budget * 0.4:  # max 40% budget for first pages
            selected.append(text)
            used_chars += len(text)

    # Always take last 5 pages (discharge summary etc.)
    last_pages = page_texts[max(0, n - 5):]
    for text in last_pages:
        if used_chars + len(text) <= budget * 0.6:
            if text not in selected:
                selected.append(text)
                used_chars += len(text)

    # Score middle pages by keyword relevance
    middle_pages = page_texts[min(10, n):max(0, n - 5)]
    scored = []
    for text in middle_pages:
        if text in selected:
            continue
        score = _relevance_score(text)
        scored.append((score, text))

    # Sort by relevance, take highest scoring until budget full
    scored.sort(key=lambda x: x[0], reverse=True)
    for score, text in scored:
        if score == 0:
            break  # no relevant keywords, skip
        if used_chars + len(text) > budget:
            break
        selected.append(text)
        used_chars += len(text)

    result = "\n\n".join(selected)

    # Add summary note if we truncated
    if total_pages > n or len(full) > MAX_AI_CHARS:
        note = (
            f"\n\n[NOTE: Document has {total_pages} pages total. "
            f"Showing {len(selected)} most relevant pages for analysis. "
            f"Full text stored in database.]"
        )
        result += note

    return result


def _smart_extract_v2(page_data: list, all_texts: list, total_pages: int) -> str:
    """
    ✅ ENHANCED: Prioritize by page type, not just keywords
    
    Priority order:
    1. DISCHARGE summaries (most important!)
    2. SURGERY notes
    3. ADMISSION notes
    4. LAB_RESULTS & RADIOLOGY
    5. CONSULTATION notes
    6. High-relevance OTHER pages
    """
    if not page_data:
        return "\n\n".join(all_texts)[:MAX_AI_CHARS]
    
    budget = MAX_AI_CHARS
    selected = []
    used_chars = 0
    
    # Priority order for page types
    PRIORITY_TYPES = [
        "DISCHARGE",     # Most important
        "SURGERY",
        "ADMISSION",
        "LAB_RESULTS",
        "RADIOLOGY",
        "PRESCRIPTION",
        "CONSULTATION",
    ]
    
    # Collect pages by type
    pages_by_type = {}
    for page in page_data:
        ptype = page.get("type", "OTHER")
        if ptype not in pages_by_type:
            pages_by_type[ptype] = []
        pages_by_type[ptype].append(page)
    
    # Add pages in priority order
    for ptype in PRIORITY_TYPES:
        if ptype not in pages_by_type:
            continue
        
        for page in pages_by_type[ptype]:
            text = page["text"]
            if used_chars + len(text) > budget:
                break
            selected.append(f"[Page {page['page']} - {ptype}]\n{text}")
            used_chars += len(text)
    
    # Add high-relevance OTHER pages if budget remaining
    if "OTHER" in pages_by_type:
        other_pages = sorted(pages_by_type["OTHER"], key=lambda p: p.get("relevance", 0), reverse=True)
        for page in other_pages:
            if used_chars + len(page["text"]) > budget:
                break
            selected.append(f"[Page {page['page']}]\n{page['text']}")
            used_chars += len(page["text"])
    
    result = "\n\n".join(selected)
    
    # Add helpful summary
    types_found = list(pages_by_type.keys())
    note = (
        f"\n\n[📊 DOCUMENT SUMMARY: {total_pages} total pages. "
        f"Page types found: {', '.join(types_found)}. "
        f"Selected {len(selected)} most critical pages for AI analysis.]"
    )
    result += note
    
    return result


def _relevance_score(text: str) -> int:
    """Score a page by how many legal/medical keywords it contains."""
    text_lower = text.lower()
    score = 0
    for keyword in RELEVANT_KEYWORDS:
        if keyword in text_lower:
            score += 1
    # Bonus for pages with numbers (dates, amounts, measurements)
    if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text):  # dates
        score += 2
    if re.search(r'₹\s*[\d,]+', text):  # rupee amounts
        score += 3
    if re.search(r'\d+\s*%', text):  # percentages (disability %)
        score += 2
    return score


def classify_page_type(text: str) -> str:
    """
    Classify what type of medical/legal page this is
    Returns: ADMISSION, DISCHARGE, SURGERY, LAB_RESULTS, RADIOLOGY, PRESCRIPTION, CONSULTATION, OTHER
    """
    text_lower = text.lower()
    scores = {}
    
    for page_type, keywords in PAGE_TYPE_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            scores[page_type] = score
    
    if not scores:
        return "OTHER"
    
    # Return page type with highest score
    return max(scores, key=scores.get)


def extract_pdf_enhanced(file_path: str) -> dict:
    """
    ✅ ENHANCED: Extract ALL pages with classification
    Returns full text + page classifications + smart summary
    """
    try:
        import fitz
    except ImportError:
        return _fail("PyMuPDF not installed. Run: pip install PyMuPDF")

    if not os.path.exists(file_path):
        return _fail(f"File not found: {file_path}")

    try:
        doc = fitz.open(file_path)
        total_pages = len(doc)
        page_data = []
        full_parts = []
        
        # Track page types found
        page_types_count = {}

        logger.info("🔍 Extracting ALL %d pages from %s", total_pages, file_path)

        for i, page in enumerate(doc, start=1):
            text = page.get_text().strip()
            if not text:
                continue

            full_parts.append(text)
            
            # Classify page type
            page_type = classify_page_type(text)
            page_types_count[page_type] = page_types_count.get(page_type, 0) + 1
            
            # Store page data (all pages now, not just first 200)
            if i <= MAX_PAGE_TEXTS_STORE:
                page_data.append({
                    "page": i,
                    "text": text,
                    "type": page_type,
                    "relevance": _relevance_score(text),
                })

        doc.close()

        full_text = "\n\n".join(full_parts)
        smart_text = _smart_extract_v2(page_data, full_parts, total_pages)

        logger.info(
            "✅ Extracted %d pages (%s), %d chars total, %d chars for AI from %s",
            total_pages, dict(page_types_count), len(full_text), len(smart_text), file_path
        )

        return {
            "success": True,
            "pages": total_pages,
            "full_text": full_text[:MAX_FULL_TEXT_CHARS],
            "page_texts": page_data,
            "smart_text": smart_text,
            "page_types": page_types_count,  # ✅ NEW: Summary of page types found
        }

    except Exception as exc:
        logger.exception("PDF extraction failed for %s", file_path)
        return _fail(str(exc))


def extract_text_for_ai(file_path: str, max_chars: int = MAX_AI_CHARS) -> str:
    """
    Extract text optimized for AI consumption.
    Uses smart extraction for large files.
    """
    result = extract_pdf(file_path)
    if result["success"]:
        smart = result.get("smart_text", "")
        if smart:
            return smart[:max_chars]
        return result["full_text"][:max_chars]
    return ""


def extract_text_preview(file_path: str, max_chars: int = 5000) -> str:
    """Quick text preview — returns first max_chars characters."""
    result = extract_pdf(file_path)
    if result["success"]:
        return result["full_text"][:max_chars]
    return ""
