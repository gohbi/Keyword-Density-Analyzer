import streamlit as st
import requests
import pandas as pd
from pathlib import Path

API_URL = "http://localhost:8000/analyze"   # adjust if you deploy elsewhere

st.title("Keyword‑Density Analyzer")
st.caption("Upload a PDF or DOCX and see the most frequent words.")

uploaded = st.file_uploader("Choose a file", type=["pdf", "docx", "doc"])

if uploaded:
    # Streamlit gives us a BytesIO; we need to send it as multipart/form-data
    files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
    with st.spinner("Analyzing…"):
        resp = requests.post(API_URL, files=files)
    if resp.status_code == 200:
        data = resp.json()
        df = pd.DataFrame(data["top_keywords"])
        st.success(f"Processed **{data['filename']}** – {data['total_words']} words")
        st.dataframe(df)
    else:
        st.error(f"Error: {resp.status_code} – {resp.text}")
