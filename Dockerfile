# -------------------------------------------------------------
# Stage 0 – Builder (install dependencies + spaCy model)
# -------------------------------------------------------------
FROM python:3.12-slim AS builder

# System packages needed for spaCy compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libffi-dev python3-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies (including spaCy)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------------------
# Install the English core model into a known location
# -------------------------------------------------------------
RUN python -m spacy download en_core_web_sm && \
    mkdir -p /models/_spacy_models && \
    cp -r $(python - <<'PY'
import en_core_web_sm, pathlib, sys
print(pathlib.Path(en_core_web_sm.__file__).parent)
PY
)/* /models/_spacy_models/

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
    chown -R appuser:appuser /app/api/_spacy_models

# -----------------------------------------------------------------
# Copy the launch script (make it executable)
# -----------------------------------------------------------------
COPY --chmod=0755 scripts/launch.sh /opt/launch.sh

# -----------------------------------------------------------------
# Copy the application source code
# -----------------------------------------------------------------
WORKDIR /app
COPY api ./api
COPY streamlit_app ./streamlit_app

# -----------------------------------------------------------------
# Drop privileges for the rest of the image
# -----------------------------------------------------------------
USER appuser

# -----------------------------------------------------------------
# Entrypoint – tini forwards signals, launch.sh starts both services
# -----------------------------------------------------------------
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/opt/launch.sh"]
