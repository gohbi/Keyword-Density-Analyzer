# ==============================================================
#  Stage 0 – Builder (install everything, including the spaCy model)
# ==============================================================

FROM python:3.12-slim AS builder

# Packages needed to compile wheels (gcc, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libffi-dev python3-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment that will be shipped to the runtime image
RUN python -m venv /opt/venv

# Activate the venv for the rest of the build stage
ENV PATH="/opt/venv/bin:$PATH"

# -----------------------------------------------------------------
# Install Python dependencies (including the spaCy model)
# -----------------------------------------------------------------
COPY requirements.txt .
# NOTE: make sure `streamlit` is listed in requirements.txt,
# e.g.   streamlit==1.38.0
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    # <<< NEW LINE >>> Download the English model into the container
    python -m spacy download en_core_web_sm --direct --quiet \
        --target /opt/venv/lib/python3.12/site-packages/_spacy_models


# ==============================================================
#  Stage 1 – Runtime (tiny)
# ==============================================================

FROM python:3.12-slim

# tini for proper signal handling + ca‑certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
        tini ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------
# Bring the virtual environment (includes spaCy + model) into the runtime image
# -----------------------------------------------------------------
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"


# ----- NEW: tell spaCy where the bundled model lives --------------------
ENV SPACY_DATA="/opt/venv/lib/python3.12/site-packages/_spacy_models"

# -----------------------------------------------------------------
# Create a **single** non‑root system user (no home, no login shell)
# -----------------------------------------------------------------
RUN groupadd -r appuser && \
    useradd -r -g appuser appuser

# -----------------------------------------------------------------
# Copy launch script (make it executable)
# -----------------------------------------------------------------
COPY --chmod=0755 scripts/launch.sh /opt/launch.sh

# -----------------------------------------------------------------
# Copy the application code
# -----------------------------------------------------------------
WORKDIR /app
COPY api ./api
COPY streamlit_app ./streamlit_app

# -----------------------------------------------------------------
# Do NOT expose ports on Render – the platform injects $PORT.
# Keeping EXPOSE is harmless for local testing, but it can be confusing.
# -----------------------------------------------------------------
# EXPOSE 8501 8502   <-- comment/remove if you prefer absolute clarity

# -----------------------------------------------------------------
# Give the newly‑created user ownership of everything it may write to
# -----------------------------------------------------------------
# The directory that FastAPI creates at start‑up (spaCy models cache)
RUN mkdir -p /app/api/_spacy_models && \
    chown -R appuser:appuser /app/api/_spacy_models && \
    # (optional) make the whole api tree writable – useful if you ever
    # generate additional files under /app/api at runtime
    chown -R appuser:appuser /app/api

# -----------------------------------------------------------------
# Drop privileges – run everything as the non‑root user
# -----------------------------------------------------------------
USER appuser

# -----------------------------------------------------------------
# Entrypoint / CMD – tini handles signals, launch.sh starts both services
# -----------------------------------------------------------------
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/opt/launch.sh"]
