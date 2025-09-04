# -------------------------------------------------
# Stage 1 – Builder: install OS deps, create venv,
#               install Python packages
# -------------------------------------------------
FROM python:3.12-slim AS builder

# Install system packages needed for:
#    • the Python venv module (python3-venv)
#    • building any wheels that may require a compiler
#    • basic CA certificates for HTTPS
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
        python3-dev \
        python3-venv \   # <-- crucial for `python -m venv`
        build-essential \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual‑env in a known location
RUN python3 -m venv /opt/venv

# Upgrade pip inside the venv (ensures we have the latest resolver)
RUN /opt/venv/bin/python -m pip install --upgrade pip

# Copy only the files needed for dependency installation
WORKDIR /app
COPY requirements.txt .
COPY .dockerignore .

# Install Python dependencies.
#    • `--no-cache-dir` keeps the layer small.
#    • `--only-binary=:all:` forces binary wheels (avoids source builds).
RUN /opt/venv/bin/pip install --no-cache-dir --only-binary=:all: -r requirements.txt

# -------------------------------------------------
# Stage 2 – Runtime: tiny image, just the venv and code
# -------------------------------------------------
FROM python:3.12-slim

# Runtime OS packages (only what the app needs)
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy the prepared virtual‑env from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Create a non‑root user (Render prefers this)
RUN useradd -m appuser
USER appuser

# Working directory for the application code
WORKDIR /app

# Copy only the source code (nothing else)
COPY api ./api

# Expose the port Render expects (the app will listen on 0.0.0.0:8000)
EXPOSE 8000

# Entrypoint / CMD – start FastAPI with uvicorn from the venv
ENTRYPOINT ["/opt/venv/bin/uvicorn"]
CMD ["api.main:app", "--host", "0.0.0.0", "--port", "8000"]
