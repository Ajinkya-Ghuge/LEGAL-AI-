"""
AI Output Formatters
Converts raw AI text into structured, readable formats
"""
import re
import markdown
from typing import Dict, List, Any


def format_medical_analysis(raw_text: str) -> Dict[str, Any]:
    """
    Convert raw AI medical analysis into structured sections with markdown
    
    Returns:
        {
            "sections": [
                {"title": "Medical Chronology", "content": "...", "icon": "calendar"},
                {"title": "Injuries Identified", "content": "...", "icon": "alert"},
                ...
            ],
            "summary": "Quick overview...",
            "html": "Full HTML rendered output"
        }
    """
    
    # Define section patterns and their icons
    SECTION_PATTERNS = {
        "Medical Chronology": {"icon": "calendar", "color": "blue"},
        "Injuries Identified": {"icon": "alert-circle", "color": "red"},
        "Treatment Summary": {"icon": "activity", "color": "green"},
        "Financial & Compensation": {"icon": "dollar-sign", "color": "yellow"},
        "Claim Heads": {"icon": "file-text", "color": "purple"},
        "Missing Documents": {"icon": "clipboard", "color": "orange"},
        "Legal Sections": {"icon": "book", "color": "indigo"},
        "Lawyer Insights": {"icon": "lightbulb", "color": "pink"},
    }
    
    sections = []
    current_section = None
    current_content = []
    
    # Split by lines and identify sections
    lines = raw_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this line is a section header
        is_header = False
        for section_name in SECTION_PATTERNS.keys():
            if section_name.lower() in line.lower() and (
                line.startswith('#') or 
                line.endswith(':') or 
                line.isupper() or
                re.match(r'^\d+\)', line)
            ):
                # Save previous section
                if current_section:
                    sections.append({
                        "title": current_section,
                        "content": '\n'.join(current_content),
                        "icon": SECTION_PATTERNS[current_section]["icon"],
                        "color": SECTION_PATTERNS[current_section]["color"],
                    })
                
                # Start new section
                current_section = section_name
                current_content = []
                is_header = True
                break
        
        if not is_header and current_section:
            current_content.append(line)
    
    # Save last section
    if current_section:
        sections.append({
            "title": current_section,
            "content": '\n'.join(current_content),
            "icon": SECTION_PATTERNS[current_section]["icon"],
            "color": SECTION_PATTERNS[current_section]["color"],
        })
    
    # If no sections found, treat entire text as single section
    if not sections:
        sections = [{
            "title": "Analysis Report",
            "content": raw_text,
            "icon": "file-text",
            "color": "gray",
        }]
    
    # Convert content to markdown and then HTML
    for section in sections:
        # Clean up content
        content = section["content"]
        
        # Convert markdown to HTML
        html_content = markdown.markdown(
            content,
            extensions=['tables', 'fenced_code', 'nl2br']
        )
        section["html"] = html_content
        section["markdown"] = content
    
    # Generate quick summary (first 3 sentences)
    summary_sentences = []
    for section in sections[:3]:  # First 3 sections
        text = section["content"]
        # Extract first sentence
        match = re.search(r'^[^.!?]+[.!?]', text)
        if match:
            summary_sentences.append(match.group(0).strip())
    
    summary = ' '.join(summary_sentences[:2])  # Max 2 sentences
    
    return {
        "sections": sections,
        "summary": summary or "Medical analysis complete.",
        "total_sections": len(sections),
    }


