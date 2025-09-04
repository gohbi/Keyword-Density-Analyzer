from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import io
import logging

# Import the helper that lazily ensures the spaCy model exists
from .utils import get_spacy_nlp

app = FastAPI(title="Keyword Density Analyzer")

# ----------------------------------------------------------------------
# Helper: read a file (PDF, DOCX, TXT) and return its text as a string
# ----------------------------------------------------------------------
def _read_file(file_bytes: bytes, filename: str) -> str:
    lower_name = filename.lower()
    if lower_name.endswith(".pdf"):
        from pdfminer.high_level import extract_text
        return extract_text(io.BytesIO(file_bytes))
    elif lower_name.endswith(".docx"):
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)
    elif lower_name.endswith(".txt"):
        return file_bytes.decode(errors="replace")
    else:
        raise ValueError(f"Unsupported file type: {filename}")

# ----------------------------------------------------------------------
# Endpoint – analyse a single uploaded file
# ----------------------------------------------------------------------
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        # 1️⃣ Read the raw bytes
        raw_bytes = await file.read()

        # 2️⃣ Extract plain text
        text = _read_file(raw_bytes, file.filename)

        # 3️⃣ Load spaCy model (downloaded lazily on first use)
        nlp = get_spacy_nlp()

        # 4️⃣ Tokenise and compute frequencies
        doc = nlp(text)
        tokens = [t.text.lower() for t in doc if not t.is_stop and not t.is_punct and not t.is_space]

        if not tokens:
            return JSONResponse(
                status_code=200,
                content={"message": "No meaningful tokens found in the document."}
            )

        freq_series = pd.Series(tokens).value_counts().astype(int)
        total_words = len(tokens)

        # 5️⃣ Build the response payload
        result = {
            "total_words": total_words,
            "unique_words": int(freq_series.shape[0]),
            "top_keywords": [
                {"keyword": kw, "count": int(cnt), "percentage": round((cnt / total_words) * 100, 2)}
                for kw, cnt in freq_series.head(20).items()
            ]
        }

        return JSONResponse(status_code=200, content=result)

    except Exception as exc:
        logging.exception("Analysis failed")
        raise HTTPException(status_code=400, detail=str(exc))

# ----------------------------------------------------------------------
# Simple health‑check endpoint (Render hits “/” by default)
# ----------------------------------------------------------------------
@app.get("/")
async def health():
    return {"status": "ok"}
