mkdir -p scripts
cat > scripts/start.sh <<'EOS'
#!/usr/bin/env bash
set -euo pipefail

# FastAPI (uvicorn) in the background
/opt/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 &

# Streamlit in the foreground (keeps container alive)
/opt/venv/bin/streamlit run streamlit_app/app.py \
    --server.port 8501 \
    --server.headless true
EOS

# Make it executable locally (optional, Docker will chmod it anyway)
chmod +x scripts/start.sh

# *** VERY IMPORTANT *** Convert to Unix LF if you edited on Windows
# If you have dos2unix installed:
dos2unix scripts/start.sh

# If you don’t have dos2unix, you can use sed:
sed -i 's/\r$//' scripts/start.sh

git add scripts/start.sh
git commit -m "Add supervisor script"
git push


# Local test (optional)
docker build -t myapp:test .

# If you have Docker Desktop, you can run it locally to double‑check:
docker run --rm -p 8501:8501 myapp:test
# Visit http://localhost:8501 – you should see the Streamlit UI.

# Push to Render (or let Render pull from your repo)
git push origin main   # assuming Render watches this branch
