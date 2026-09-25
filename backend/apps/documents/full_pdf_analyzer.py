"""
Full PDF Multi-Pass Analyzer
Processes ALL pages in chunks, then combines results
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

CHUNK_SIZE = 100_000  # 100K chars per chunk (~80 pages)


def split_into_chunks(full_text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    """
    Split full PDF text into manageable chunks for AI processing
    
    Args:
        full_text: Complete PDF text (all 500 pages)
        chunk_size: Characters per chunk (default 100K)
    
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_len = len(full_text)
    
    while start < text_len:
        end = start + chunk_size
        
        # Try to break at paragraph boundary
        if end < text_len:
            # Look for nearest paragraph break (double newline)
            last_para = full_text.rfind('\n\n', start, end + 1000)
            if last_para > start:
                end = last_para
        
        chunk = full_text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end
    
    logger.info(f"Split {text_len:,} chars into {len(chunks)} chunks")
    return chunks


def analyze_chunk(chunk: str, chunk_number: int, total_chunks: int, ai_generate_func) -> Dict[str, Any]:
    """
    Analyze a single chunk of PDF text
    
    Returns:
        {
            "injuries": [...],
            "timeline": [...],
            "medications": [...],
            "key_findings": "...",
        }
    """
    
    prompt = f"""
You are a SENIOR INDIAN MACT ADVOCATE analyzing medical records.

This is PART {chunk_number} of {total_chunks} of a large hospital file.

Extract ONLY the key medical facts from THIS section. Be concise.

Return in this format:

**Injuries Found:**
- [List any injuries mentioned]

**Timeline Events:**
- [Date]: [Event description]

**Medications:**
- [Drug name] - [Dosage]

**Key Findings:**
[Important medical findings, test results, diagnoses]

**Critical Information:**
[Anything essential for legal case - disability %, income, etc.]

==================== MEDICAL RECORD SECTION ====================
{chunk}
"""
    
    result = ai_generate_func(prompt)
    return {
        "chunk_number": chunk_number,
        "raw_analysis": result,
    }


def combine_analyses(chunk_results: List[Dict], ai_generate_func) -> str:
    """
    Combine all chunk analyses into final comprehensive report
    
    Args:
        chunk_results: Results from each chunk analysis
        ai_generate_func: AI generation function
    
    Returns:
        Final comprehensive medical-legal report
    """
    
    # Combine all chunk results
    combined_findings = "\n\n" + "="*70 + "\n".join([
        f"\n\nSECTION {r['chunk_number']}:\n{r['raw_analysis']}"
        for r in chunk_results
    ])
    
    final_prompt = f"""
You are a SENIOR INDIAN MACT ADVOCATE preparing a final court-ready report.

You have analyzed a large medical file in multiple sections. Now create a 
comprehensive final report combining ALL findings.

Generate a PROFESSIONAL legal medical report in CLEAN STRUCTURED FORMAT.

FORMATTING RULES:
- Use ## for main section headings
- Use ### for subheadings  
- Use numbered lists (1., 2., 3.) for sequences
- Use bullet points (-) for items
- Write clear paragraphs
- Use **bold** for important terms
- NO EMOJIS - professional tone
- Use tables for financial data

Generate EXACTLY these 8 sections:

## 1. Medical Chronology
[Complete timeline from admission to discharge, combining all sections]

## 2. Injuries Identified
[All injuries from all sections, categorized by severity]

## 3. Treatment Summary
[All treatments, surgeries, medications across entire hospitalization]

## 4. Financial and Compensation Analysis
[All medical expenses, future costs, income loss]

## 5. Claim Heads Under Motor Vehicles Act, 1988
[Calculate compensation based on ALL findings]

## 6. Missing Documents Checklist
[Documents needed but not found in file]

## 7. Relevant Legal Provisions
[Applicable sections and precedents]

## 8. Legal Strategy and Recommendations
[Case strength, recommendations based on COMPLETE file]

==================== ALL MEDICAL SECTIONS ====================
{combined_findings}
"""
    
    return ai_generate_func(final_prompt)


def analyze_full_pdf(full_text: str, ai_generate_func, show_progress=True) -> Dict[str, Any]:
    """
    Multi-pass analysis of complete PDF
    
    Args:
        full_text: Complete PDF text (all pages)
        ai_generate_func: Function to call AI
        show_progress: Whether to log progress
    
    Returns:
        {
            "success": bool,
            "chunks_processed": int,
            "final_report": str,
            "chunk_analyses": [...],
        }
    """
    
    try:
        # Step 1: Split into chunks
        chunks = split_into_chunks(full_text)
        
        if show_progress:
            logger.info(f"📄 Processing {len(chunks)} chunks (~{len(full_text):,} chars total)")
        
        # Step 2: Analyze each chunk
        chunk_results = []
        for i, chunk in enumerate(chunks, 1):
            if show_progress:
                logger.info(f"🔍 Analyzing chunk {i}/{len(chunks)}")
            
            result = analyze_chunk(chunk, i, len(chunks), ai_generate_func)
            chunk_results.append(result)
        
        # Step 3: Combine all results
        if show_progress:
            logger.info(f"🔄 Combining all {len(chunks)} sections into final report...")
        
        final_report = combine_analyses(chunk_results, ai_generate_func)
        
        if show_progress:
            logger.info(f"✅ Full PDF analysis complete!")
        
        return {
            "success": True,
            "chunks_processed": len(chunks),
            "final_report": final_report,
            "chunk_analyses": chunk_results,
            "total_chars_processed": len(full_text),
        }
        
    except Exception as e:
        logger.exception("Full PDF analysis failed")
        return {
            "success": False,
            "error": str(e),
        }


def quick_analysis_vs_full_analysis(full_text: str) -> Dict[str, Any]:
    """
    Determine whether to use quick (80-page) or full (all-page) analysis
    
    Rules:
    - If file < 50 pages: Use all pages (quick)
    - If file 50-200 pages: Use smart selection (current method)
    - If file > 200 pages: Use multi-pass (full analysis)
    
    Returns:
        {
            "method": "quick" | "smart" | "full",
            "reason": "...",
            "estimated_time": seconds,
            "api_calls": int,
        }
    """
    
    # Estimate page count (rough: 2000 chars per page average)
    estimated_pages = len(full_text) // 2000
    
    if estimated_pages < 50:
        return {
            "method": "quick",
            "reason": "Small file - process all pages in one call",
            "estimated_time": 30,
            "api_calls": 1,
        }
    elif estimated_pages < 200:
        return {
            "method": "smart",
            "reason": "Medium file - use smart page selection (current method)",
            "estimated_time": 30,
            "api_calls": 1,
        }
    else:
        chunks_needed = (len(full_text) // CHUNK_SIZE) + 1
        return {
            "method": "full",
            "reason": f"Large file ({estimated_pages} pages) - use multi-pass analysis",
            "estimated_time": 30 + (chunks_needed * 20),  # 20s per chunk
            "api_calls": chunks_needed + 1,  # chunk analyses + final combination
        }
