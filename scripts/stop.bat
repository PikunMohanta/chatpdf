@echo off
REM ===================================================================
REM PDF Pal - Stop Servers Script for Windows
REM ===================================================================

echo Stopping PDF Pal servers...

REM Kill processes on port 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill processes on port 3000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo All servers stopped.
