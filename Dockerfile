# ---------- Stage 1: Build ----------
FROM python:3.12-slim AS builder

# Install OS deps needed for building wheels (gcc, libffi, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a non‑root user (Render recommends this)
RUN useradd -m appuser

# Set workdir for the builder
WORKDIR /app

# Copy only the files needed for installing deps
COPY requirements.txt .
COPY .dockerignore .

# Install Python deps into a virtual‑env inside the image
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -vvv -r requirements.txt

# ---------- Stage 2: Runtime ----------
FROM python:3.12-slim

# OS deps required at runtime (none for this project, but keep it minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy the venv from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Create a non‑root user (same UID/GID as builder)
RUN useradd -m appuser
USER appuser

# Set workdir for the runtime container
WORKDIR /app

# Copy only the source code (skip venv, tests, etc.)
COPY api ./api

# Expose the port Render expects (default 10000 → we forward to 8000)
EXPOSE 8000

# Startup command – Render will run this as PID 1
ENTRYPOINT ["/opt/venv/bin/uvicorn"]
CMD ["api.main:app", "--host", "0.0.0.0", "--port", "8000"]
