# ---- Builder stage ---------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build‑time deps (gcc, libffi…) only if needed for wheels
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---- Runtime stage ---------------------------------------------------------
FROM python:3.12-slim

WORKDIR /app

# Copy only the installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy our source code
COPY api ./api
COPY tmp_uploads ./tmp_uploads   
# empty folder, will be created at runtime

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
