# -------------------------------------------------
# Stage 1 – build the virtual environment with deps
# -------------------------------------------------
FROM python:3.12-slim AS builder

# Install OS packages needed to compile wheels (gcc, libffi, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
        build-essential \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN /opt/venv/bin/pip install --only-binary=:all: -r requirements.txt

# Create a non‑root user (Render likes this)
RUN useradd -m appuser

# Working directory for the builder
WORKDIR /app

# Copy only the files needed for installing dependencies
COPY requirements.txt .
COPY .dockerignore .

# Create a virtual‑env inside the image and install deps
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------
# Stage 2 – runtime image (tiny)
# -------------------------------------------------
FROM python:3.12-slim

# Runtime OS packages (only what we need)
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual‑env from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Create the same non‑root user
RUN useradd -m appuser
USER appuser

# Set workdir for the app code
WORKDIR /app

# Copy only the source code (nothing else)
COPY api ./api

# Expose the port Render expects (the app will listen on 8000)
EXPOSE 8000

# Entrypoint / CMD – start FastAPI with uvicorn
ENTRYPOINT ["/opt/venv/bin/uvicorn"]
CMD ["api.main:app", "--host", "0.0.0.0", "--port", "8000"]
