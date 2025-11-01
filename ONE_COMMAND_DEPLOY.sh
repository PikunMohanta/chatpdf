#!/bin/bash
# ⚡ ONE COMMAND DEPLOYMENT - Copy and paste this entire block into your EC2 terminal

cd ~/apps/chatpdf && \
  echo "📥 Pulling latest code..." && \
  git pull origin docker-deployment && \
  echo "🛑 Stopping old containers..." && \
  docker-compose down -v && \
  echo "🧹 Cleaning Docker..." && \
  docker system prune -af && \
  echo "🔨 Building new image (5-10 minutes)..." && \
  docker-compose build --no-cache app && \
  echo "🚀 Starting services..." && \
  docker-compose up -d && \
  echo "⏳ Waiting 60 seconds for startup..." && \
  sleep 60 && \
  echo "✅ Checking status..." && \
  docker-compose ps && \
  echo "" && \
  echo "🏥 Testing health..." && \
  curl http://localhost/health && \
  echo "" && \
  echo "" && \
  echo "🎉 Deployment complete!"
