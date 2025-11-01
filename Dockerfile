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

# Create Nginx config
RUN cat > /etc/nginx/sites-available/default <<'NGINX'
server {
    listen 80;
    root /var/www/html;
    client_max_body_size 50M;
    gzip on;
    gzip_types text/css application/javascript;
    
    location / { try_files $uri /index.html; }
    location /api/ { 
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_buffering off;
    }
    location ~ ^/(upload|health|pdf) { 
        proxy_pass http://127.0.0.1:8000;
    }
    location /socket.io/ {
        proxy_pass http://127.0.0.1:8000/socket.io/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
        proxy_read_timeout 86400;
    }
}
NGINX

# Create startup script (replaces supervisor)
RUN cat > /app/start.sh <<'STARTSH'
#!/bin/bash
set -e

echo "Starting PDFPixie services..."

# Start Nginx in background
echo "Starting Nginx..."
nginx &

# Start FastAPI (this runs in foreground)
echo "Starting FastAPI..."
cd /app
exec uvicorn main:socket_app --host 0.0.0.0 --port 8000 --workers 1
STARTSH

RUN chmod +x /app/start.sh

# Setup directories
RUN mkdir -p /app/data/{chromadb,uploads,chat_history} /app/logs && \
    chmod 755 /app/data /app/logs

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s \
    CMD curl -sf http://localhost/health || exit 1

EXPOSE 80 8000

CMD ["/app/start.sh"]