# Keyword-Density-Analyzer
Easily find the keyword density of a given document. Helps with resume optimization. 
A lightweight Python app that extracts text from PDFs/DOCX files, calculates how often each word appears, and presents the results as a clear density report.

## 📄 Project Overview

Job‑search platforms and Applicant Tracking Systems (ATS) often rank resumes higher when the wording matches the job description, especially when certain keywords appear with a noticeable frequency.
This tool gives job seekers a fast, visual way to see which terms dominate their resume (or any other document) so they can:

 * Spot missing industry‑specific buzzwords.
 * Adjust the wording to increase keyword density where it matters.
 * Avoid over‑stuffing by seeing exact percentages.

The core of the project is a **FastAPI backend** that:

1. Accepts a PDF or DOCX upload.
2. Extracts raw text (pdfminer.six / python‑docx).
3. Normalises the text (lower‑casing, lemmatisation, stop‑word removal) with spaCy.
4. Counts each token and computes its percentage of the total word count.

Both a **desktop GUI** (PySide6) and a web UI (Streamlit or a React front‑end) consume the same API, so the service can be run locally or hosted for anyone to use.


🎯 Why This Project Exists

1. **Showcase rapid learning** – I built the entire stack (PDF parsing, NLP, async API, GUI, Docker) from scratch while mastering the MERN‑style workflow in Python.
2. **Solve a real pain point** – Many candidates tweak their resumes blindly. By exposing the actual keyword density, the app empowers users to make data‑driven edits that align with ATS expectations.
3. **Demonstrate full‑stack competence** – Recruiters can see a clean, documented codebase, meaningful commit history, unit tests, and a deployable Docker image—all hallmarks of production‑ready software.

## 🚀 Quick Start (Local)

# Clone the repo
    git clone https://github.com/gohbi/keyword-density-analyzer.git
cd keyword-density-analyzer

# Create a virtual environment
    python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
    pip install -r requirements.txt

# Run the API (development mode)
    uvicorn api.main:app --reload

Visit http://127.0.0.1:8000/docs for the interactive Swagger UI where you can test the /analyze endpoint.

Optional: Launch the Streamlit UI

    streamlit run ui/streamlit_app.py

## 🛠️ Tech Stack

 | Layer |	Library / Tool |	Reason |
 | --- | --- | --- |
 | File parsing |	pdfminer.six, python-docx |	Reliable pure‑Python extraction |
 | NLP |	spaCy (en_core_web_sm) |	Fast tokenisation, lemmatisation, stop‑word filtering |
 | API |	FastAPI + Uvicorn |	Async, auto‑generated OpenAPI docs |
 | Desktop GUI |	PySide6 (Qt) |	Native‑look, cross‑platform |
 | Web UI |	Streamlit (or React) |	One‑file Python UI for rapid prototyping |
 | Containerisation |	Docker |	Consistent environment for local & cloud |
 | Hosting |	Render / Fly.io / Railway (Docker) |	Free tier HTTPS endpoints |
 | Testing |	pytest |	Guarantees correctness of parsing & counting |
 | Packaging |	pyinstaller (desktop) |	Single‑executable distribution |

## 📂 Repository Layout

    ├─ api/
    │   ├─ main.py          # FastAPI entry point
    │   ├─ utils.py         # text extraction & density logic
    │   └─ tests/           # pytest suite
    ├─ ui/
    │   ├─ streamlit_app.py # optional web UI
    │   └─ desktop_gui.py   # PySide6 GUI
    ├─ Dockerfile
    ├─ requirements.txt
    ├─ README.md            # <-- you are here
    └─ LICENSE              # MIT

📊 Example Output:

 | Keyword |	Count |	Density % |
 | --- | --- | --- |
 | python |	27 |	4.32 |
 | data |	19 |	3.04 |
 | analyst |	12 |	1.92 |
 | ... |	... |	... |

The table is returned as JSON from the API and rendered as a sortable grid in the UI.
🤝 Contributing

    Fork the repository.
    Create a feature branch (git checkout -b feat/xyz).
    Follow the Conventional Commits format for commit messages (feat, fix, docs, etc.).
    Open a Pull Request describing the change and referencing any related issue.

Please keep the code PEP 8 compliant and add unit tests for new functionality. 

📜 License

Distributed under the MIT License. See LICENSE for details. 

🙋‍♂️ Author

Reanna Francis – Passionate self-taught full‑stack developer focused on practical AI/NLP tools for career empowerment.
[GitHub Profile](https://github.com/gohbi) | [LinkedIn](www.linkedin.com/in/reannaf)


