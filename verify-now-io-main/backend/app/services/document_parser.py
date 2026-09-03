"""
Extracts real text content from uploaded documents so it can be verified.
No content is invented -- unsupported/corrupt files raise a clear error
instead of silently producing empty or placeholder text.
"""
import io

from docx import Document
from pypdf import PdfReader


class DocumentParseError(Exception):
    pass


def extract_text_from_bytes(filename: str, content: bytes, max_chars: int = 12000) -> str:
    lower = filename.lower()

    if lower.endswith(".pdf"):
        try:
            reader = PdfReader(io.BytesIO(content))
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(pages).strip()
        except Exception as exc:  # noqa: BLE001
            raise DocumentParseError(f"Failed to parse PDF: {exc}") from exc

    elif lower.endswith(".docx"):
        try:
            doc = Document(io.BytesIO(content))
            text = "\n".join(p.text for p in doc.paragraphs).strip()
        except Exception as exc:  # noqa: BLE001
            raise DocumentParseError(f"Failed to parse DOCX: {exc}") from exc

    elif lower.endswith(".txt") or lower.endswith(".md"):
        try:
            text = content.decode("utf-8", errors="replace").strip()
        except Exception as exc:  # noqa: BLE001
            raise DocumentParseError(f"Failed to decode text file: {exc}") from exc

    else:
        raise DocumentParseError(
            f"Unsupported document type for '{filename}'. Supported: .pdf, .docx, .txt, .md"
        )

    if not text:
        raise DocumentParseError(
            "No extractable text found in document (it may be a scanned image without OCR)."
        )

    return text[:max_chars]
