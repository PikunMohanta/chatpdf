@echo off
echo Starting Newchat Backend Server...
cd /d "e:\Project\Newchat\backend"

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Start the server
echo Starting FastAPI server on http://127.0.0.1:8000
python -c "import uvicorn; uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)"

pause