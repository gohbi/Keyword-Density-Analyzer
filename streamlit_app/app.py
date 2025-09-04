import streamlit as st
import httpx
from pathlib import Path

# ----------------------------------------------------------------------
# Helper: call the FastAPI backend
# ----------------------------------------------------------------------
def analyze_file(file_bytes: bytes, filename: str):
    """
    Sends the uploaded file to the FastAPI /analyze endpoint.
    Returns the JSON response (or raises an exception).
    """
    url = "http://localhost:8000/analyze"
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
    Upload a **plain‑text**, **PDF**, or **DOCX** file and the app will return the
    top 20 keywords (excluding stop‑words) along with their frequencies.
    """
)

uploaded = st.file_uploader(
    "Choose a file",
    type=["txt", "pdf", "docx"],
    help="Maximum size ~5 MB (larger files may cause timeouts).",
)

if uploaded:
    # Show a spinner while we talk to the backend
    with st.spinner("Analyzing…"):
        try:
            result = analyze_file(uploaded.read(), uploaded.name)
        except httpx.HTTPStatusError as exc:
            st.error(f"Backend returned an error: {exc.response.status_code}")
            st.code(exc.response.text)
        except Exception as e:
            st.error(f"Unexpected error: {e}")
        else:
            # Display the JSON nicely
            st.success("✅ Analysis complete!")
            st.subheader("Top Keywords")
            # Convert dict → sorted list for pretty printing
            sorted_items = sorted(result.items(), key=lambda kv: kv[1], reverse=True)
            for word, freq in sorted_items[:20]:
                st.markdown(f"- **{word}** → {freq}")

            # Optional: raw JSON view
            with st.expander("Show raw JSON"):
                st.json(result)
