#!/usr/bin/env bash
# ---------------------------------------------------------
# launch.sh – starts FastAPI (uvicorn) in the background
#            and then runs Streamlit in the foreground.
#
# Render injects the environment variable PORT (e.g. 10000).
# Streamlit must listen on that port, otherwise Render cannot
# forward traffic to the UI.
# ---------------------------------------------------------

set -euo pipefail   # fail fast on any error

# -----------------------------------------------------------------
#   Start FastAPI (uvicorn) on an internal port (8000)
#    It runs in the background because Streamlit needs the PID‑1
#    process to stay alive.
# -----------------------------------------------------------------
/opt/venv/bin/uvicorn api.main:app \
    --host 0.0.0.0 \
    --port 8000 &
UVICORN_PID=$!

# -----------------------------------------------------------------
#   Start Streamlit on the port Render gave us.
#    $PORT is guaranteed to be set by Render for web services.
# -----------------------------------------------------------------
/opt/venv/bin/streamlit run streamlit_app/app.py \
    --server.port "${PORT:-8501}" \   # fallback to 8501 for local testing
    --server.headless true

# -----------------------------------------------------------------
# When Streamlit exits (e.g. container stopped), kill uvicorn so we
# don’t leave orphan processes behind.
# -----------------------------------------------------------------
kill "$UVICORN_PID" 2>/dev/null || true
