# -------------------------------------------------------------
# Stage 0 – Build the virtual‑env with all Python deps
# -------------------------------------------------------------
FROM python:3.12-slim AS builder

COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------------------
# Stage 1 – Runtime image (tiny, no build‑tools)
# -------------------------------------------------------------
FROM python:3.12-slim

# tini gives us a proper PID‑1 and signal forwarding
RUN apt-get update && apt-get install -y --no-install-recommends tini ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy the prepared virtual‑env
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# -----------------------------------------------------------------
# Create a non‑root user (still root while we copy files)
# -----------------------------------------------------------------
RUN useradd -m appuser

# -----------------------------------------------------------------
# Copy the launch script **and** set executable bit in one go
# -----------------------------------------------------------------
COPY --chmod=0755 scripts/launch.sh /opt/launch.sh

# -----------------------------------------------------------------
# Switch to the non‑root user for the rest of the image
# -----------------------------------------------------------------
USER appuser

# -----------------------------------------------------------------
# Application code
# -----------------------------------------------------------------
WORKDIR /app
COPY api ./api
COPY streamlit_app ./streamlit_app

# -----------------------------------------------------------------
# Entrypoint – tini forwards signals, launch.sh starts both services
# -----------------------------------------------------------------
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/opt/launch.sh"]
