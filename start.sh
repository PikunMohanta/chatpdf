#!/bin/bash
# Production start script for PDFPixie backend on Render

echo "🚀 Starting PDFPixie Backend on Render"
echo "Environment: $ENVIRONMENT"
echo "Port: $PORT"

# Navigate to backend directory
cd backend

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Initialize database
echo "💾 Initializing database..."
python -c "from app.database import init_db; init_db(); print('Database initialized successfully')"

# Start the server
echo "🌟 Starting FastAPI server..."
python -m uvicorn main:socket_app --host 0.0.0.0 --port $PORT