"""
PDF Source Viewer - Extract and highlight specific text from PDFs
"""
import fitz  # PyMuPDF
import json
from typing import Dict, List, Tuple, Optional


class PDFSourceViewer:
    """
    Extract PDF content and locate specific text for source verification.
    """
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = None
        
    def __enter__(self):
        self.doc = fitz.open(self.pdf_path)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.doc:
            self.doc.close()
    
    def find_text_location(self, search_text: str, page_num: Optional[int] = None) -> List[Dict]:
        """
        Find all occurrences of text in the PDF.
        
        Args:
            search_text: Text to search for
            page_num: Specific page to search (0-indexed), or None to search all pages
            
        Returns:
            List of dicts with {page, coordinates, context}
        """
        results = []
        
        pages_to_search = [page_num] if page_num is not None else range(len(self.doc))
        
        for page_idx in pages_to_search:
            if page_idx >= len(self.doc):
                continue
                
            page = self.doc[page_idx]
            text_instances = page.search_for(search_text)
            
            for rect in text_instances:
                # Get surrounding context (50 chars before and after)
                full_text = page.get_text()
                text_pos = full_text.find(search_text)
                
                context_start = max(0, text_pos - 50)
                context_end = min(len(full_text), text_pos + len(search_text) + 50)
                context = full_text[context_start:context_end].strip()
                
                results.append({
                    'page': page_idx + 1,  # Convert to 1-indexed for display
                    'page_zero_indexed': page_idx,
                    'coordinates': {
                        'x0': rect.x0,
                        'y0': rect.y0,
                        'x1': rect.x1,
                        'y1': rect.y1,
                    },
                    'context': context,
                    'matched_text': search_text
                })
        
        return results
    
    def get_page_content(self, page_num: int) -> Dict:
        """
        Get full content of a specific page.
        
        Args:
            page_num: Page number (1-indexed)
            
        Returns:
            Dict with page text and metadata
        """
        if page_num < 1 or page_num > len(self.doc):
            return {'error': 'Invalid page number'}
        
        page = self.doc[page_num - 1]
        
        return {
            'page': page_num,
            'text': page.get_text(),
            'width': page.rect.width,
            'height': page.rect.height,
            'total_pages': len(self.doc)
        }
    
    def highlight_text_on_page(self, page_num: int, search_text: str) -> Optional[bytes]:
        """
        Create a highlighted version of a page with text highlighted.
        
        Args:
            page_num: Page number (1-indexed)
            search_text: Text to highlight
            
        Returns:
            PDF bytes of the highlighted page, or None if not found
        """
        if page_num < 1 or page_num > len(self.doc):
            return None
        
        page = self.doc[page_num - 1]
        text_instances = page.search_for(search_text)
        
        # Create new PDF with just this page
        new_doc = fitz.open()
        new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
        
        # Copy original page content
        new_page.show_pdf_page(new_page.rect, self.doc, page_num - 1)
        
        # Add yellow highlights
        for rect in text_instances:
            highlight = new_page.add_highlight_annot(rect)
            highlight.set_colors(stroke=(1, 1, 0))  # Yellow
            highlight.update()
        
        # Return PDF bytes
        pdf_bytes = new_doc.tobytes()
        new_doc.close()
        
        return pdf_bytes
    
    def extract_snippet_with_context(self, page_num: int, snippet: str, 
                                     context_lines: int = 2) -> Dict:
        """
        Extract a snippet with surrounding context lines.
        
        Args:
            page_num: Page number (1-indexed)
            snippet: Text snippet to find
            context_lines: Number of lines before/after to include
            
        Returns:
            Dict with snippet, context, and location info
        """
        if page_num < 1 or page_num > len(self.doc):
            return {'error': 'Invalid page number'}
        
        page = self.doc[page_num - 1]
        full_text = page.get_text()
        
        # Find snippet in text
        snippet_pos = full_text.find(snippet)
        if snippet_pos == -1:
            return {'error': 'Snippet not found on page'}
        
        # Split into lines
        lines = full_text.split('\n')
        
        # Find which line contains the snippet
        current_pos = 0
        snippet_line_idx = -1
        
        for idx, line in enumerate(lines):
            if current_pos <= snippet_pos < current_pos + len(line):
                snippet_line_idx = idx
                break
            current_pos += len(line) + 1  # +1 for newline
        
        if snippet_line_idx == -1:
            snippet_line_idx = 0
        
        # Extract context
        start_line = max(0, snippet_line_idx - context_lines)
        end_line = min(len(lines), snippet_line_idx + context_lines + 1)
        
        context_lines_text = lines[start_line:end_line]
        
        return {
            'page': page_num,
            'snippet': snippet,
            'context': '\n'.join(context_lines_text),
            'line_number': snippet_line_idx + 1,
            'total_lines': len(lines)
        }


def find_text_in_pdf(pdf_path: str, search_text: str, page_num: Optional[int] = None) -> List[Dict]:
    """
    Convenience function to find text in PDF.
    
    Args:
        pdf_path: Path to PDF file
        search_text: Text to search for
        page_num: Optional specific page (1-indexed)
        
    Returns:
        List of matches with location info
    """
    with PDFSourceViewer(pdf_path) as viewer:
        # Convert page_num to 0-indexed if provided
        page_idx = (page_num - 1) if page_num is not None else None
        return viewer.find_text_location(search_text, page_idx)


def get_page_with_highlight(pdf_path: str, page_num: int, search_text: str) -> Optional[bytes]:
    """
    Get a PDF page with highlighted text.
    
    Args:
        pdf_path: Path to PDF file
        page_num: Page number (1-indexed)
        search_text: Text to highlight
        
    Returns:
        PDF bytes with highlights
    """
    with PDFSourceViewer(pdf_path) as viewer:
        return viewer.highlight_text_on_page(page_num, search_text)
