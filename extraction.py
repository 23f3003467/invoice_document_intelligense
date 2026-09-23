"""
Step 1: Ingestion.
Turn a PDF into raw text. Two paths:
  - text-based PDF -> pypdf pulls text directly (fast, cheap, accurate)
  - scanned/image PDF -> falls back to OCR (slower, less accurate)

This split is the single most useful lesson of this stage: real documents
are rarely uniform, so your pipeline has to handle both.
"""

from pypdf import PdfReader
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        text_parts.append(text)
    combined = "\n".join(text_parts).strip()
    return combined


def needs_ocr(extracted_text: str, min_chars: int = 30) -> bool:
    """Heuristic: if pypdf barely got any text, it's probably a scanned image."""
    return len(extracted_text) < min_chars


def extract_text_with_ocr(file_bytes: bytes) -> str:
    """
    OCR fallback for scanned documents.
    Requires poppler + tesseract installed on the system
    (apt install poppler-utils tesseract-ocr).
    """
    from pdf2image import convert_from_bytes
    import pytesseract

    images = convert_from_bytes(file_bytes)
    text_parts = [pytesseract.image_to_string(img) for img in images]
    return "\n".join(text_parts).strip()


def extract_text(file_bytes: bytes) -> str:
    text = extract_text_from_pdf(file_bytes)
    if needs_ocr(text):
        try:
            text = extract_text_with_ocr(file_bytes)
        except Exception as e:
            # OCR deps missing or failed — surface what we have rather than crash
            text = text or f"[OCR failed: {e}]"
    return text
