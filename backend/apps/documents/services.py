"""
Document processing services.
PDF text extraction via PyMuPDF (fitz).
Handles large files (1000+ pages) with smart chunking.
"""
import logging
import os
import re

logger = logging.getLogger(__name__)

# ── Limits ────────────────────────────────────────────────────────────────────
MAX_FULL_TEXT_CHARS  = 500_000   # Store up to 500K chars in DB (~400 pages)
MAX_AI_CHARS         = 50_000    # Send up to 50K chars to Gemini (~40 pages)
MAX_PAGE_TEXTS_STORE = 200       # Store page-by-page for first 200 pages

# Keywords that indicate medically/legally relevant pages
RELEVANT_KEYWORDS = [
    "admission", "discharge", "diagnosis", "injury", "fracture", "surgery",
    "operation", "treatment", "medicine", "prescription", "hospital", "doctor",
    "accident", "police", "fir", "insurance", "claim", "compensation",
    "income", "salary", "disability", "certificate", "report", "mri", "xray",
    "x-ray", "scan", "blood", "test", "result", "patient", "ward", "icu",
    "emergency", "ortho", "neuro", "physiotherapy", "rehabilitation",
    "section 166", "motor vehicle", "mact", "tribunal", "petitioner",
]


def extract_pdf(file_path: str) -> dict:
    """
    Extract text from a PDF file page by page.
    Handles large files gracefully — stores all pages but caps DB storage.

    Returns:
        {
            "success":    bool,
            "pages":      int,       # total pages in PDF
            "full_text":  str,       # capped at MAX_FULL_TEXT_CHARS
            "page_texts": list,      # first MAX_PAGE_TEXTS_STORE pages
            "smart_text": str,       # best pages for AI (MAX_AI_CHARS)
            "error":      str
        }
    """
    try:
        import fitz
    except ImportError:
        return _fail("PyMuPDF not installed. Run: pip install PyMuPDF")

    if not os.path.exists(file_path):
        return _fail(f"File not found: {file_path}")

    try:
        doc        = fitz.open(file_path)
        total_pages = len(doc)
        page_texts  = []
        full_parts  = []

        logger.info("Extracting %d pages from %s", total_pages, file_path)

        for i, page in enumerate(doc, start=1):
            text = page.get_text().strip()
            if not text:
                continue

            full_parts.append(text)

            # Store page-by-page only for first N pages (DB size control)
            if i <= MAX_PAGE_TEXTS_STORE:
                page_texts.append({"page": i, "text": text})

        doc.close()

        full_text  = "\n\n".join(full_parts)
        smart_text = _smart_extract(full_parts, total_pages)

        logger.info(
            "Extracted %d pages, %d chars total, %d chars smart from %s",
            total_pages, len(full_text), len(smart_text), file_path
        )

        return {
            "success":    True,
            "pages":      total_pages,
            "full_text":  full_text[:MAX_FULL_TEXT_CHARS],
            "page_texts": page_texts,
            "smart_text": smart_text,
        }

    except Exception as exc:
        logger.exception("PDF extraction failed for %s", file_path)
        return _fail(str(exc))


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
