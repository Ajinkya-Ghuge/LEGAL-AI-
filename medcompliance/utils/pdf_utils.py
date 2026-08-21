"""PDF extraction — reused from backend/apps/documents/services.py"""
import os

def extract_pdf_text(file_path: str, max_chars: int = 50000) -> str:
    try:
        import fitz
        doc = fitz.open(file_path)
        text = "\n\n".join(page.get_text().strip() for page in doc if page.get_text().strip())
        doc.close()
        return text[:max_chars]
    except ImportError:
        return ""
    except Exception as e:
        return f"[PDF read error: {e}]"


def load_vault_knowledge(vault_path: str, max_chars: int = 8000) -> str:
    """Load all PDFs from vault as compliance knowledge base."""
    if not os.path.exists(vault_path):
        return ""
    knowledge = ""
    try:
        import fitz
        for root, _, files in os.walk(vault_path):
            for f in files:
                if f.endswith(".pdf"):
                    try:
                        full = os.path.join(root, f)
                        doc = fitz.open(full)
                        text = "".join(p.get_text() for p in doc)[:2000]
                        doc.close()
                        knowledge += f"\n\n=== SOURCE: {f} ===\n{text}"
                    except Exception:
                        pass
    except ImportError:
        pass
    return knowledge[:max_chars]
