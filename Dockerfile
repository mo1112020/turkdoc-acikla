FROM python:3.12-slim-bookworm

# Tesseract for photo/PDF OCR (Turkish + English)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-tur \
        tesseract-ocr-eng \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --- Layer 1: Python deps only (cached until requirements.txt changes) ---
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- Layer 2: App code (rebuilds fast when you change code) ---
COPY pyproject.toml README.md LICENSE ./
COPY turkdoc/ turkdoc/
COPY backend/ backend/
COPY frontend/ frontend/
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
    && mkdir -p /app/data/uploads

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    HOST=0.0.0.0 \
    RELOAD=false \
    ENVIRONMENT=production

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${PORT:-8000}/health" || exit 1

ENTRYPOINT ["/entrypoint.sh"]
