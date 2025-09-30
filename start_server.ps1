Write-Host "Starting Newchat Backend Server..." -ForegroundColor Green
Set-Location "e:\Project\Newchat\backend"

# Activate virtual environment
& ".\.venv\Scripts\Activate.ps1"

# Start the server
Write-Host "Starting FastAPI server on http://127.0.0.1:8000" -ForegroundColor Yellow
python -c "import uvicorn; uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)"

Read-Host "Press Enter to exit..."