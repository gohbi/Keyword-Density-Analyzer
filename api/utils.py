import spacy
import subprocess
import pathlib
import os
import logging
from functools import lru_cache

# The model is already present in the image (see Dockerfile).
# We only need to load it; no download, no --dest flag.
@lru_cache(maxsize=1)
def get_spacy_nlp():
    """
    Return a cached spaCy Language object.
    The model was baked into the container at build time, so we simply load it.
    """
    # Because we set SPACY_DATA in the Dockerfile, spacy.load will find the model.
    return spacy.load("en_core_web_sm")


MODEL_DIR = pathlib.Path(os.getenv("SPACY_MODEL_DIR", "/app/api/_spacy_models"))

def _ensure_model_downloaded():
    """
    If the directory does not contain a valid spaCy model,
    invoke `python -m spacy download` to populate it.
    """
    if (MODEL_DIR / "meta.json").exists():
        return  # already there

    logging.info("Downloading spaCy model into %s …", MODEL_DIR)
    # Ensure the target directory exists and is writable
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # Download the *same* model you declared in requirements.txt
    # (the name must match the pip package, e.g. en_core_web_sm)
    subprocess.check_call([
        "python", "-m", "spacy", "download", "en_core_web_sm",
        "--dest", str(MODEL_DIR)
    ])


