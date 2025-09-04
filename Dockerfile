# -------------------------------------------------
# Stage 1 – Builder (install OS deps, create venv)
# -------------------------------------------------
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev python3-dev python3-venv build-essential ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/python -m pip install --upgrade pip

WORKDIR /app
COPY requirements.txt .
COPY .dockerignore .
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------
# Stage 2 – Runtime (tiny image, just the venv + code)
# -------------------------------------------------
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

RUN useradd -m appuser
USER appuser

WORKDIR /app
COPY api ./api
COPY streamlit_app ./streamlit_app
COPY scripts/start.sh /opt/start.sh
RUN chmod +x /opt/start.sh

EXPOSE 8000
EXPOSE 8501

ENTRYPOINT ["/opt/start.sh"]
