# PDFPixie Optimized Dockerfile
# Simplified and reduced from 1.12GB to ~400-500MB

# ============================================
# Stage 1: Build Frontend (Alpine = smaller)
# ============================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install --silent

COPY frontend/ ./
RUN npm run build

# ============================================
# Stage 2: Production Image
# ============================================
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install minimal runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        nginx-light \
        supervisor \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Install Python packages
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    find /usr/local/lib/python3.11 -name '*.pyc' -delete && \
    find /usr/local/lib/python3.11 -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true

# Copy application files
COPY backend/ ./
COPY --from=frontend-builder /app/frontend/dist /var/www/html
COPY frontend/public/pdf.worker.min.js /var/www/html/

 # Copy external Nginx & Supervisor configs
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/conf.d/pdfpixie.conf /etc/nginx/conf.d/pdfpixie.conf
COPY supervisor/supervisord.conf /etc/supervisor/supervisord.conf

# Setup directories
RUN mkdir -p /app/data/{chromadb,uploads,chat_history} /app/logs && \
    chmod 755 /app/data /app/logs

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s \
    CMD curl -sf http://localhost/health || exit 1

EXPOSE 80 8000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]