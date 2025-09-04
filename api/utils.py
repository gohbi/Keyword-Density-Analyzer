# api/utils.py
import logging
import pathlib
import os
from functools import lru_cache

import spacy

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
