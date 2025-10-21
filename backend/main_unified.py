"""
Alternative main.py for unified deployment (backend + frontend in one service)
This version serves the React frontend alongside the API
"""

import os
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import socketio
from pathlib import Path
import uvicorn

# Import your existing modules
from app.pdf_processing import PDFProcessor
from app.chat_history_db import ChatHistoryDB
from app.openrouter_client import OpenRouterClient
from app.config import *

# Create FastAPI app
app = FastAPI(
    title="PDFPixie API",
    description="AI-powered PDF analysis and chat application",
    version="1.0.0"
)

# Create socket.io server
sio = socketio.AsyncServer(
    cors_allowed_origins=ALLOWED_ORIGINS,
    logger=True,
    engineio_logger=True
)

# Initialize components
pdf_processor = PDFProcessor()
chat_db = ChatHistoryDB()
openrouter_client = OpenRouterClient()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": ENVIRONMENT}

# Your existing API endpoints here...
# (Copy all the existing endpoints from your current main.py)

# Serve static files (React app)
# Check if static directory exists (for unified deployment)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    print(f"📁 Serving static files from: {static_dir}")
    
    # Serve static assets
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")
    
    # Handle SPA routing - serve index.html for non-API routes
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Don't intercept API routes
        if full_path.startswith(("api/", "socket.io/", "health", "docs", "redoc")):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Serve index.html for all other routes (SPA routing)
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        else:
            raise HTTPException(status_code=404, detail="Frontend not built")
else:
    print("⚠️  Static directory not found - running API only")

# Attach socket.io to FastAPI
socket_app = socketio.ASGIApp(sio, app)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:socket_app",
        host="0.0.0.0",
        port=port,
        reload=not IS_PRODUCTION
    )