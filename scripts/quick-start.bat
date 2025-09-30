@echo off
REM Quick development start script using UV (Windows)
REM This script starts the development environment quickly

echo 🚀 Quick start with UV - Starting Newchat development...

REM Check if UV is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 📦 UV not found. Installing UV...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
    echo ✅ UV installed successfully!
)

REM Backend setup
echo 🐍 Setting up backend with UV...
cd backend

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment with UV...
    uv venv
)

REM Install dependencies
echo Installing dependencies with UV (this will be fast!)...
call .venv\Scripts\activate.bat
uv pip install -r requirements.txt

REM Copy environment file if needed
if not exist ".env" (
    copy .env.example .env
    echo ⚠️  Created .env file - please update with your API keys!
)

cd ..

REM Start services in background
echo 🐳 Starting development services...
docker-compose -f docker-compose.dev.yml up -d

echo ⏳ Waiting for services to be ready...
timeout /t 5

echo.
echo 🎉 Quick start complete!
echo.
echo Next steps:
echo 1. Backend: cd backend ^&^& .venv\Scripts\activate.bat ^&^& uvicorn main:socket_app --reload
echo 2. Frontend: cd frontend ^&^& npm install ^&^& npm start
echo.
echo Services:
echo - Backend API: http://localhost:8000
echo - Frontend: http://localhost:3000
echo - API Docs: http://localhost:8000/docs
echo.
echo ⚡ UV made dependency installation 10-100x faster!

pause