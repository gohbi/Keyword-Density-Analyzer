import subprocess
import sys
from pathlib import Path
import spacy

_MODEL_NAME = "en_core_web_sm"
_MODEL_PATH = Path(__file__).parent / "_spacy_models" / _MODEL_NAME


def _download_model() -> None:
    """
    Downloads the spaCy model into a sub‑directory of the package.
    This runs **inside the container at runtime**, not during the Docker build,
    so the image stays small and the download happens only once per container start.
    """
    # Ensure the target directory exists
    _MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    # If the model is already there, skip the download
    if (_MODEL_PATH / "meta.json").exists():
        return

    # Run the spaCy download command, pointing it to the local folder
    subprocess.check_call([
        sys.executable,
        "-m",
        "spacy",
        "download",
        _MODEL_NAME,
        "--direct",
        "--dest",
        str(_MODEL_PATH.parent)
    ])


def get_spacy_nlp():
    """
    Returns a loaded spaCy Language object.
    The first call will trigger a download if the model is missing.
    Subsequent calls reuse the cached object.
    """
    global _nlp
    try:
        return _nlp
    except NameError:
        # Download if needed, then load from the local path
        _download_model()
        _nlp = spacy.load(str(_MODEL_PATH))
        return _nlp
