# -------------------------------------------------------------
# Stage 0 – Build a virtual‑env with all Python deps
# -------------------------------------------------------------
FROM python:3.12-slim AS builder

# Install OS build‑tools that some wheels may need
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libffi-dev python3-dev build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment that will be copied later
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install the exact versions you need
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------------------
# Stage 1 – Runtime image (tiny, no build‑tools)
# -------------------------------------------------------------
FROM python:3.12-slim

# Install tini – a minimal init system that forwards signals
# correctly (important for graceful shutdown on Render)
RUN apt-get update && apt-get install -y --no-install-recommends \
        tini ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual‑env from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create a non‑root user (good practice on Render)
RUN useradd -m appuser
USER appuser

# -----------------------------------------------------------------
# Application code
# -----------------------------------------------------------------
WORKDIR /app
COPY api ./api
COPY streamlit_app ./streamlit_app
COPY scripts/launch.sh /opt/launch.sh

# Make the script executable – we are still root at this point
# (the USER was set *after* the COPY, so this RUN runs as root)
RUN chmod +x /opt/launch.sh

# -----------------------------------------------------------------
# Tell Docker to use tini as PID‑1 and then run our launch script
# -----------------------------------------------------------------
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/opt/launch.sh"]
