"""
Markdown to Structured HTML Formatter
Converts AI-generated markdown reports into clean, professional HTML
"""
import re


def format_medical_report(text: str) -> str:
    """
    Convert markdown medical report to beautiful structured HTML.
    Handles ## headings, ** bold, lists, and tables.
    """
    if not text:
        return ""
    
    html_parts = []
    lines = text.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Main heading (## )
        if line.startswith('## '):
            title = line[3:].strip()
            # Remove any numbering (e.g., "## 1. Medical Chronology" -> "Medical Chronology")
            title = re.sub(r'^\d+\.\s*', '', title)
            
            html_parts.append(f'''
            <div class="report-section mb-6">
                <div class="flex items-center gap-3 mb-4 pb-3 border-b-2 border-primary">
                    <div class="w-8 h-8 bg-primary text-white rounded-lg flex items-center justify-center font-bold text-sm">
                        {len(html_parts) + 1}
                    </div>
                    <h3 class="text-xl font-bold text-gray-900">{title}</h3>
                </div>
                <div class="space-y-3">
            ''')
            i += 1
            continue
        
        # Subheading (### or **Title:**)
        if line.startswith('### ') or (line.startswith('**') and line.endswith(':**')):
            if line.startswith('### '):
                subtitle = line[4:].strip()
            else:
                subtitle = line.replace('**', '').replace(':', '').strip()
            
            html_parts.append(f'''
                <div class="mt-4">
                    <h4 class="text-base font-bold text-gray-800 mb-2 flex items-center gap-2">
                        <svg class="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                        </svg>
                        {subtitle}
                    </h4>
            ''')
            i += 1
            continue
        
        # Table detection (lines with | )
        if '|' in line and i + 1 < len(lines) and '|' in lines[i + 1]:
            table_lines = [line]
            j = i + 1
            while j < len(lines) and '|' in lines[j]:
                table_lines.append(lines[j])
                j += 1
            
            html_parts.append(format_table(table_lines))
            i = j
            continue
        
        # Numbered list item (1., 2., etc.)
        if re.match(r'^\d+\.\s+', line):
            html_parts.append('<div class="space-y-2">')
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i].strip()):
                item = re.sub(r'^\d+\.\s+', '', lines[i].strip())
                item = format_inline(item)
                html_parts.append(f'''
                    <div class="flex items-start gap-3 p-3 bg-gray-50 rounded-lg border-l-4 border-primary">
                        <span class="text-primary font-bold text-sm mt-0.5">•</span>
                        <p class="text-gray-700 text-sm leading-relaxed flex-1">{item}</p>
                    </div>
                ''')
                i += 1
            html_parts.append('</div>')
            continue
        
        # Bullet list item (- or *)
        if line.startswith('- ') or line.startswith('* '):
            html_parts.append('<div class="space-y-2 ml-4">')
            while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                item = lines[i].strip()[2:].strip()
                item = format_inline(item)
                html_parts.append(f'''
                    <div class="flex items-start gap-2">
                        <span class="text-primary font-bold mt-1">•</span>
                        <p class="text-gray-700 text-sm leading-relaxed">{item}</p>
                    </div>
                ''')
                i += 1
            html_parts.append('</div>')
            continue
        
        # Regular paragraph
        para = format_inline(line)
        html_parts.append(f'<p class="text-gray-700 leading-relaxed mb-3">{para}</p>')
        i += 1
    
    # Close any open section
    if html_parts and '<div class="report-section' in ''.join(html_parts[-5:]):
        html_parts.append('</div></div>')
    
    return '\n'.join(html_parts)


def format_inline(text: str) -> str:
    """Format inline markdown: **bold**, ++highlight++"""
    # Bold (**text**)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong class="font-bold text-gray-900">\1</strong>', text)
    
    # Highlight (++text++)
    text = re.sub(r'\+\+(.+?)\+\+', r'<mark class="bg-yellow-100 px-1 rounded font-semibold">\1</mark>', text)
    
    # NOT FOUND special handling
    text = text.replace('NOT FOUND', '<span class="text-red-600 font-semibold">NOT FOUND</span>')
    
    return text


def format_table(lines: list) -> str:
    """Convert markdown table to HTML table"""
    if len(lines) < 2:
        return ''
    
    # Parse header
    headers = [h.strip() for h in lines[0].split('|') if h.strip()]
    
    # Skip separator line (---|---|---)
    # Parse rows
    rows = []
    for line in lines[2:]:
        if not line.strip():
            continue
        cells = [c.strip() for c in line.split('|') if c.strip()]
        if cells:
            rows.append(cells)
    
    # Build HTML table
    html = '''
    <div class="overflow-x-auto my-4">
        <table class="w-full border-collapse bg-white rounded-lg overflow-hidden shadow-sm">
            <thead class="bg-gradient-to-r from-primary/10 to-primary/5">
                <tr>
    '''
    
    for header in headers:
        html += f'<th class="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider border-b-2 border-primary/20">{header}</th>'
    
    html += '</tr></thead><tbody class="divide-y divide-gray-100">'
    
    for row in rows:
        html += '<tr class="hover:bg-gray-50 transition-colors">'
        for cell in row:
            formatted_cell = format_inline(cell)
            html += f'<td class="px-4 py-3 text-sm text-gray-700">{formatted_cell}</td>'
        html += '</tr>'
    
    html += '</tbody></table></div>'
    
    return html


def extract_sections(text: str) -> dict:
    """
    Extract different sections from medical report.
    Returns dict with section titles as keys and content as values.
    """
    sections = {}
    current_section = None
    current_content = []
    
    for line in text.split('\n'):
        if line.startswith('## '):
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            
            # Start new section
            current_section = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return sections


def format_report_for_display(text: str) -> dict:
    """
    Format a medical report and return structured data for template.
    Returns sections with formatted HTML content.
    """
    sections_dict = extract_sections(text)
    formatted = {}
    
    for title, content in sections_dict.items():
        formatted[title] = format_medical_report(content)
    
    return formatted
