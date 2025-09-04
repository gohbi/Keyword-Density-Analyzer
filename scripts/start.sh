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

# If you don’t have dos2unix, you can use sed:
sed -i 's/\r$//' scripts/start.sh

git add scripts/start.sh
git commit -m "Add supervisor script"
git push


