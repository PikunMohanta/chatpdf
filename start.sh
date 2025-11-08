#!/bin/bash
# PDFPixie Startup Script for Docker
# Runs Nginx and FastAPI together

set -e

echo "========================================"
echo "PDFPixie Starting..."
echo "========================================"

# Ensure data directories exist with proper permissions
echo "Creating data directories..."
mkdir -p /app/data/chromadb
mkdir -p /app/data/uploads
mkdir -p /app/data/chat_history
mkdir -p /app/data/database
mkdir -p /app/data/mock_embeddings
mkdir -p /app/logs

chmod -R 755 /app/data
chmod -R 755 /app/logs

echo "Data directories ready"

# Start Nginx in background
echo "Starting Nginx..."
nginx -g 'daemon off;' &
NGINX_PID=$!
echo "Nginx started (PID: $NGINX_PID)"

# Wait a moment for Nginx to start
sleep 2

# Start FastAPI with uvicorn
echo "Starting FastAPI backend..."
cd /app
exec uvicorn main:socket_app \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info \
    --access-log \
    --use-colors
