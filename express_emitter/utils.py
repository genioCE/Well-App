from __future__ import annotations

from typing import Any

ALLOWED_EXTENSIONS = {".txt", ".csv", ".pdf"}


def determine_source(extension: str) -> str:
    """Map file extension to source type."""
    ext = extension.lower()
    mapping = {".txt": "text", ".csv": "csv", ".pdf": "pdf"}
    return mapping.get(ext, "unknown")


def extract_content(content: bytes, extension: str) -> str:
    """Return text content from supported file bytes."""
    ext = extension.lower()
    if ext in {".txt", ".csv"}:
        return content.decode("utf-8", errors="ignore")
    if ext == ".pdf":
        try:
            import fitz  # PyMuPDF
        except Exception as exc:  # noqa: BLE001
            raise ImportError("PyMuPDF is required for PDF extraction") from exc

        with fitz.open(stream=content, filetype="pdf") as doc:
            text = "".join(page.get_text() for page in doc)
        return text
    raise ValueError("Unsupported file type")
