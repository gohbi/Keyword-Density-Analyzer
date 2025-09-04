#!/usr/bin/env bash
#=====================================================================
# scripts/launch.sh
#
# Entry‑point for the Lumo container.
#   • Starts FastAPI (uvicorn) on $PORT (default 8501)
#   • Starts Streamlit on a second port (8502) – optional UI
#   • Handles SIGTERM/SIGINT so Docker can stop the container cleanly
#   • Exits with the status of the process that terminates first
#
# The script is copied into the image with:
#   COPY --chmod=0755 scripts/launch.sh /opt/launch.sh
#=====================================================================

set -euo pipefail   # abort on error, undefined vars, and pipe failures

# --------------------------------------------------------------------
# Helper: print a timestamped log line (helps when you look at container logs)
# --------------------------------------------------------------------
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') | $*"
}

# --------------------------------------------------------------------
# Resolve the port on which FastAPI should listen.
# Render injects $PORT; when running locally we fall back to 8501.
# --------------------------------------------------------------------
FASTAPI_PORT="${PORT:-8501}"
STREAMLIT_PORT=8502   # fixed – you can change it if you wish

log "🚀 Starting Lumo services"
log "🔧 FastAPI will listen on 0.0.0.0:${FASTAPI_PORT}"
log "🔧 Streamlit will listen on 0.0.0.0:${STREAMLIT_PORT}"

# --------------------------------------------------------------------
# 1️⃣ Start FastAPI (uvicorn)
# --------------------------------------------------------------------
uvicorn api.main:app \
    --host 0.0.0.0 \
    --port "${FASTAPI_PORT}" \
    --workers 2 \
    --log-level info &
FASTAPI_PID=$!
log "✅ FastAPI launched (PID ${FASTAPI_PID})"

# --------------------------------------------------------------------
# 2️⃣ Start Streamlit (optional UI)
# --------------------------------------------------------------------
# If you don't need Streamlit, you can comment out the block below.
streamlit run streamlit_app/app.py \
    --server.port "${STREAMLIT_PORT}" \
    --server.headless true \
    --browser.serverAddress "0.0.0.0" \
    --browser.gatherUsageStats false &
STREAMLIT_PID=$!
log "✅ Streamlit launched (PID ${STREAMLIT_PID})"

# --------------------------------------------------------------------
# 3️⃣ Signal handling – forward SIGTERM/SIGINT to child processes
# --------------------------------------------------------------------
_term() {
    log "⚡ Received termination signal – stopping children"
    kill -TERM "${FASTAPI_PID}" 2>/dev/null || true
    kill -TERM "${STREAMLIT_PID}" 2>/dev/null || true
}
trap _term SIGTERM SIGINT

# --------------------------------------------------------------------
# 4️⃣ Wait for *any* child to exit.
#    `wait -n` (available in Bash ≥4.3) returns as soon as the first
#    background job finishes. We then propagate its exit code.
# --------------------------------------------------------------------
wait -n
EXIT_CODE=$?
log "🛑 One of the services exited (code ${EXIT_CODE}) – shutting down"

# Give the other process a chance to shut down cleanly
kill -TERM "${FASTAPI_PID}" 2>/dev/null || true
kill -TERM "${STREAMLIT_PID}" 2>/dev/null || true
wait "${FASTAPI_PID}" 2>/dev/null || true
wait "${STREAMLIT_PID}" 2>/dev/null || true

log "👋 Lumo container exiting with code ${EXIT_CODE}"
exit "${EXIT_CODE}"
