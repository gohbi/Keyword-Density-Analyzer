# streamlit_app/app.py
# --------------------------------------------------------------
import os
from pathlib import Path

import httpx
import pandas as pd
import streamlit as st
import requests

# ------------------------------------------------------------------
#   Backend configuration
# ------------------------------------------------------------------
# Render injects FASTAPI_PORT; fall back to 8000 (the port FastAPI runs on)
FASTAPI_PORT = os.getenv("FASTAPI_PORT", "8000")
BASE_URL = f"http://localhost:{FASTAPI_PORT}"


# ----------------------------------------------------------------------
# Streamlit layout
# ----------------------------------------------------------------------
st.set_page_config(page_title="Keyword‑Density Analyzer", layout="centered")

st.title("🔍 Keyword‑Density Analyzer")
st.write(
    """
    Upload a **plain‑text**, **PDF**, **DOCX** or **ODT** file and the app will
    return the **keyword density** (percentage of total words) for the
    pre‑defined keyword list.
    """
)

# ------------------------------------------------------------------
# Slider – lets the user choose the minimum count (default = 3)
# ------------------------------------------------------------------
min_occurrences = st.slider(
    "Show words that appear at least",
    min_value=1,
    max_value=20,
    value=3,
    step=1,
    help="Words with fewer occurrences will be hidden."
)

uploaded_file = st.file_uploader(
    "Choose a file", 
    type=["txt", "pdf", "docx", "odt"],
    help="Maximum size ~5 MB (larger files may cause timeouts).",
)


# ----------------------------------------------------------------------
# Helper: call the FastAPI backend
# ----------------------------------------------------------------------
def analyze_file(file_bytes: bytes, filename: str) -> list[dict]:
    """
    POST the file to the FastAPI ``/analyze`` endpoint.
    Returns the JSON list produced by the backend, where each element
    contains ``word``, ``count`` and ``density``.
    """
    backend_port = os.getenv("FASTAPI_PORT", "8501")
    url = f"http://localhost:{backend_port}/analyze?min_count={min_occurrences}"
    files = {"file": (filename, file_bytes)}
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(url, files=files)
        resp.raise_for_status()          # raises for 4xx/5xx
        return resp.json()               # list of dicts




# ------------------------------------------------------------------
#   Main flow – run when a file is provided
# ------------------------------------------------------------------
if uploaded_file is not None:
    with st.spinner("Analyzing…"):
        try:
            # ``uploaded_file.read()`` returns the raw bytes of the file
            result = analyze_file(uploaded_file.read(), uploaded_file.name)
        except httpx.HTTPStatusError as exc:
            # FastAPI returned a 4xx/5xx – show the message from the API
            st.error(f"Backend error {exc.response.status_code}: {exc.response.text}")
            st.stop()
        except Exception as e:                 # pragma: no cover
            st.error(f"Unexpected error: {e}")
            st.stop()





    # --------------------------------------------------------------
    #   Show a friendly success banner
    # --------------------------------------------------------------
    st.success("✅ Analysis complete!")

   # ------------------------------------------------------------------
    #   Render the frequency table
    # ------------------------------------------------------------------
    if not result:
        st.info("No words met the selected minimum occurrence threshold.")
    else:
        df = pd.DataFrame(result)               # columns: word, count, density
        # Sort by count descending for nicer UX
        df = df.sort_values(by="count", ascending=False)
        st.subheader("Word Frequency (≥ threshold)")
        st.dataframe(df, hide_index=True)
        
    # --------------------------------------------------------------
    #  Optional raw JSON view (useful for debugging)
    # --------------------------------------------------------------
    with st.expander("Show raw JSON"):
        st.json(result)
