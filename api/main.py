# api/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import pathlib
import pandas as pd
import logging
import json
from typing import List, Dict


# ----------------------------------------------------------------------
# Existing utilities
# ----------------------------------------------------------------------
from .utils import get_spacy_nlp, tokenize, compute_frequencies         # lazy spaCy loader (unchanged)
from .text_extractor import read_file      # <-- NEW import

app = FastAPI(title="Keyword Density Analyzer")

# ----------------------------------------------------------------------
# Startup – keep the spacy model folder creation (unchanged)
# ----------------------------------------------------------------------
@app.on_event("startup")
def create_spacy_dir():
    spacy_path = pathlib.Path("/app/api/_spacy_models")
    spacy_path.mkdir(parents=True, exist_ok=True)   # owned by appuser already


# ----------------------------------------------------------------------
# Helper: compute keyword density
# ----------------------------------------------------------------------


def _keyword_density(tokens: list[str], keywords: list[str]) -> dict[str, float]:
    """
    Return a mapping {keyword: density_percent}.
    Density = (occurrences / total_tokens) * 100
    """
    total = len(tokens) or 1                     # avoid division by zero
    # Normalise both token list and keyword list to lower case
    token_counts = pd.Series(tokens).value_counts()
    density = {}
    for kw in keywords:
        kw_lc = kw.lower()
        cnt = token_counts.get(kw_lc, 0)
        density[kw] = round(cnt / total * 100, 2)
    return density


# ----------------------------------------------------------------------
# Helper: manage the temporary JSON output file
# ----------------------------------------------------------------------
OUTPUT_DIR = pathlib.Path("/tmp/lumo-output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def _clear_previous_output():
    """Remove any stale JSON result – we keep only the latest one."""
    for f in OUTPUT_DIR.glob("*.json"):
        try:
            f.unlink()
        except Exception:
            pass


# ----------------------------------------------------------------------
# Endpoint – analyse a single uploaded file
# ----------------------------------------------------------------------
# ------------------------------------------------------------------
# Configurable threshold – can be overridden with an env‑var.
# ------------------------------------------------------------------
MIN_COUNT = int(os.getenv("LUMO_MIN_WORD_COUNT", "3"))   # default = 3


@app.post("/analyze", response_model=List[Dict])
async def analyze(file: UploadFile = File(...)):
    """
    Receive a text file, compute word frequencies, and return the
    filtered list as JSON.
    """
    # 1️⃣ Read the file (expect UTF‑8 text)
    try:
        raw = await file.read()
        text = raw.decode("utf-8")
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read uploaded file: {exc}"
        )

    # 2️⃣ Tokenise the whole document
    tokens = tokenize(text)

    # 3️⃣ Compute frequencies, applying the MIN_COUNT filter
    result = compute_frequencies(tokens, min_count=MIN_COUNT)

    # 4️⃣ Return JSON that Streamlit will turn into a table
    return JSONResponse(content=result)

    except Exception as exc:               # pragma: no cover
        logging.exception("Analysis failed")
        raise HTTPException(status_code=400, detail=str(exc))


# ----------------------------------------------------------------------
# Simple health‑check endpoint (Render hits “/” by default)
# ----------------------------------------------------------------------
@app.get("/")
async def health():
    return {"status": "ok"}
