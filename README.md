# Keyword-Density-Analyzer 
(Built with AI)
Version 1.2 – released Sep 5 2025
A lightweight, privacy‑first web app that lets you upload a document (TXT, PDF, DOCX, ODT) and instantly see a table of word frequencies and densities. Built with FastAPI (backend) and Streamlit (frontend) and packaged for easy deployment on Render (or any Docker host).

### Visit the functional app:
[Key Density Analyzer](https://keyword-analyzer-3i9f.onrender.com)

Table of Contents

1. [/#Project Overview](https://github.com/gohbi/Keyword-Density-Analyzer/blob/main/README.md#-project-overview)
2. [The Why](https://github.com/gohbi/Keyword-Density-Analyzer/blob/main/README.md#-why-this-project-exists)
3. [Key Features](https://github.com/gohbi/Keyword-Density-Analyzer/blob/main/README.md#-key-features)
4. [Architecture Diagram](https://github.com/gohbi/Keyword-Density-Analyzer/blob/main/README.md#-architecture-diagram)
5. [Getting Started (Local)](https://github.com/gohbi/Keyword-Density-Analyzer/blob/main/README.md#-getting-started-(local))
6. [Deploying to Render (or any Docker host)](https://github.com/gohbi/Keyword-Density-Analyzer/blob/main/README.md#-deploying-to-render(or-any-docker-host))
7. [API Reference](https://github.com/gohbi/Keyword-Density-Analyzer/blob/main/README.md#-api-reference)
8. [Frontend Details (Streamlit UI)](https://github.com/gohbi/Keyword-Density-Analyzer/blob/main/README.md#-frontend-details-(streamlit-ui))
9. [File‑type handling & text extraction](https://github.com/gohbi/Keyword-Density-Analyzer/blob/main/README.md#-file-type-handling-&-text-execution)
10. [Configuration & Environment Variables](https://github.com/gohbi/Keyword-Density-Analyzer/blob/main/README.md#-configuration-&-Environment-Variables)
11. [Testing & Development Tips](https://github.com/gohbi/Keyword-Density-Analyzer/blob/main/README.md#-Testing-&-Development-Tips)
12. [Troubleshooting](https://github.com/gohbi/Keyword-Density-Analyzer/blob/main/README.md#-Troubleshooting)
13. [License & Credits](https://github.com/gohbi/Keyword-Density-Analyzer/blob/main/README.md#-License-&-Credits)


## 📄 Project Overview

Job‑search platforms and Applicant Tracking Systems (ATS) often rank resumes higher when the wording matches the job description, especially when certain keywords appear with a noticeable frequency.
This tool gives job seekers a fast, visual way to see which terms dominate their resume (or any other document) so they can:

 * Spot missing industry‑specific buzzwords.
 * Adjust the wording to increase keyword density where it matters.
 * Avoid over‑stuffing by seeing exact percentages.

The Keyword‑Density Analyzer is a Lumo‑powered micro‑service that:
    * Accepts a single uploaded file (plain‑text or common office formats).
    * Extracts plain‑text from the file in a robust, encoding‑aware way.
    * Tokenises the text with a lazily‑loaded spaCy model (en_core_web_sm).
    * Computes per‑word count and density (count / total_words * 100).
    * Returns a JSON list that the Streamlit UI renders as a sortable table.

All processing runs inside the container – no external APIs, no telemetry. Encryption is end‑to‑end (the file never leaves the container).


🎯 Why This Project Exists

1. **Showcase rapid learning** – I built the entire stack (PDF parsing, NLP, async API, GUI, Docker) from scratch, with the use of AI, while mastering the MERN‑style workflow in Python.
2. **Solve a real pain point** – Many candidates tweak their resumes blindly. By exposing the actual keyword density, the app empowers users to make data‑driven edits that align with ATS expectations.
3. **Demonstrate full‑stack competence** – Recruiters can see a clean, documented codebase, meaningful commit history, unit tests, and a deployable Docker image—all hallmarks of production‑ready software.

✨ Key Features
| ✅ Feature |	Description |
| --- | --- |
|Multi‑format support |	.txt (any encoding), .pdf, .docx, .odt. |
|Robust charset detection |	Uses chardet to fall back gracefully when a TXT file isn’t UTF‑8. |
|Dynamic minimum‑occurrence filter |	Streamlit slider (1 – 20) feeds the min_count query‑parameter to the backend, so the server only returns words that meet the threshold. |
|Zero‑access encryption |	All data stays inside the container; Lumo’s encryption layer protects the in‑memory state. |
|Fast, lightweight | The whole stack fits comfortably under the free tier on Render (≈ 150 MB RAM). |
|Extensible |	Text‑extraction logic lives in api/text_extractor.py; adding new formats is a single function addition. |
|Docker‑first |	One‑step build (docker build .) produces a ready‑to‑run image. |
|Health‑check endpoint |	Render’s auto‑restart uses GET /. |

🔨 Architecture
┌─────────────────────┐          ┌─────────────────────┐
│   Streamlit Front‑   │  HTTP    │   FastAPI Backend   │
│   end (UI)          │◀──────▶ │   (uvicorn)         │
│   - Slider (min)    │          │   - /analyze        │
│   - File uploader   │          │   - / (health)      │
│   - Dataframe view │          │   - text_extractor   │
└─────────────────────┘          └─────────────────────┘
          ▲                                 ▲
          │                                 │
          │ Docker container (single image) │
          └─────────────────────────────────┘
All components run in the same container, sharing the same virtual environment.


## 🚀 Getting Started (Local)

Prerequisites
    *Python 3.12+
    *Docker (optional, but recommended)
    *git

Clone the repo

    git clone https://github.com/yourorg/keyword-density-analyzer.git
    cd keyword-density-analyzer
Option A – Run with Docker (quickest)

    docker build -t keyword-analyzer .
    docker run -p 8501:8501 -p 8000:8000 \
      -e FASTAPI_PORT=8000 \
      keyword-analyzer

* Streamlit UI ->  http://localhost:8501
* FastAPI docs ->  http://localhost:8000/docs

Option B – Run locally without Docker

    # 1️⃣ Create a virtualenv
    python -m venv .venv
    source .venv/bin/activate   # Windows: .venv\Scripts\activate
    
    # 2️⃣ Install deps
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # 3️⃣ Download spaCy model (the Dockerfile does this automatically)
    python -m spacy download en_core_web_sm --quiet
    
    # 4️⃣ Start the backend
    uvicorn api.main:app --host 0.0.0.0 --port 8000 &
    # 5️⃣ Start the frontend
    streamlit run streamlit_app/app.py

    
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



📡 Deploying to Render (or any Docker host)
   1. Create a new “Web Service” on Render.
   2. Connect your GitHub repo (the same repo you cloned locally).
   3. Set the build command (Render detects the Dockerfile automatically).
   4. Runtime – leave the default (Docker).
   5. Environment variables (see § 9).
   6. Click “Create Web Service” – Render will build the image, run the container, and expose two ports:
        * 8501 → Streamlit UI (public URL)
        * 8000 → FastAPI (internal; not exposed publicly).

    uvicorn api.main:app --host 0.0.0.0 --port $FASTAPI_PORT &
    streamlit run streamlit_app/app.py --server.port $PORT


🎇 API Reference
| Method |	Path |	Query Params |	Request Body |	Description |
| --- | --- | --- | --- | --- |
| POST |	/analyze |	min_count (int, default = 3) |	multipart/form-data with field file (binary) |	Extracts text, tokenises, computes frequencies, returns only words whose count ≥ min_count. |
| GET |	/ |	— |	— |	Health‑check ({"status":"ok"}) – used by Render to confirm the service is alive. |
| GET |	/docs |	— |	— |	Interactive Swagger UI (auto‑generated). |

Response schema (List[Dict]):
    [
      {
        "word": "example",
        "count": 12,
        "density": 0.45   // percent of total words
      },
      …
    ]

🏆Frontend Details (Streamlit UI)

Key UI components (found in streamlit_app/app.py):
| Component |	Purpose |
| --- | --- |
| Slider (st.slider) |	Controls min_occurrences. The current value is passed to the backend via ?min_count= and also used for a client‑side safety filter. |
| File uploader (st.file_uploader) |	Accepts .txt, .pdf, .docx, .odt. Files larger than ~5 MB may cause a timeout (adjust timeout in httpx if needed). |
| Spinner (st.spinner) |	Shows progress while the request is in flight. |
| Dataframe view (st.dataframe) |	Displays the sorted frequency table; column count is descending. |
| Expander (st.expander) |	Shows the raw JSON payload for debugging. |
| Success / error alerts (st.success, st.error) |	Gives immediate feedback on request outcome. |

Dynamic behaviour – every time the slider moves or a new file is uploaded, Streamlit re‑runs the script, re‑fetches data from the backend, and updates the table automatically.


🧨 File‑type handling & Text Extraction

All heavy lifting lives in api/text_extractor.py. The public function:

    async def read_file(upload: UploadFile) -> str


   * Detects the file extension (.txt, .pdf, .docx, .odt).
   * Calls the appropriate private helper: _read_txt, _read_pdf, _read_docx, _read_odt.
   * For TXT files it first tries UTF‑8, then falls back to a charset guessed by chardet, finally decoding with errors="replace" to avoid crashes.
   * Unsupported extensions raise HTTPException(status_code=400, detail="Unsupported file type …").

Dependencies (added to requirements.txt):

    pdfminer.six==20240706
    python-docx==1.1.2
    odfpy==1.4.2
    chardet==5.2.0

These libraries are lightweight and have no external system dependencies, making the Docker image stay under 200 MB.


⚙ Configuration & Environment Variables
| Variable |	Default |	Description |
| --- | --- | --- |
| FASTAPI_PORT |	8000 |	Port on which the FastAPI server listens. Used by the Streamlit app to build the request URL. |
| MIN_WORD_COUNT |	3 |	Fallback minimum‑occurrence count if the UI does not supply a value. |
| PORT (Render) |	8501 |	Port on which Streamlit serves the UI. Render injects this automatically. |
| PYTHONUNBUFFERED |	1 |	Recommended for Docker logs (set in the Dockerfile). |

You can add more env vars (e.g., LOG_LEVEL) without touching the code – just read them via os.getenv.


🔧 Testing & Development Tips
    * Unit tests – place them under tests/. Example for the extractor:

    def test_txt_utf8(tmp_path):
        txt = tmp_path / "sample.txt"
        txt.write_bytes("hello world".encode("utf-8"))
        upload = UploadFile(filename=str(txt), file=open(txt, "rb"))
        assert asyncio.run(read_file(upload)) == "hello world"

* Integration test – spin up the FastAPI app with TestClient and POST a multipart request. Verify that min_count filters correctly.
* Live reload – when developing locally, run FastAPI with uvicorn api.main:app --reload. Streamlit automatically reloads on file changes.
* Debugging the backend – add logging.basicConfig(level=logging.DEBUG) at the top of api/main.py to see incoming requests in the console.


🛠️ Troubleshooting
| Symptom |	Likely cause |	Fix |
| --- | --- | --- |
| Invalid requirement: chardet=5.2.0 (Docker build fails) |	Wrong operator in requirements.txt. |	Use chardet==5.2.0 (double equals). |
| Unable to read uploaded file: 'utf-8' codec can't decode … |	Backend still using the old raw.decode('utf-8'). |	Ensure api/main.py calls await read_file(file) and that text_extractor.py is present. |
| No results displayed after uploading a PDF |	PDF extraction library not installed or PDF is encrypted. |	Confirm pdfminer.six is in the image; for encrypted PDFs you’ll need to decrypt beforehand (out of scope). |
| Slider value doesn’t affect the table |	The slider value isn’t passed to the backend. |	Verify analyze_file(..., min_cnt=min_occurrences) is used in app.py. |
| Container exits with “permission denied” on /tmp/lumo-output |	The user inside the container lacks write permission. |	The Dockerfile creates the directory as root before switching to a non‑root user; ensure the RUN mkdir -p /tmp/lumo-output && chown appuser:appuser /tmp/lumo-output line exists. |
| Render health‑check fails |	FastAPI didn’t start or crashed on import. |	Check Render logs; look for stack traces about missing modules (e.g., forgot to add a new dependency). |



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

📜 License & Credits


* License: MIT – feel free to fork, modify, and deploy.
* Core contributors:
    * Reanna Francis – architecture & backend.
    * AI – Streamlit UI & Docker integration.
* Third‑party libraries: spaCy, pdfminer.six, python‑docx, odfpy, chardet, FastAPI, Streamlit, httpx.
* Powered by: Lumo (Proton) – privacy‑first AI platform.


🎉 Ready to go!
    1. Clone → Build → Deploy (Docker or Render).
    2. Open the UI, upload a document, move the slider, and watch the word‑frequency table update in real time.

If you add new file formats, just extend api/text_extractor.py with a new helper and update the if ext == … dispatch block. The rest of the stack will pick it up automatically.


🙋‍♂️ Author

Reanna Francis – Passionate self-taught full‑stack developer focused on practical AI/NLP tools for career empowerment.
[GitHub Profile](https://github.com/gohbi) | [LinkedIn](www.linkedin.com/in/reannaf)


