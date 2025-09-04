# streamlit_app/app.py
# --------------------------------------------------------------
import os
from pathlib import Path

import httpx
import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------
# Helper: call the FastAPI backend
# ----------------------------------------------------------------------
def analyze_file(file_bytes: bytes, filename: str):
    """
    Sends the uploaded file to the FastAPI /analyze endpoint.
    Returns the parsed JSON response (or raises an exception).
    """
    # Render injects the FastAPI port via $FASTAPI_PORT;
    # default to 8501 for local development.
    backend_port = os.getenv("FASTAPI_PORT", "8501")
    url = f"http://localhost:{backend_port}/analyze"

    files = {"file": (filename, file_bytes)}
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(url, files=files)
        resp.raise_for_status()
        return resp.json()


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

uploaded = st.file_uploader(
    "Choose a file",
    type=["txt", "pdf", "docx", "odt"],
    help="Maximum size ~5 MB (larger files may cause timeouts).",
)

if uploaded:
    # --------------------------------------------------------------
    # 1️⃣  Send the file to the backend
    # --------------------------------------------------------------
    with st.spinner("Analyzing…"):
        try:
            result = analyze_file(uploaded.read(), uploaded.name)
        except httpx.HTTPStatusError as exc:
            st.error(f"Backend returned an error: {exc.response.status_code}")
            st.code(exc.response.text)
            st.stop()
        except Exception as e:  # pragma: no cover
            st.error(f"Unexpected error: {e}")
            st.stop()

    # --------------------------------------------------------------
    # 2️⃣  Show a friendly success banner
    # --------------------------------------------------------------
    st.success("✅ Analysis complete!")

    # --------------------------------------------------------------
    # 3️⃣  Render the keyword‑density table
    # --------------------------------------------------------------
    st.subheader("Keyword Density (%)")
    density_dict = result.get("keyword_density", {})

    if not density_dict:
        st.info("No keywords from the configured list were found in the document.")
    else:
        # Turn the dict into a sorted DataFrame for pretty rendering
        df = (
            pd.DataFrame(list(density_dict.items()), columns=["Keyword", "Density (%)"])
            .sort_values(by="Density (%)", ascending=False)
        )
        # Streamlit will display a nice sortable table
        st.dataframe(df, hide_index=True)

    # --------------------------------------------------------------
    # 4️⃣  Optional raw JSON view (useful for debugging)
    # --------------------------------------------------------------
    with st.expander("Show raw JSON"):
        st.json(result)
