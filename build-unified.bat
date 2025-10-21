@echo off
REM Unified Build Script for PDFPixie (Windows)
REM This script builds both frontend and backend for single-service deployment

echo 🚀 Starting unified build process...

REM Navigate to project root
cd /d "%~dp0"

REM Install backend dependencies
echo 📦 Installing Python dependencies...
cd backend
pip install -r requirements.txt
cd ..

REM Build frontend
echo 🎨 Building frontend...
cd frontend
call npm install
call npm run build

REM Copy built frontend to backend static directory
echo 📁 Copying frontend build to backend...
if exist "..\backend\static" rmdir /s /q "..\backend\static"
xcopy /e /i "dist" "..\backend\static"

REM Verify the build
if exist "..\backend\static\index.html" (
    echo ✅ Unified build completed successfully!
    echo 📂 Frontend files copied to backend/static/
    echo 🚀 Ready for deployment!
) else (
    echo ❌ Build failed - index.html not found in backend/static
    exit /b 1
)

cd ..
echo 🎉 Unified build process complete!