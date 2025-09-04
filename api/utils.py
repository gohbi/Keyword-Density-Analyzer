# api/utils.py
import pathlib
import spacy
from typing import Any

# Path where the model was copied during the Docker build
MODEL_DIR = pathlib.Path(__file__).parent / "_spacy_models"

def get_spacy_nlp() -> spacy.Language:
    """
    Load the pre‑bundled spaCy model.
    If, for any reason, the model directory is missing,
    raise a clear exception so the caller can return a 500 error.
    """
    if not MODEL_DIR.exists():
        raise FileNotFoundError(
            f"SpaCy model directory not found at {MODEL_DIR}. "
            "Make sure the Dockerfile copies the model correctly."
        )

    # The model package name is stored in the directory; we can load it via `spacy.load`.
    # spaCy will look for a model in the given path.
    try:
        nlp = spacy.load(str(MODEL_DIR))
        return nlp
    except Exception as exc:
        # Re‑raise with a more helpful message
        raise RuntimeError(f"Failed to load spaCy model from {MODEL_DIR}: {exc}") from exc
