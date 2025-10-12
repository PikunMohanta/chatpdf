# PDFPixie Startup Script
# Run this to start both backend and frontend servers

Write-Host "🚀 Starting PDFPixie Servers..." -ForegroundColor Cyan
Write-Host ""

# Check if already running
$backendRunning = Get-Process | Where-Object {$_.CommandLine -like "*uvicorn*main:socket_app*"} -ErrorAction SilentlyContinue
$frontendRunning = Get-Process | Where-Object {$_.CommandLine -like "*vite*"} -ErrorAction SilentlyContinue

if ($backendRunning) {
    Write-Host "⚠️  Backend already running (PID: $($backendRunning.Id))" -ForegroundColor Yellow
} else {
    Write-Host "📡 Starting Backend Server (Socket.IO)..." -ForegroundColor Green
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd E:\Project\New\chatpdf\backend; python -m uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000"
    Start-Sleep -Seconds 3
}

if ($frontendRunning) {
    Write-Host "⚠️  Frontend already running (PID: $($frontendRunning.Id))" -ForegroundColor Yellow
} else {
    Write-Host "🎨 Starting Frontend Server (React)..." -ForegroundColor Green
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd E:\Project\New\chatpdf\frontend; npm run dev"
    Start-Sleep -Seconds 3
}

Write-Host ""
Write-Host "✅ Servers starting..." -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Access Points:" -ForegroundColor Cyan
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   Frontend: http://localhost:3001" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "⌨️  Press Ctrl+C in each terminal window to stop servers" -ForegroundColor Yellow
Write-Host ""

# Wait a bit then test
Start-Sleep -Seconds 5

Write-Host "🧪 Testing connections..." -ForegroundColor Cyan

try {
    $healthCheck = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5
    if ($healthCheck.StatusCode -eq 200) {
        Write-Host "✅ Backend is healthy" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Backend not responding yet (it may still be starting)" -ForegroundColor Red
}

try {
    $frontendCheck = Invoke-WebRequest -Uri "http://localhost:3001" -Method GET -TimeoutSec 5
    if ($frontendCheck.StatusCode -eq 200) {
        Write-Host "✅ Frontend is accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Frontend not responding yet (it may still be starting)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Setup complete! Open http://localhost:3001 in your browser" -ForegroundColor Cyan
Write-Host ""
