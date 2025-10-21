from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import socketio
import uvicorn
from dotenv import load_dotenv
import logging
import uuid
from datetime import datetime
import os
from pathlib import Path

# Load environment variables
load_dotenv()

# Get environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

# Initialize FastAPI app
app = FastAPI(
    title="PDFPixie API",
    description="AI-powered PDF ingestion, parsing, and interactive chat application",
    version="1.0.0"
)

# Configure CORS for production/development
# For unified deployment, we don't need CORS since everything is same origin
if not IS_PRODUCTION:
    # Development CORS - allow all for local development
    allowed_origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Initialize Socket.IO with environment-specific CORS
# For unified deployment, CORS is not needed since everything is same origin
if IS_PRODUCTION:
    cors_origins = True  # Same origin
else:
    cors_origins = "*"  # Allow all for development

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=cors_origins,
    logger=IS_PRODUCTION,  # Reduce logging in production
    engineio_logger=False,  # Disable engine.io logging in production
    always_connect=True
)

# Combine FastAPI and Socket.IO
socket_app = socketio.ASGIApp(sio, app)

# Security
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
from app.database import init_db
init_db()
logger.info("Database initialized successfully")

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
    return {"status": "healthy", "service": "pdfpixie-api"}

# Static file serving for unified deployment
static_dir = Path(__file__).parent / "static"
if static_dir.exists() and IS_PRODUCTION:
    logger.info(f"📁 Serving static files from: {static_dir}")
    
    # Serve static assets (CSS, JS, images)
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")
    
    # Serve any other static files (like pdf.worker.min.js)
    @app.get("/pdf.worker.min.js")
    async def serve_pdf_worker():
        worker_file = static_dir / "pdf.worker.min.js"
        if worker_file.exists():
            return FileResponse(worker_file)
        raise HTTPException(status_code=404, detail="PDF worker not found")
    
    # Serve favicon and other root files
    @app.get("/favicon.ico")
    async def serve_favicon():
        favicon_file = static_dir / "favicon.ico"
        if favicon_file.exists():
            return FileResponse(favicon_file)
        raise HTTPException(status_code=404)
    
    # Handle SPA routing - serve index.html for non-API routes
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Don't intercept API routes, docs, or health check
        if full_path.startswith(("api/", "socket.io/", "health", "docs", "redoc", "openapi.json")):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Serve index.html for all other routes (SPA routing)
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        else:
            raise HTTPException(status_code=404, detail="Frontend not built")
else:
    # Development or API-only mode
    @app.get("/")
    async def root():
        if not IS_PRODUCTION:
            return {
                "message": "Welcome to PDFPixie API (Development Mode)",
                "version": "1.0.0",
                "docs": "/docs",
                "note": "Frontend served separately in development"
            }
        else:
            return {
                "message": "Welcome to PDFPixie API",
                "version": "1.0.0",
                "docs": "/docs",
                "error": "Frontend static files not found"
            }

# Development endpoint for loading chat history without authentication
@app.get("/api/chat/history/{session_id}")
async def get_chat_history_dev(session_id: str):
    """
    Get chat history for development (no auth required)
    """
    try:
        from app.chat_history_db import chat_history_manager
        
        session = chat_history_manager.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        return {
            "session_id": session.session_id,
            "document_id": session.document_id,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "messages": [msg.to_dict() for msg in session.messages]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")

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
            'message': 'Connected to PDFPixie',
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
        session_id = data.get('session_id')
        user_id = data.get('user_id', 'anonymous')  # Get user_id from client
        
        logger.info(f"📥 Received query from {sid}: {query_text[:50] if query_text else 'None'}... for document {document_id}, session {session_id}, user {user_id}")
        
        if not query_text or not document_id:
            logger.warning(f"Missing data - query: {bool(query_text)}, document_id: {bool(document_id)}")
            await sio.emit('error', {'message': 'Missing query or document_id'}, room=sid)
            return
        
        # Check if this is a "new_chat_" temporary document
        if document_id.startswith('new_chat_'):
            logger.warning(f"Attempt to query temporary new_chat document: {document_id}")
            await sio.emit('error', {'message': 'Please upload a PDF document first before starting a chat'}, room=sid)
            return
        
        # Import the AI response generator and chat history (database-backed)
        from app.chat import generate_ai_response
        from app.chat_history_db import chat_history_manager, ChatMessage
        import uuid
        
        # Get or create chat session
        session = None
        if session_id:
            session = chat_history_manager.get_session(session_id)
        
        if not session:
            # Create new session for this document and user
            logger.info(f"Creating new chat session for document {document_id}, user {user_id}")
            session = chat_history_manager.create_session(document_id, user_id)
            session_id = session.session_id
        
        # Save user message to history
        user_message = ChatMessage(
            message_id=str(uuid.uuid4()),
            text=query_text,
            sender='user',
            timestamp=datetime.now()
        )
        chat_history_manager.add_message_to_session(session_id, user_message)
        logger.info(f"💾 Saved user message to session {session_id}")
        
        # Send typing indicator
        await sio.emit('typing', {'status': 'ai_typing'}, room=sid)
        
        # Generate AI response
        logger.info(f"🤖 Generating AI response for document {document_id}...")
        response_text, sources, search_mode = await generate_ai_response(query_text, document_id)
        
        logger.info(f"✅ Generated response for {sid}: {response_text[:100] if response_text else 'Empty'}...")
        
        # Save AI response to history
        ai_message = ChatMessage(
            message_id=str(uuid.uuid4()),
            text=response_text,
            sender='ai',
            timestamp=datetime.now(),
            sources=sources
        )
        chat_history_manager.add_message_to_session(session_id, ai_message)
        logger.info(f"💾 Saved AI response to session {session_id}")
        
        # Send response back to client with session_id and search mode
        await sio.emit('response', {
            'response': response_text,
            'document_id': document_id,
            'session_id': session_id,
            'sources': sources,
            'searchMode': search_mode
        }, room=sid)
        
    except Exception as e:
        logger.error(f"❌ Error processing query from {sid}: {e}", exc_info=True)
        await sio.emit('error', {'message': f'Error processing query: {str(e)}'}, room=sid)

if __name__ == "__main__":
    # Get port from environment variable (for Render deployment)
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:socket_app",
        host="0.0.0.0",
        port=port,
        reload=not IS_PRODUCTION,  # Disable reload in production
        log_level="info" if IS_PRODUCTION else "debug"
    )