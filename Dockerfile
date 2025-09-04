# -------------------------------------------------------------
# Stage 0 – Builder (install dependencies + spaCy model)
# -------------------------------------------------------------
FROM python:3.12-slim AS builder

# System packages needed for spaCy compilation (gcc, libffi, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libffi-dev python3-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# Virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python deps (including spaCy)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------------------
# Install the English core model into a known location
# -------------------------------------------------------------
RUN python -m spacy download en_core_web_sm && \
    # Create a folder that will be shipped with the runtime image
    mkdir -p /models/_spacy_models && \
    # Copy the installed model files into that folder
    cp -r $(python - <<'PY'\nimport en_core_web_sm, pathlib, sys; p=pathlib.Path(en_core_web_sm.__file__).parent; print(p)\nPY)/* /models/_spacy_models/

# -------------------------------------------------------------
# Stage 1 – Runtime (tiny)
# -------------------------------------------------------------
FROM python:3.12-slim

# tini for proper signal handling + ca‑certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
        tini ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy the virtual‑env from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the pre‑installed spaCy model into the location your code expects
COPY --from=builder /models/_spacy_models /app/api/_spacy_models

# -----------------------------------------------------------------
# Create the non‑root user (still root while we prepare files)
# -----------------------------------------------------------------
RUN useradd -m appuser && \
    # Give appuser ownership of the model folder (read‑only is fine)
    chown -R appuser:appuser /app/api/_spacy_models

# -----------------------------------------------------------------
# Copy the launch script (make it executable)
# -----------------------------------------------------------------
COPY --chmod=0755 scripts/launch.sh /opt/launch.sh

# -----------------------------------------------------------------
# Copy the rest of the application code
# -----------------------------------------------------------------
WORKDIR /app
COPY api ./api
COPY streamlit_app ./streamlit_app

# -----------------------------------------------------------------
# Drop privileges for the rest of the image
# -----------------------------------------------------------------
USER appuser

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/opt/launch.sh"]
