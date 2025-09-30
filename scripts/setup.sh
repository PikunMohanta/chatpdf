#!/bin/bash

# Setup script for Newchat development environment
# This script sets up the local development environment

set -e

echo "🚀 Setting up Newchat development environment..."

# Check if required tools are installed
check_requirements() {
    echo "📋 Checking requirements..."
    
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    if ! command -v python &> /dev/null; then
        echo "❌ Python is not installed. Please install Python 3.10+ first."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    echo "✅ All requirements are met!"
}

# Setup backend
setup_backend() {
    echo "🐍 Setting up backend..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "env" ]; then
        echo "Creating Python virtual environment..."
        python -m venv env
    fi
    
    # Install UV if not present
    if ! command -v uv &> /dev/null; then
        echo "Installing UV..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
    
    # Check Python version
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo "🐍 Detected Python version: $python_version"
    
    # Create virtual environment with UV
    echo "Creating virtual environment with UV..."
    uv venv --python python3
    
    # Activate virtual environment
    echo "Activating virtual environment..."
    source .venv/bin/activate
    
    # Install dependencies
    echo "Installing Python dependencies with UV (faster)..."
    echo "Note: Using ChromaDB instead of FAISS for Python 3.13 compatibility"
    uv pip install -r requirements.txt
    
    # Copy environment file
    if [ ! -f ".env" ]; then
        echo "Creating backend .env file..."
        cp .env.example .env
        echo "⚠️  Please update the .env file with your actual API keys and configuration!"
    fi
    
    cd ..
    echo "✅ Backend setup complete!"
}

# Setup frontend
setup_frontend() {
    echo "⚛️ Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    echo "Installing Node.js dependencies..."
    npm install
    
    # Create environment file
    if [ ! -f ".env" ]; then
        echo "Creating frontend .env file..."
        echo "REACT_APP_API_URL=http://localhost:8000" > .env
        echo "REACT_APP_SOCKET_URL=http://localhost:8000" >> .env
    fi
    
    cd ..
    echo "✅ Frontend setup complete!"
}

# Setup database and services
setup_services() {
    echo "🐳 Setting up development services..."
    
    # Start development services
    echo "Starting PostgreSQL and Redis..."
    docker-compose -f docker-compose.dev.yml up -d
    
    # Wait for services to be ready
    echo "Waiting for services to be ready..."
    sleep 10
    
    echo "✅ Development services are running!"
    echo "📊 PGAdmin: http://localhost:5050 (admin@newchat.dev / admin)"
    echo "🔧 Redis Commander: http://localhost:8081"
}

# Create necessary directories
create_directories() {
    echo "📁 Creating necessary directories..."
    
    mkdir -p backend/data/indexes
    mkdir -p backend/logs
    mkdir -p logs
    
    echo "✅ Directories created!"
}

# Main setup
main() {
    check_requirements
    create_directories
    setup_backend
    setup_frontend
    setup_services
    
    echo ""
    echo "🎉 Setup complete!"
    echo ""
    echo "To start development:"
    echo "1. Backend: cd backend && source env/bin/activate && uvicorn main:socket_app --reload"
    echo "2. Frontend: cd frontend && npm start"
    echo ""
    echo "Services running:"
    echo "- Backend API: http://localhost:8000"
    echo "- Frontend: http://localhost:3000"
    echo "- API Docs: http://localhost:8000/docs"
    echo "- PGAdmin: http://localhost:5050"
    echo "- Redis Commander: http://localhost:8081"
    echo ""
    echo "⚠️  Don't forget to update your .env files with actual API keys!"
}

# Run main function
main