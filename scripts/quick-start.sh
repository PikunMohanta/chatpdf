#!/bin/bash

# Quick development start script using UV
# This script starts the development environment quickly

set -e

echo "🚀 Quick start with UV - Starting Newchat development..."

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "📦 UV not found. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    echo "✅ UV installed successfully!"
fi

# Backend setup
echo "🐍 Setting up backend with UV..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment with UV..."
    uv venv
fi

# Activate and install dependencies
echo "Installing dependencies with UV (this will be fast!)..."
source .venv/bin/activate
uv pip install -r requirements.txt

# Copy environment file if needed
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Created .env file - please update with your API keys!"
fi

cd ..

# Start services in background
echo "🐳 Starting development services..."
docker-compose -f docker-compose.dev.yml up -d

echo "⏳ Waiting for services to be ready..."
sleep 5

echo ""
echo "🎉 Quick start complete!"
echo ""
echo "Next steps:"
echo "1. Backend: cd backend && source .venv/bin/activate && uvicorn main:socket_app --reload"
echo "2. Frontend: cd frontend && npm install && npm start"
echo ""
echo "Services:"
echo "- Backend API: http://localhost:8000"
echo "- Frontend: http://localhost:3000"
echo "- API Docs: http://localhost:8000/docs"
echo ""
echo "⚡ UV made dependency installation 10-100x faster!"