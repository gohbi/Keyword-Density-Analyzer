import os
import uuid
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from .utils import read_file, preprocess, keyword_density

app = FastAPI(
    title="Keyword‑Density Analyzer",
    description="Upload a PDF/DOCX and receive a word‑frequency report.",
    version="0.1.0",
)


UPLOAD_DIR = Path("./tmp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """
    Accept a PDF or DOCX, compute keyword density,
    and return JSON with the top words.
    """
    # Basic validation
    if file.content_type not in {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    }:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    # Store temporarily on disk (required for pdfminer / python-docx)
    suffix = Path(file.filename).suffix.lower()
    temp_name = f"{uuid.uuid4()}{suffix}"
    temp_path = UPLOAD_DIR / temp_name

    # Write the uploaded bytes to the temp file
    with open(temp_path, "wb") as out_file:
        content = await file.read()
        out_file.write(content)

    try:
        raw_text = read_file(str(temp_path))
        tokens = preprocess(raw_text)
        density = keyword_density(tokens)

        # Return only the top 30 entries (adjust as you like)
        top_n = density[:30]

        response = {
            "filename": file.filename,
            "total_words": len(tokens),
            "top_keywords": [
                {"word": w, "count": c, "density_pct": d} for w, c, d in top_n
            ],
        }
        return JSONResponse(content=response)

    finally:
        # Clean up the temporary file
        if temp_path.exists():
            temp_path.unlink()
