# -------------------------------------------------------------
# Stage 0 – Build the virtual‑env (unchanged)
# -------------------------------------------------------------
FROM python:3.12-slim AS builder
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------------------
# Stage 1 – Runtime image
# -------------------------------------------------------------
FROM python:3.12-slim

# tini for proper signal handling
RUN apt-get update && apt-get install -y --no-install-recommends \
        tini ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy the virtual‑env from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# -----------------------------------------------------------------
# Create the non‑root user (still root while we prepare files)
# -----------------------------------------------------------------
RUN useradd -m appuser

# -----------------------------------------------------------------
# Pre‑create the spaCy model directory and give ownership
# -----------------------------------------------------------------
RUN mkdir -p /app/api/_spacy_models && \
    chown -R appuser:appuser /app/api/_spacy_models

# -----------------------------------------------------------------
# Copy the application code (still root)
# -----------------------------------------------------------------
WORKDIR /app
COPY api ./api
COPY streamlit_app ./streamlit_app

# -----------------------------------------------------------------
# Drop privileges for the rest of the image
# -----------------------------------------------------------------
USER appuser

# -----------------------------------------------------------------
# Launch script (tini forwards signals)
# -----------------------------------------------------------------
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/opt/launch.sh"]
