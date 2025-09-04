#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------
# Ports
# ------------------------------------------------------------
# Render injects the public port in $PORT.
# We will bind Streamlit to that port (the UI the user sees).
export STREAMLIT_PORT="${PORT}"               # <-- MUST be $PORT on Render
# Choose any free internal port for FastAPI – it does NOT need to be exposed.
export FASTAPI_PORT="${FASTAPI_PORT:-8000}"   # default 8000 if you run locally

# ------------------------------------------------------------
# Start FastAPI (background)
# ------------------------------------------------------------
uvicorn api.main:app \
    --host 0.0.0.0 \
    --port "$FASTAPI_PORT" &
FASTAPI_PID=$!

# ------------------------------------------------------------
# Start Streamlit (foreground)
# ------------------------------------------------------------
streamlit run streamlit_app/app.py \
    --server.port "$STREAMLIT_PORT" \
    --server.headless true \
    --browser.serverAddress 0.0.0.0 \
    --browser.gatherUsageStats false

# ------------------------------------------------------------
# When Streamlit exits, forward its exit code (clean shutdown)
# ------------------------------------------------------------
wait $FASTAPI_PID || exit $?
