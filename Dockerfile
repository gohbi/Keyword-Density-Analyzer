# -------------------------------------------------------------
# Stage 0 – Builder (install everything, including the model)
# -------------------------------------------------------------
FROM python:3.12-slim AS builder

# Packages needed to compile wheels (gcc, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libffi-dev python3-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# Virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies (model is now a normal package)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------------------
# Stage 1 – Runtime (tiny)
# -------------------------------------------------------------
FROM python:3.12-slim

# tini for proper signal handling + ca‑certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
        tini ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Bring the virtual environment (includes spaCy + model) into the runtime image
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create a non‑root user
RUN useradd -m appuser

# Copy launch script (make it executable)
COPY --chmod=0755 scripts/launch.sh /opt/launch.sh

# Copy the application code
WORKDIR /app
COPY api ./api
COPY streamlit_app ./streamlit_app

# <<< NEW: give appuser ownership of everything that will be written at runtime >>>
RUN mkdir -p /app/api/_spacy_models && \
    chown -R 1000:1000 /app/api/_spacy_models && \
    chown -R 1000:1000 /app/api   # optional – makes the whole api tree writable

# Create the non‑root user *after* the chown so the UID/GID match
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Run as the non‑root user
USER appuser

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/opt/launch.sh"]
