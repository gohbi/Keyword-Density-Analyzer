# -------------------------------------------------------------
# Stage 0 – Build the virtual‑env (unchanged)
# -------------------------------------------------------------
FROM python:3.12-slim AS builder

COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------------------
# Stage 1 – Runtime image (tiny)
# -------------------------------------------------------------
FROM python:3.12-slim

# tini for proper signal handling + ca‑certificates (needed by many libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
        tini ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------
# Copy the virtual‑env from the builder stage
# -----------------------------------------------------------------
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# -----------------------------------------------------------------
# Create the non‑root user (still root while we prepare files)
# -----------------------------------------------------------------
RUN useradd -m appuser

# -----------------------------------------------------------------
# Give appuser ownership of the whole /app/api tree
# -----------------------------------------------------------------
RUN mkdir -p /app/api && \
    chown -R appuser:appuser /app/api

# -----------------------------------------------------------------
# Copy the launch script **and make it executable**
# -----------------------------------------------------------------
#   • The script must be in the repository at `scripts/launch.sh`
#   • `--chmod=0755` sets the executable bit while the copy runs as root
#   • Using `COPY --chmod` also guarantees Unix LF line endings
COPY --chmod=0755 scripts/launch.sh /opt/launch.sh

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
# Entrypoint – tini forwards signals, launch.sh starts both services
# -----------------------------------------------------------------
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/opt/launch.sh"]
