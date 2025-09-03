import os
from pathlib import Path
from typing import List, Tuple

import spacy
from collections import Counter
from pdfminer.high_level import extract_text as pdf_to_text
from docx import Document

# Load spaCy model once (global)
nlp = spacy.load("en_core_web_sm")


def _read_pdf(path: Path) -> str:
    """Extract raw text from a PDF file."""
    return pdf_to_text(str(path))


def _read_docx(path: Path) -> str:
    """Extract raw text from a DOCX file."""
    doc = Document(str(path))
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)


def read_file(file_path: str) -> str:
    """
    Dispatch based on extension and return the plain‑text content.
    Supported: .pdf, .docx, .doc
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _read_pdf(path)
    elif suffix in {".docx", ".doc"}:
        return _read_docx(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def preprocess(text: str) -> List[str]:
    """
    Lower‑case, lemmatize, drop stop‑words and non‑alphabetic tokens.
    Returns a list of cleaned tokens.
    """
    doc = nlp(text.lower())
    tokens = [
        token.lemma_
        for token in doc
        if token.is_alpha and not token.is_stop
    ]
    return tokens


def keyword_density(tokens: List[str]) -> List[Tuple[str, int, float]]:
    """
    Compute raw count and percentage for each token.
    Returns a list sorted by descending count:
    [(word, count, density_percent), ...]
    """
    total = len(tokens)
    freq = Counter(tokens)

    result = [
        (word, cnt, round(cnt / total * 100, 2))
        for word, cnt in freq.most_common()
    ]
    return result
