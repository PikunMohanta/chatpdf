#!/bin/bash
set -e

echo "================================================"
echo "🚀 Starting PDFPixie services..."
echo "================================================"

# Create required directories
echo "📁 Creating required directories..."
mkdir -p /app/data/chromadb /app/data/uploads /app/data/chat_history /app/data/database /app/logs
chmod -R 755 /app/data /app/logs
echo "✅ Directories created"

# Test Python imports
echo "🐍 Testing Python environment..."
cd /app
python3 -c "import fastapi, socketio, uvicorn; print('✅ Core dependencies OK')" || {
    echo "❌ Failed to import core dependencies"
    exit 1
}

# Test database initialization
echo "💾 Testing database initialization..."
python3 -c "from app.database import init_db; init_db(); print('✅ Database initialized')" || {
    echo "❌ Failed to initialize database"
    exit 1
}

# Check environment variables
echo "🔑 Checking environment variables..."
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "⚠️  WARNING: OPENROUTER_API_KEY not set"
fi
echo "   DATABASE_URL: ${DATABASE_URL:-not set}"
echo "   REDIS_URL: ${REDIS_URL:-not set}"
echo "   ENVIRONMENT: ${ENVIRONMENT:-not set}"

# Start Nginx in background
echo "🌐 Starting Nginx..."
nginx -t && nginx || {
    echo "❌ Nginx failed to start"
    cat /var/log/nginx/error.log
    exit 1
}
echo "✅ Nginx started on port 80"

# Give Nginx a moment to start
sleep 2

# Test Nginx
echo "🧪 Testing Nginx..."
curl -sf http://localhost:80/ > /dev/null && echo "✅ Nginx responding" || echo "⚠️  Nginx not responding yet"

# Start FastAPI (this runs in foreground)
echo "🚀 Starting FastAPI on port 8000..."
echo "================================================"
cd /app
exec uvicorn main:socket_app --host 0.0.0.0 --port 8000 --workers 1 --log-level info
