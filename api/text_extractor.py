# --------------------------------------------------------------
# api/text_extractor.py
# --------------------------------------------------------------
"""
Utility module that turns a binary upload (PDF, DOCX, ODT, TXT)
into plain‑text.  The public entry point is ``read_file``.
"""

from __future__ import annotations

import io
from typing import Final

# ------------------------------------------------------------------
# Public API – what other modules may import
# ------------------------------------------------------------------
__all__: Final = ["read_file"]


# ------------------------------------------------------------------
# Private helpers – each one imports its heavy dependency lazily
# ------------------------------------------------------------------
def _read_pdf(data: bytes) -> str:
    """Extract plain text from a PDF binary blob."""
    # Import inside the function – avoids ImportError at module import time
    from pdfminer.high_level import extract_text as _pdf_extract_text

    out = io.StringIO()
    _pdf_extract_text(io.BytesIO(data), out)
    return out.getvalue()


def _read_docx(data: bytes) -> str:
    """Extract plain text from a DOCX binary blob."""
    from docx import Document

    doc = Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs)


def _read_odt(data: bytes) -> str:
    """Extract plain text from an ODT binary blob."""
    from odf import text, teletype
    from odf.opendocument import load as _load_odf

    odt = _load_odf(io.BytesIO(data))
    paras = odt.getElementsByType(text.P)
    return "\n".join(teletype.extractText(p) for p in paras)


def _read_txt(data: bytes) -> str:
    """Decode a UTF‑8/ASCII text file."""
    return data.decode(errors="replace")


# ------------------------------------------------------------------
# Public wrapper
# ------------------------------------------------------------------
def read_file(file_bytes: bytes, filename: str) -> str:
    """
    Dispatch to the correct extractor based on the file extension.
    Supported extensions (case‑insensitive): pdf, docx, doc, odt, txt.
    Raises ``ValueError`` for anything else.
    """
    ext = filename.lower().rsplit(".", 1)[-1]

    if ext == "pdf":
        return _read_pdf(file_bytes)
    if ext in ("docx", "doc"):
        return _read_docx(file_bytes)
    if ext == "odt":
        return _read_odt(file_bytes)
    if ext == "txt":
        return _read_txt(file_bytes)

    raise ValueError(f"Unsupported file type: {filename}")
