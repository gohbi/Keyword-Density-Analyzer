# -------------------------------------------------------------
# Stage 0 – Builder (install spaCy model)
# -------------------------------------------------------------
FROM python:3.12-slim AS builder

# Install system deps needed by spaCy (usually just gcc, libffi, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libffi-dev python3-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

# Virtual env
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python deps (including spaCy)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install the English core model into a known location
RUN python -m spacy download en_core_web_sm && \
    # Move the model to the folder we will ship with the image
    mkdir -p /models/_spacy_models && \
    cp -r $(python -c "import en_core_web_sm, pathlib; print(pathlib.Path(en_core_web_sm.__file__).parent)")/* /models/_spacy_models/

# -------------------------------------------------------------
# Stage 1 – Runtime (tiny)
# -------------------------------------------------------------
FROM python:3.12-slim

# tini for signal handling
RUN apt-get update && apt-get install -y --no-install-recommends tini ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy the virtual env
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the pre‑downloaded model
COPY --from=builder /models/_spacy_models /app/api/_spacy_models

# Create non‑root user
RUN useradd -m appuser && \
    chown -R appuser:appuser /app/api/_spacy_models

WORKDIR /app
COPY api ./api
COPY streamlit_app ./streamlit_app

USER appuser

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/opt/launch.sh"]
