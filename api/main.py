# ──────────────────────────────────────────────────────────────
# api/main.py
# ──────────────────────────────────────────────────────────────
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import pathlib
import logging
from typing import List, Dict

# ----------------------------------------------------------------------
# Utilities
# ----------------------------------------------------------------------
from .utils import (
    get_spacy_nlp,          # lazy spaCy loader (unchanged)
    tokenize,
    compute_frequencies,
)

# NEW: helper that knows how to turn *any* supported upload into plain text
from .text_extractor import read_file

# ----------------------------------------------------------------------
# FastAPI app
# ----------------------------------------------------------------------
app = FastAPI(title="Keyword Density Analyzer")

# ----------------------------------------------------------------------
# Startup – keep the spaCy model folder creation (unchanged)
# ----------------------------------------------------------------------
@app.on_event("startup")
def create_spacy_dir():
    spacy_path = pathlib.Path("/app/api/_spacy_models")
    spacy_path.mkdir(parents=True, exist_ok=True)   # owned by appuser already

# ----------------------------------------------------------------------
# Temporary JSON output directory (unchanged)
# ----------------------------------------------------------------------
OUTPUT_DIR = pathlib.Path("/tmp/lumo-output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def clear_previous_output():
    """Remove any stale JSON result – we keep only the latest one."""
    for f in OUTPUT_DIR.glob("*.json"):
        try:
            f.unlink()
        except Exception:
            pass


# ----------------------------------------------------------------------
# Configurable threshold – can be overridden with an env‑var.
# ----------------------------------------------------------------------
MIN_COUNT = int(os.getenv("LUMO_MIN_WORD_COUNT", "3"))   # default = 3


# ----------------------------------------------------------------------
# Endpoint – analyse a single uploaded file
# ----------------------------------------------------------------------
@app.post("/analyze", response_model=List[Dict])
async def analyze(file: UploadFile = File(...)):
    """
    Receive a file (TXT, PDF, DOCX, ODT), extract plain text,
    compute word frequencies, and return the filtered list as JSON.
    """
    # --------------------------------------------------------------
    # Read the file and turn it into plain‑text
    # --------------------------------------------------------------
    try:
        # `read_file` does:
        #   • Detect the extension
        #   • Choose the proper extractor (txt → robust decode,
        #     pdf → pdfminer, docx → python‑docx, odt → odfpy)
        #   • Returns a *str* containing the extracted text.
        text = await read_file(file)          # <-- NEW line
    except HTTPException as http_exc:
        # Propagate our own 400/415 messages unchanged
        raise http_exc
    except Exception as exc:
        # Anything unexpected becomes a generic 400 – same shape as before
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read uploaded file: {exc}",
        ) from exc

    # --------------------------------------------------------------
    # Tokenise the whole document
    # --------------------------------------------------------------
    tokens = tokenize(text)

    # --------------------------------------------------------------
    # Compute frequencies, applying the MIN_COUNT filter
    # --------------------------------------------------------------
    result = compute_frequencies(tokens, min_count=MIN_COUNT)

    # --------------------------------------------------------------
    # Return JSON that Streamlit will turn into a table
    # --------------------------------------------------------------
    return JSONResponse(content=result)


# ----------------------------------------------------------------------
# Simple health‑check endpoint (Render hits “/” by default)
# ----------------------------------------------------------------------
@app.get("/")
async def health():
    return {"status": "ok"}
