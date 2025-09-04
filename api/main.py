# api/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import pathlib
import pandas as pd
import logging
import json

# ----------------------------------------------------------------------
# Existing utilities
# ----------------------------------------------------------------------
from .utils import get_spacy_nlp          # lazy spaCy loader (unchanged)
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
KEYWORDS = ["privacy", "encryption", "proton", "vpn", "security"]  # <-- edit as needed

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
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """
    1️⃣  Read raw bytes from the uploaded file.
    2️⃣  Convert to plain text (supports PDF, DOCX, ODT, TXT).
    3️⃣  Run spaCy tokenisation.
    4️⃣  Compute keyword density for the list above.
    5️⃣  Persist the JSON result (overwrites previous output).
    6️⃣  Return the JSON payload.
    """
    try:
        # --------------------------------------------------------------
        # 1️⃣  Raw bytes
        # --------------------------------------------------------------
        raw_bytes = await file.read()

        # --------------------------------------------------------------
        # 2️⃣  Plain‑text extraction (uses the new helper)
        # --------------------------------------------------------------
        text = read_file(raw_bytes, file.filename)

        # --------------------------------------------------------------
        # 3️⃣  spaCy processing (unchanged)
        # --------------------------------------------------------------
        nlp = get_spacy_nlp()
        doc = nlp(text)

        # Keep only meaningful tokens (same filter you already used)
        tokens = [
            t.text.lower()
            for t in doc
            if not t.is_stop and not t.is_punct and not t.is_space
        ]

        if not tokens:
            return JSONResponse(
                status_code=200,
                content={"message": "No meaningful tokens found in the document."},
            )

        # --------------------------------------------------------------
        # 4️⃣  Keyword‑density calculation
        # --------------------------------------------------------------
        density = _keyword_density(tokens, KEYWORDS)

        # --------------------------------------------------------------
        # 5️⃣  Build the response payload
        # --------------------------------------------------------------
        total_words = len(tokens)
        result = {
            "filename": file.filename,
            "total_words": total_words,
            "keyword_density": density,
        }

        # --------------------------------------------------------------
        # 6️⃣  Persist the JSON (overwrites previous output)
        # --------------------------------------------------------------
        _clear_previous_output()
        out_path = OUTPUT_DIR / "latest.json"
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))

        # --------------------------------------------------------------
        # 7️⃣  Return to the caller
        # --------------------------------------------------------------
        return JSONResponse(status_code=200, content=result)

    except Exception as exc:               # pragma: no cover
        logging.exception("Analysis failed")
        raise HTTPException(status_code=400, detail=str(exc))


# ----------------------------------------------------------------------
# Simple health‑check endpoint (Render hits “/” by default)
# ----------------------------------------------------------------------
@app.get("/")
async def health():
    return {"status": "ok"}
