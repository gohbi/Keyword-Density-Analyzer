# api/utils.py
import logging
import pathlib
import os
from functools import lru_cache

import spacy

# ──────────────────────────────────────────────────────────────
"""
Utility helpers for the Keyword‑Density Analyzer.

* `tokenize(text)` – split a string into lowercase word tokens.
* `compute_frequencies(tokens, min_count)` – count tokens, keep only
  those that appear at least `min_count` times, and calculate density.
"""

import re
from collections import Counter
from typing import List, Dict

# ------------------------------------------------------------------
# Tokeniser – pure‑Python, no external model required.
# ------------------------------------------------------------------
_WORD_RE = re.compile(r"\b\w+\b", flags=re.UNICODE)


def tokenize(text: str) -> List[str]:
    """
    Return a list of lowercase word tokens.
    • Keeps only alphanumeric “words” (punctuation, emojis, etc. are dropped).
    • Works for any language that uses Unicode word characters.
    """
    return [tok.lower() for tok in _WORD_RE.findall(text)]


# ------------------------------------------------------------------
# Frequency calculator + filter.
# ------------------------------------------------------------------
def compute_frequencies(tokens: List[str], min_count: int = 3) -> List[Dict]:
    """
    From a list of tokens produce the JSON payload expected by the UI.

    Parameters
    ----------
    tokens : List[str]
        All word tokens from the document (already lower‑cased).
    min_count : int, default = 3
        Minimum number of occurrences required for a word to be included.

    Returns
    -------
    List[Dict] – each dict contains:
        * word   – the token
        * count  – how many times it appeared
        * density – percentage of total tokens (rounded to 2 dp)
    """
    total = len(tokens)
    if total == 0:                     # empty document → empty result
        return []

    # Count every token
    freq = Counter(tokens)

    # Keep only words that meet the threshold
    filtered = [(w, c) for w, c in freq.items() if c >= min_count]

    # Sort by descending count (most frequent first)
    filtered.sort(key=lambda pair: pair[1], reverse=True)

    # Build the final list of dicts
    result = [
        {
            "word": w,
            "count": c,
            "density": round((c / total) * 100, 2)   # percent, two decimals
        }
        for w, c in filtered
    ]

    return result

# ----------------------------------------------------------------------
# Where the model lives (optional – you can keep it for debugging)
# ----------------------------------------------------------------------
# The Dockerfile sets SPACY_DATA to the directory that already contains the model.
# If you also want a convenient Path object you can read it from the env‑var.
MODEL_DIR = pathlib.Path(
    os.getenv("SPACY_DATA", "/opt/venv/lib/python3.12/site-packages")
)

# ----------------------------------------------------------------------
# Cached spaCy loader – this is the only thing the rest of the code calls
# ----------------------------------------------------------------------
@lru_cache(maxsize=1)
def get_spacy_nlp() -> spacy.language.Language:
    """
    Return a cached spaCy Language object.

    The English model (`en_core_web_sm`) is installed at **build time**
    (see Dockerfile).  Because the Dockerfile exports ``SPACY_DATA``,
    ``spacy.load`` automatically finds the model without any extra
    configuration.
    """
    # A tiny log line helps you see when the model is actually loaded
    logging.debug("Loading spaCy model from %s", MODEL_DIR)
    return spacy.load("en_core_web_sm")


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# NOTE: The original ``*ensure*model_downloaded`` function has been
# completely removed.  It tried to run:
#
#   python -m spacy download en_core_web_sm --dest <path>
#
# The ``--dest`` flag is no longer supported by spaCy (it caused the
# “Invalid wheel filename” error you saw).  Because the model is baked
# into the image, there is nothing to download at request time, so the
# helper is unnecessary and would only re‑introduce the failure mode.
# ----------------------------------------------------------------------
