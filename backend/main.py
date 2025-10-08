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

# Get configuration from environment
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

# In production, don't allow all origins
if DEBUG:
    ALLOWED_ORIGINS.append("*")

# Configure CORS BEFORE Socket.IO initialization
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Socket.IO with environment-based configuration
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*' if DEBUG else ALLOWED_ORIGINS,
    logger=DEBUG,
    engineio_logger=DEBUG,
    always_connect=True  # Accept all connections (authentication can be added later)
)

# Combine FastAPI and Socket.IO
socket_app = socketio.ASGIApp(sio, app)

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
app.include_router(pdf_router, prefix="/api", tags=["pdf"])
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
    """
    Handle new Socket.IO connections
    For development, we accept all connections without authentication
    """
    logger.info(f"✅ Client {sid} connected from {environ.get('REMOTE_ADDR', 'unknown')}")
    try:
        await sio.emit('connected', {
            'message': 'Connected to Newchat',
            'sid': sid,
            'status': 'success'
        }, room=sid)
    except Exception as e:
        logger.error(f"Error sending connected event: {e}")
    return True  # Accept the connection

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

@sio.event
async def query(sid, data):
    """
    Handle chat query from client via Socket.IO
    """
    try:
        document_id = data.get('document_id')
        query_text = data.get('query')
        
        logger.info(f"📥 Received query from {sid}: {query_text[:50] if query_text else 'None'}... for document {document_id}")
        
        if not query_text or not document_id:
            logger.warning(f"Missing data - query: {bool(query_text)}, document_id: {bool(document_id)}")
            await sio.emit('error', {'message': 'Missing query or document_id'}, room=sid)
            return
        
        # Import the AI response generator
        from app.chat import generate_ai_response
        
        # Send typing indicator
        await sio.emit('typing', {'status': 'ai_typing'}, room=sid)
        
        # Generate AI response
        logger.info(f"🤖 Generating AI response for document {document_id}...")
        response_text, sources = await generate_ai_response(query_text, document_id)
        
        logger.info(f"✅ Generated response for {sid}: {response_text[:100] if response_text else 'Empty'}...")
        
        # Send response back to client
        await sio.emit('response', {
            'response': response_text,
            'document_id': document_id,
            'sources': sources
        }, room=sid)
        
    except Exception as e:
        logger.error(f"❌ Error processing query from {sid}: {e}", exc_info=True)
        await sio.emit('error', {'message': f'Error processing query: {str(e)}'}, room=sid)

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
    # Get host and port from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        "main:socket_app",  # CRITICAL: Must be socket_app for Socket.IO to work!
        host=host,
        port=port,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info"
    )