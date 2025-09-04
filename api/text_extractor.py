# api/text_extractor.py
import io
from typing import Union

from pdfminer.high_level import extract_text_to_fp
from docx import Document
from odf import text, teletype
from odf.opendocument import load as load_odf

def _read_pdf(data: bytes) -> str:
    """Extract text from a PDF byte‑stream."""
    out = io.StringIO()
    with io.BytesIO(data) as src:
        extract_text_to_fp(src, out)
    return out.getvalue()

def _read_docx(data: bytes) -> str:
    """Extract text from a DOCX byte‑stream."""
    doc = Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs)

def _read_odt(data: bytes) -> str:
    """Extract text from an ODT byte‑stream."""
    odt = load_odf(io.BytesIO(data))
    all_paras = odt.getElementsByType(text.P)
    return "\n".join(teletype.extractText(p) for p in all_paras)

def _read_txt(data: bytes) -> str:
    """Plain‑text files – just decode."""
    return data.decode(errors="ignore")

def extract_text(file_name: str, data: bytes) -> str:
    """Dispatch based on filename extension."""
    ext = file_name.lower().rsplit(".", 1)[-1]
    if ext == "pdf":
        return _read_pdf(data)
    if ext in ("docx", "doc"):
        return _read_docx(data)
    if ext == "odt":
        return _read_odt(data)
    if ext == "txt":
        return _read_txt(data)
    raise ValueError(f"Unsupported file type: .{ext}")
