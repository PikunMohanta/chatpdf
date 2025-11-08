#!/bin/bash
# PDFPixie Development Startup Script

echo "🚀 Starting PDFPixie Development Environment..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}Port $1 is already in use!${NC}"
        return 1
    fi
    return 0
}

# Check ports
echo "Checking ports..."
check_port 8000 || exit 1
check_port 5173 || exit 1

# Start Backend
echo -e "\n${BLUE}Starting Backend (FastAPI)...${NC}"
cd backend

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null

# Install dependencies if needed
if [ ! -f ".venv/installed" ]; then
    echo "Installing backend dependencies..."
    pip install -r requirements.txt
    touch .venv/installed
fi

# Start backend in background
echo "Starting FastAPI server on http://localhost:8000..."
uvicorn main:socket_app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running!${NC}"
else
    echo -e "${RED}❌ Backend failed to start. Check backend.log${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start Frontend
cd ../frontend
echo -e "\n${BLUE}Starting Frontend (Vite)...${NC}"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start frontend
echo "Starting Vite dev server on http://localhost:5173..."
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for frontend to start
sleep 3

echo -e "\n${GREEN}✅ PDFPixie is running!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  Frontend: ${GREEN}http://localhost:5173${NC}"
echo -e "  Backend:  ${GREEN}http://localhost:8000${NC}"
echo -e "  API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\nPress Ctrl+C to stop all services..."

# Trap Ctrl+C to cleanup
cleanup() {
    echo -e "\n${RED}Shutting down...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

trap cleanup INT TERM

# Wait for processes
wait
