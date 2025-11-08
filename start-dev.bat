@echo off
REM PDFPixie Development Startup Script for Windows

echo Starting PDFPixie Development Environment...

REM Check if backend is already running
netstat -ano | findstr ":8000" >nul 2>&1
if %errorlevel% == 0 (
    echo Port 8000 is already in use! Please close the existing backend server.
    exit /b 1
)

REM Check if frontend is already running
netstat -ano | findstr ":5173" >nul 2>&1
if %errorlevel% == 0 (
    echo Port 5173 is already in use! Please close the existing frontend server.
    exit /b 1
)

REM Start Backend
echo.
echo [Backend] Starting FastAPI server...
cd backend

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment and start server
start "PDFPixie Backend" cmd /k "call .venv\Scripts\activate && pip install -r requirements.txt >nul 2>&1 && echo Backend ready on http://localhost:8000 && uvicorn main:socket_app --host 0.0.0.0 --port 8000 --reload"

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Start Frontend
cd ..\frontend
echo.
echo [Frontend] Starting Vite dev server...

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

REM Start frontend
start "PDFPixie Frontend" cmd /k "npm run dev"

REM Wait for frontend to start
timeout /t 3 /nobreak >nul

echo.
echo ================================================
echo   PDFPixie is running!
echo ================================================
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo ================================================
echo.
echo Press any key to open the application in your browser...
pause >nul

start http://localhost:5173

echo.
echo Close the Backend and Frontend windows to stop the servers.
