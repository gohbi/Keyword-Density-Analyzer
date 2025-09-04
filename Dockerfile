# -------------------------------------------------
# Stage 1 – Builder (install OS deps, create venv)
# -------------------------------------------------
FROM python:3.12-slim AS builder

# OS packages needed for Python venv + compiled wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    python3-dev \
    python3-venv \
    build-essential \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python3 -m venv /opt/venv

# Upgrade pip inside the venv
RUN /opt/venv/bin/python -m pip install --upgrade pip

# Copy only the files needed for dependency installation
WORKDIR /app
COPY requirements.txt .
COPY .dockerignore .

# Install all Python dependencies (FastAPI + Streamlit)
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------
# Stage 2 – Runtime (tiny image, just the venv + code)
# -------------------------------------------------
FROM python:3.12-slim

# Runtime OS packages (only CA certs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Create a non‑root user (Render recommendation)
RUN useradd -m appuser
USER appuser

# Working directory for our code
WORKDIR /app

# Copy the source code (FastAPI + Streamlit)
COPY api ./api
COPY streamlit_app ./streamlit_app

# Expose the ports Render will forward:
#   8000 – FastAPI (internal only)
#   8501 – Streamlit (public UI)
EXPOSE 8000
EXPOSE 8501

# -------------------------------------------------
# Supervisor script – launches both processes
# -------------------------------------------------
# NOTE: The closing EOF must be on a line by itself with NO whitespace.
RUN cat <<'EOF' > /opt/start.sh
#!/usr/bin/env bash
set -euo pipefail
/opt/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 &
/opt/venv/bin/streamlit run streamlit_app/app.py --server.port 8501 --server.headless true
EOF

# Make it executable
RUN chmod +x /opt/start.sh

# Default command – Render will execute this
ENTRYPOINT ["/opt/start.sh"]
