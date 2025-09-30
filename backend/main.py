from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
import socketio
import uvicorn
import os
from dotenv import load_dotenv
import logging
from typing import List, Optional
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Newchat API",
    description="AI-powered PDF ingestion, parsing, and interactive chat application",
    version="1.0.0"
)

# Initialize Socket.IO
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*"
)

# Combine FastAPI and Socket.IO
socket_app = socketio.ASGIApp(sio, app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import route modules
from app.auth import router as auth_router
from app.pdf_processing import router as pdf_router
from app.chat import router as chat_router

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(pdf_router, prefix="/api/pdf", tags=["pdf"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "newchat-api"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Newchat API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    logger.info(f"Client {sid} connected")
    await sio.emit('connected', {'message': 'Connected to Newchat'}, room=sid)

@sio.event
async def disconnect(sid):
    logger.info(f"Client {sid} disconnected")

@sio.event
async def join_room(sid, data):
    room = data.get('room')
    if room:
        await sio.enter_room(sid, room)
        await sio.emit('joined_room', {'room': room}, room=sid)

@sio.event
async def leave_room(sid, data):
    room = data.get('room')
    if room:
        await sio.leave_room(sid, room)

# WebSocket endpoint for real-time chat
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process message here (integrate with AI service)
            response = f"Echo: {message.get('text', 'No message')}"
            
            await websocket.send_text(json.dumps({
                "type": "response",
                "text": response,
                "timestamp": datetime.utcnow().isoformat()
            }))
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected from WebSocket")

if __name__ == "__main__":
    uvicorn.run(
        "main:socket_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )