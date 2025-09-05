# ──────────────────────────────────────────────────────────────
# api/text_extractor.py
# ──────────────────────────────────────────────────────────────
import io
import pathlib
import chardet
from fastapi import HTTPException, UploadFile

# ---------- TXT ----------
def _read_txt(raw: bytes) -> str:
    """Robust UTF‑8 → fallback → replace."""
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        guess = chardet.detect(raw)
        enc = guess["encoding"] or "latin-1"
        return raw.decode(enc, errors="replace")


# ---------- PDF ----------
def _read_pdf(raw: bytes) -> str:
    from pdfminer.high_level import extract_text
    with io.BytesIO(raw) as f:
        return extract_text(f)


# ---------- DOCX ----------
def _read_docx(raw: bytes) -> str:
    from docx import Document
    with io.BytesIO(raw) as f:
        doc = Document(f)
        return "\n".join(p.text for p in doc.paragraphs)


# ---------- ODT ----------
def _read_odt(raw: bytes) -> str:
    from odf.opendocument import load
    from odf.text import P
    with io.BytesIO(raw) as f:
        odt = load(f)
        paras = odt.getElementsByType(P)
        return "\n".join(p.firstChild.data if p.firstChild else "" for p in paras)


# ---------- Dispatcher ----------
async def read_file(upload: UploadFile) -> str:
    """
    Detect the file extension and return plain‑text.
    Raises HTTPException(400) for unsupported types.
    """
    raw = await upload.read()
    ext = pathlib.Path(upload.filename).suffix.lower()

    if ext == ".txt":
        return _read_txt(raw)
    if ext == ".pdf":
        return _read_pdf(raw)
    if ext == ".docx":
        return _read_docx(raw)
    if ext == ".odt":
        return _read_odt(raw)

    raise HTTPException(
        status_code=400,
        detail=(
            f"Unsupported file type '{ext}'. "
            "Supported extensions: .txt, .pdf, .docx, .odt"
        ),
    )
