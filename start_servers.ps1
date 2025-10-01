# Newchat - Complete Startup Script
# This script starts both backend (with Socket.IO) and frontend servers

Write-Host "🚀 Starting Newchat Application..." -ForegroundColor Cyan
Write-Host ""

# Check if UV is installed
if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "❌ UV is not installed. Please install it first:" -ForegroundColor Red
    Write-Host "   powershell -c 'irm https://astral.sh/uv/install.ps1 | iex'" -ForegroundColor Yellow
    exit 1
}

# Start Backend with Socket.IO
Write-Host "📦 Starting Backend Server (with Socket.IO)..." -ForegroundColor Green
$backendPath = Join-Path $PSScriptRoot "backend"
$env:PYTHONPATH = $backendPath

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; Write-Host '🔧 Backend Server' -ForegroundColor Cyan; uv run uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal

Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start Frontend
Write-Host "🎨 Starting Frontend Server..." -ForegroundColor Green
$frontendPath = Join-Path $PSScriptRoot "frontend"
$npmPath = "C:\Program Files\nodejs\node.exe"
$npmCliPath = "C:\Program Files\nodejs\node_modules\npm\bin\npm-cli.js"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; Write-Host '🎨 Frontend Server' -ForegroundColor Cyan; & '$npmPath' '$npmCliPath' run dev" -WindowStyle Normal

Write-Host ""
Write-Host "✅ Servers Starting!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 URLs:" -ForegroundColor Cyan
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   Frontend: http://localhost:3001" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Test Chat: Open test_chat_live.html in your browser" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  IMPORTANT: Backend must use 'main:socket_app' not 'main:app'" -ForegroundColor Magenta
Write-Host "    This enables Socket.IO for real-time chat!" -ForegroundColor Magenta
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