def format_draft_content(raw_text: str, draft_type: str) -> Dict[str, Any]:
    """
    Format legal draft with proper structure
    
    Returns formatted draft with sections, numbering, proper legal formatting
    """
    
    # Legal document templates
    DRAFT_STRUCTURES = {
        "CLAIM_PETITION": {
            "sections": ["Title", "Petitioner Details", "Respondent Details", 
                        "Facts", "Cause of Action", "Valuation", "Prayer", "Verification"],
            "numbering": "arabic",  # 1, 2, 3
        },
        "LEGAL_NOTICE": {
            "sections": ["Header", "To", "Subject", "Facts", "Demand", "Legal Consequences"],
            "numbering": "none",
        },
        "AFFIDAVIT": {
            "sections": ["Title", "Deponent Details", "Affirmation", "Facts", "Verification"],
            "numbering": "arabic",
        },
    }
    
    structure = DRAFT_STRUCTURES.get(draft_type, DRAFT_STRUCTURES["CLAIM_PETITION"])
    
    # Add proper legal formatting
    formatted = f"""
<div class="legal-document">
    <style>
        .legal-document {{
            font-family: 'Times New Roman', Times, serif;
            line-height: 2;
            padding: 2rem;
        }}
        .legal-title {{
            text-align: center;
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 2rem;
            text-transform: uppercase;
        }}
        .legal-section {{
            margin: 1.5rem 0;
        }}
        .legal-heading {{
            font-weight: bold;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }}
        .legal-paragraph {{
            text-align: justify;
            text-indent: 2rem;
            margin: 0.5rem 0;
        }}
        .legal-list {{
            margin-left: 3rem;
        }}
    </style>
    {raw_text}
</div>
"""
    
    return {
        "formatted_html": formatted,
        "structure": structure,
        "preview": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text,
    }


def add_citations(text: str, sources: List[Dict]) -> str:
    """
    Add citation markers to text
    
    Args:
        text: Raw text
        sources: [{"claim": "...", "source": "file.pdf:12"}]
    
    Returns:
        Text with [1], [2] markers and footnotes
    """
    footnotes = []
    for i, source in enumerate(sources, 1):
        footnote = f"[{i}] {source['source']}"
        footnotes.append(footnote)
    
    if footnotes:
        citations_section = "\n\n---\n### Sources:\n" + "\n".join(footnotes)
        text += citations_section
    
    return text


def format_timeline_event(event: Dict) -> str:
    """Format a timeline event with icons and structure"""
    
    TAG_ICONS = {
        "EMERGENCY": "🚨",
        "SURGERY": "🔪",
        "SPECIALIST": "👨‍⚕️",
        "DISCHARGE": "🏠",
        "FOLLOW_UP": "📋",
        "PHYSIOTHERAPY": "🏋️",
        "LAB": "🧪",
    }
    
    icon = TAG_ICONS.get(event.get("tag", "OTHER"), "📌")
    
    formatted = f"""
    {icon} **{event['facility']}**
    📅 {event['date']}
    👨‍⚕️ Dr. {event.get('doctor', 'Not specified')}
    
    {event.get('description', '')}
    """
    
    if event.get('medications'):
        formatted += "\n\n💊 **Medications:**\n"
        for med in event['medications']:
            formatted += f"- {med}\n"
    
    return formatted.strip()


def beautify_compensation_table(data: Dict) -> str:
    """Create a beautiful HTML table for compensation breakdown"""
    
    html = """
    <table class="compensation-table">
        <thead>
            <tr>
                <th>Claim Head</th>
                <th>Amount (₹)</th>
                <th>Basis</th>
            </tr>
        </thead>
        <tbody>
    """
    
    heads = data.get('heads', [])
    for head in heads:
        html += f"""
            <tr>
                <td><strong>{head['name']}</strong></td>
                <td class="amount">₹ {head['amount']:,}</td>
                <td>{head.get('basis', 'As per law')}</td>
            </tr>
        """
    
    total = sum(h['amount'] for h in heads)
    html += f"""
        </tbody>
        <tfoot>
            <tr class="total-row">
                <td><strong>TOTAL CLAIM</strong></td>
                <td class="amount"><strong>₹ {total:,}</strong></td>
                <td></td>
            </tr>
        </tfoot>
    </table>
    
    <style>
        .compensation-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }}
        .compensation-table th {{
            background: #7B2C2C;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        .compensation-table td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        .compensation-table .amount {{
            text-align: right;
            font-family: monospace;
            font-weight: 600;
        }}
        .total-row {{
            background: #f5f5f5;
            font-size: 1.1em;
        }}
    </style>
    """
    
    return html
