@echo off
REM Setup script for Newchat develoREM Install UV if not present
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing UV...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%USERPROFILE%\\.cargo\\bin;%PATH%"
)

REM Check Python version
for /f %%i in ('python --version') do set PYTHON_VERSION=%%i
echo 🐍 Detected Python version: %PYTHON_VERSION%

REM Create virtual environment with UV
echo Creating virtual environment with UV...
uv venv --python python

REM Activate virtual environment and install dependencies
echo Installing Python dependencies with UV (faster)...
echo Note: Using ChromaDB instead of FAISS for Python 3.13 compatibility
call .venv\\Scripts\\activate.bat
uv pip install -r requirements.txtt (Windows)
REM This script sets up the local development environment

echo 🚀 Setting up Newchat development environment...

REM Check if required tools are installed
echo 📋 Checking requirements...

where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    exit /b 1
)

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python is not installed. Please install Python 3.10+ first.
    exit /b 1
)

where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    exit /b 1
)

where docker-compose >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

echo ✅ All requirements are met!

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "backend\data\indexes" mkdir "backend\data\indexes"
if not exist "backend\logs" mkdir "backend\logs"
if not exist "logs" mkdir "logs"
echo ✅ Directories created!

REM Setup backend
echo 🐍 Setting up backend...
cd backend

REM Install UV if not present
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing UV...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
)

REM Create virtual environment with UV
echo Creating virtual environment with UV...
uv venv

REM Activate virtual environment and install dependencies
echo Installing Python dependencies with UV (faster)...
call .venv\Scripts\activate.bat
uv pip install -r requirements.txt

REM Copy environment file
if not exist ".env" (
    echo Creating backend .env file...
    copy .env.example .env
    echo ⚠️  Please update the .env file with your actual API keys and configuration!
)

cd ..
echo ✅ Backend setup complete!

REM Setup frontend
echo ⚛️ Setting up frontend...
cd frontend

REM Install dependencies
echo Installing Node.js dependencies...
npm install

REM Create environment file
if not exist ".env" (
    echo Creating frontend .env file...
    echo REACT_APP_API_URL=http://localhost:8000 > .env
    echo REACT_APP_SOCKET_URL=http://localhost:8000 >> .env
)

cd ..
echo ✅ Frontend setup complete!

REM Setup database and services
echo 🐳 Setting up development services...
echo Starting PostgreSQL and Redis...
docker-compose -f docker-compose.dev.yml up -d

echo Waiting for services to be ready...
timeout /t 10

echo ✅ Development services are running!
echo 📊 PGAdmin: http://localhost:5050 (admin@newchat.dev / admin)
echo 🔧 Redis Commander: http://localhost:8081

echo.
echo 🎉 Setup complete!
echo.
echo To start development:
echo 1. Backend: cd backend ^&^& env\Scripts\activate.bat ^&^& uvicorn main:socket_app --reload
echo 2. Frontend: cd frontend ^&^& npm start
echo.
echo Services running:
echo - Backend API: http://localhost:8000
echo - Frontend: http://localhost:3000
echo - API Docs: http://localhost:8000/docs
echo - PGAdmin: http://localhost:5050
echo - Redis Commander: http://localhost:8081
echo.
echo ⚠️  Don't forget to update your .env files with actual API keys!

pause