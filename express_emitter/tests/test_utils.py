import os
import sys
from io import BytesIO

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

import pytest

from express_emitter.utils import determine_source, extract_content


def test_determine_source() -> None:
    assert determine_source(".txt") == "text"
    assert determine_source(".csv") == "csv"
    assert determine_source(".pdf") == "pdf"
    assert determine_source(".foo") == "unknown"


def test_extract_text() -> None:
    data = b"hello world"
    assert extract_content(data, ".txt") == "hello world"
    assert "a,b" in extract_content(b"a,b\n1,2", ".csv")


def test_extract_pdf(tmp_path: str) -> None:
    pytest.importorskip("fitz")
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "hello pdf")
    pdf_bytes = doc.write()
    doc.close()

    text = extract_content(pdf_bytes, ".pdf")
    assert "hello pdf" in text
