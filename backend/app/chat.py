from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import json
import logging
from datetime import datetime
import asyncio
import os

# Optional imports for production use
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("chromadb not available - using mock storage for local development")

try:
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    from langchain.chains import RetrievalQA
    from langchain.prompts import PromptTemplate
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("langchain not available - using mock responses for local development")

from .auth import verify_token, UserInfo
from .chat_history import chat_history_manager, ChatMessage as HistoryChatMessage, ChatSession as HistoryChatSession

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic models
class ChatMessage(BaseModel):
    message_id: str
    text: str
    sender: str  # "user" or "ai"
    timestamp: datetime
    document_id: Optional[str] = None

class ChatSession(BaseModel):
    session_id: str
    document_id: str
    created_at: datetime
    messages: List[ChatMessage] = []

class ChatRequest(BaseModel):
    text: str
    document_id: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_id: str
    sources: List[str] = []

class ChatHistoryResponse(BaseModel):
    session_id: str
    document_id: str
    created_at: str
    updated_at: str
    messages: List[Dict[str, Any]]
    
class SessionListResponse(BaseModel):
    sessions: List[Dict[str, Any]]

from .openrouter_client import get_openrouter_client, is_openrouter_enabled, generate_response

# Initialize LLM using custom OpenRouter client
try:
    # Check if OpenRouter is available
    if is_openrouter_enabled():
        LLM_ENABLED = True
        logger.info("OpenRouter client initialized successfully")
    else:
        LLM_ENABLED = False
        logger.warning("OpenRouter not available - using mock responses for development")
except Exception as e:
    LLM_ENABLED = False
    logger.warning(f"OpenRouter client initialization failed - using mock responses: {e}")

# Initialize ChromaDB client only if available AND embeddings are enabled
if CHROMADB_AVAILABLE:
    try:
        from dotenv import load_dotenv
        load_dotenv()  # Ensure environment variables are loaded
        
        chroma_client = chromadb.PersistentClient(path="./data/chromadb")
        # Check if we can actually create embeddings (need OpenAI/OpenRouter for embeddings)
        EMBEDDINGS_AVAILABLE = False
        try:
            from langchain_openai import OpenAIEmbeddings
            import os
            openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
            openai_api_key = os.getenv("OPENAI_API_KEY")
            logger.info(f"Checking embeddings availability: OpenRouter key = {'Yes' if openrouter_api_key else 'No'}, OpenAI key = {'Yes' if openai_api_key else 'No'}")
            if openrouter_api_key and openrouter_api_key != "your-openrouter-api-key":
                EMBEDDINGS_AVAILABLE = True
            elif openai_api_key and openai_api_key != "your-openai-api-key":
                EMBEDDINGS_AVAILABLE = True
        except Exception as e:
            logger.warning(f"Error checking embeddings availability: {e}")
        
        CHROMADB_ENABLED = EMBEDDINGS_AVAILABLE
        if not EMBEDDINGS_AVAILABLE:
            logger.info("ChromaDB available but embeddings not configured - using mock embeddings")
    except Exception as e:
        chroma_client = None
        CHROMADB_ENABLED = False
        logger.warning(f"ChromaDB initialization failed: {e}")
else:
    chroma_client = None
    CHROMADB_ENABLED = False
    EMBEDDINGS_AVAILABLE = False
    logger.warning("ChromaDB not available - using mock storage for development")

# Custom prompt template for PDF Q&A
PROMPT_TEMPLATE = """
Use the following pieces of context from the PDF document to answer the question. 
If you don't know the answer based on the context, just say that you don't know, 
don't try to make up an answer.

Context:
{context}

Question: {question}

Answer: """

PROMPT = PromptTemplate(
    template=PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)

# In-memory storage for active chat sessions (replace with Redis in production)
active_sessions: Dict[str, ChatSession] = {}

def load_document_collection(document_id: str):
    """
    Load ChromaDB collection for a specific document
    """
    try:
        collection_name = f"doc_{document_id}"
        collection = chroma_client.get_collection(name=collection_name)
        return collection
    except Exception as e:
        logger.error(f"Error loading collection for document {document_id}: {e}")
        raise HTTPException(status_code=404, detail="Document embeddings not found")

def create_qa_chain_with_chromadb(collection):
    """
    Create a custom QA chain using ChromaDB collection
    """
    try:
        # This is a simplified QA implementation
        # In a production environment, you'd want more sophisticated retrieval
        return collection
    except Exception as e:
        logger.error(f"Error creating QA chain: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize chat system")

async def query_collection(collection, question: str, k: int = 3) -> tuple[str, List[str]]:
    """
    Query ChromaDB collection and generate response
    """
    try:
        # Query the collection for relevant documents
        results = collection.query(
            query_texts=[question],
            n_results=k
        )
        
        if not results['documents'] or not results['documents'][0]:
            return "I couldn't find relevant information in the document to answer your question.", []
        
        # Get the most relevant documents
        relevant_docs = results['documents'][0]
        
        # Create context from retrieved documents
        context = "\n\n".join(relevant_docs)
        
        # Create prompt for the LLM
        prompt = f"""Based on the following context from the document, answer the question.
        If the answer is not in the context, say so.

Context:
{context}

Question: {question}

Answer:"""

        # Get response from LLM using OpenRouter
        if LLM_ENABLED:
            messages = [
                {"role": "system", "content": "You are a helpful assistant that answers questions based on document context."},
                {"role": "user", "content": prompt}
            ]
            answer = generate_response(messages)
        else:
            answer = f"Mock response: Based on the document context, here's what I found about '{question}'. (This is a development response since OpenRouter is not configured.)"
        
        # Return answer and sources
        sources = [doc[:100] + "..." for doc in relevant_docs]
        return answer, sources
        
    except Exception as e:
        logger.error(f"Error querying collection: {e}")
        return "I'm sorry, I encountered an error while processing your question.", []

async def generate_ai_response(question: str, document_id: str) -> tuple[str, List[str]]:
    """
    Generate AI response for a question about a specific document
    Uses OpenRouter when available, falls back to mock responses only when needed
    """
    try:
        # If we have OpenRouter available, use it even with mock embeddings
        if LLM_ENABLED:
            logger.info(f"Generating OpenRouter response for document {document_id}, question: {question[:50]}...")
            
            # Try to get document context (from mock or real embeddings)
            context = ""
            sources = []
            
            try:
                # Always try mock embeddings first when real embeddings aren't available
                use_mock_embeddings = True
                
                # Check if we have real embeddings configured
                try:
                    from dotenv import load_dotenv
                    load_dotenv()
                    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
                    openai_api_key = os.getenv("OPENAI_API_KEY")
                    
                    # Only use ChromaDB if we have a valid embedding API key AND the collection exists
                    if (openrouter_api_key and openrouter_api_key != "your-openrouter-api-key") or \
                       (openai_api_key and openai_api_key != "your-openai-api-key"):
                        try:
                            if CHROMADB_ENABLED and chroma_client:
                                collection = chroma_client.get_collection(name=f"doc_{document_id}")
                                results = collection.query(query_texts=[question], n_results=3)
                                if results['documents'] and results['documents'][0]:
                                    context = "\n\n".join(results['documents'][0])
                                    sources = [doc[:100] + "..." for doc in results['documents'][0]]
                                    logger.info(f"Found {len(results['documents'][0])} relevant chunks from ChromaDB")
                                    use_mock_embeddings = False
                        except Exception as chroma_e:
                            logger.info(f"ChromaDB collection not found or error: {chroma_e} - using mock embeddings")
                except Exception as env_e:
                    logger.info(f"Environment check failed: {env_e} - using mock embeddings")
                
                # Use mock embeddings if ChromaDB didn't work
                if use_mock_embeddings:
                    logger.info("Using mock embeddings for document context")
                    import json
                    import os
                    
                    # Get the absolute path to the mock embeddings file
                    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    mock_file = os.path.join(current_dir, "data", "mock_embeddings", f"doc_{document_id}.json")
                    logger.info(f"Looking for mock embeddings file: {mock_file}")
                    
                    if os.path.exists(mock_file):
                        logger.info(f"Found mock embeddings file for document {document_id}")
                        with open(mock_file, 'r', encoding='utf-8') as f:
                            mock_data = json.load(f)
                        
                        total_chunks = len(mock_data.get('chunks', []))
                        logger.info(f"Loaded {total_chunks} chunks from mock embeddings")
                        
                        # Simple keyword matching for mock retrieval
                        relevant_chunks = []
                        question_words = question.lower().split()
                        logger.info(f"Question keywords: {question_words}")
                        
                        for i, chunk in enumerate(mock_data.get('chunks', [])):
                            chunk_words = chunk.lower().split()
                            matches = sum(1 for word in question_words if word in chunk_words)
                            if matches > 0:
                                relevant_chunks.append((chunk, matches))
                                logger.info(f"Chunk {i} has {matches} matches")
                        
                        # Sort by relevance and take top 3
                        relevant_chunks.sort(key=lambda x: x[1], reverse=True)
                        top_chunks = [chunk[0] for chunk in relevant_chunks[:3]]
                        
                        if top_chunks:
                            context = "\n\n".join(top_chunks)
                            sources = [f"Chunk {i+1}: {chunk[:100]}..." for i, chunk in enumerate(top_chunks)]
                            logger.info(f"Using {len(top_chunks)} relevant chunks for context")
                        else:
                            logger.warning(f"No relevant chunks found for question: {question}")
                            # Fallback: use first few chunks if no keyword matches
                            fallback_chunks = mock_data.get('chunks', [])[:2]
                            if fallback_chunks:
                                context = "\n\n".join(fallback_chunks)
                                sources = [f"Document excerpt {i+1}: {chunk[:100]}..." for i, chunk in enumerate(fallback_chunks)]
                                logger.info(f"Using fallback chunks from document")
                    else:
                        logger.error(f"Mock embeddings file not found: {mock_file}")
                        # List available files for debugging
                        mock_dir = os.path.join(current_dir, "data", "mock_embeddings")
                        if os.path.exists(mock_dir):
                            available_files = os.listdir(mock_dir)
                            logger.info(f"Available mock embedding files: {available_files}")
                        else:
                            logger.error(f"Mock embeddings directory not found: {mock_dir}")
                            logger.info(f"Current working directory: {os.getcwd()}")
                            logger.info(f"Script directory: {current_dir}")
                
            except Exception as context_e:
                logger.warning(f"Error loading document context: {context_e}")
                context = "No specific document context available."
            
            # Generate response using OpenRouter
            try:
                if context and context.strip():
                    # We have document context - create a context-aware prompt
                    messages = [
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on document content. Always base your answer on the provided context. If the context doesn't contain enough information to answer the question, say so clearly."},
                        {"role": "user", "content": f"Based on the following document content, please answer the question.\n\nDocument content:\n{context}\n\nQuestion: {question}\n\nPlease provide a detailed answer based on the document content above:"}
                    ]
                    logger.info(f"Sending context-aware prompt to OpenRouter (context length: {len(context)} chars)")
                else:
                    # No document context available - general response
                    messages = [
                        {"role": "system", "content": "You are a helpful assistant. The user is asking about a document, but no document context is available."},
                        {"role": "user", "content": f"I'd like to ask about a document, but it seems the document content isn't available right now. My question is: {question}\n\nCan you provide a general helpful response and suggest how I might get a better answer?"}
                    ]
                    logger.info(f"Sending general prompt to OpenRouter (no document context)")
                
                response = generate_response(messages)
                
                if response:
                    logger.info(f"OpenRouter response generated successfully (length: {len(response)} chars)")
                    return response, sources
                else:
                    logger.error("OpenRouter returned empty response")
                    return "I apologize, but I couldn't generate a response at the moment. Please try again.", sources
                    
            except Exception as openrouter_e:
                logger.error(f"OpenRouter error: {openrouter_e}")
                return f"I encountered an error while generating a response: {str(openrouter_e)}", sources
        
        # Fallback to mock response only if OpenRouter is not available
        logger.info(f"Using mock response for question: {question[:50]}...")
        return f"Mock response: I would analyze the document to answer '{question}' but OpenRouter is not configured. This is a development response.", ["Mock source: Please configure OpenRouter API key for AI responses"]
        
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        return f"I encountered an error: {str(e)}", []
        return "I'm sorry, I encountered an error while processing your question.", []

@router.post("/query", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    current_user: UserInfo = Depends(verify_token)
):
    """
    Process a chat query and return AI response
    """
    try:
        # Generate AI response
        ai_response, sources = await generate_ai_response(request.text, request.document_id)
        
        # Generate unique IDs
        import uuid
        message_id = str(uuid.uuid4())
        
        # Get or create chat session
        session = None
        if hasattr(request, 'session_id') and request.session_id:
            session = chat_history_manager.get_session(request.session_id)
        
        if not session:
            # Create new session for this document and user
            session = chat_history_manager.create_session(request.document_id, current_user.user_id)
        
        # Save user message
        user_message = HistoryChatMessage(
            message_id=str(uuid.uuid4()),
            text=request.text,
            sender='user',
            timestamp=datetime.now()
        )
        chat_history_manager.add_message_to_session(session.session_id, user_message)
        
        # Save AI response
        ai_message = HistoryChatMessage(
            message_id=message_id,
            text=ai_response,
            sender='ai',
            timestamp=datetime.now(),
            sources=sources
        )
        chat_history_manager.add_message_to_session(session.session_id, ai_message)
        
        logger.info(f"Chat query processed for user {current_user.user_id}, document {request.document_id}, session {session.session_id}")
        
        return ChatResponse(
            response=ai_response,
            session_id=session.session_id,
            message_id=message_id,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Error processing chat query: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat query")

@router.get("/sessions/all", response_model=SessionListResponse)
async def get_all_user_sessions(current_user: UserInfo = Depends(verify_token)):
    """
    Get all chat sessions for the current user across all documents
    """
    try:
        sessions_data = chat_history_manager.get_all_user_sessions(current_user.user_id)
        return SessionListResponse(sessions=sessions_data)
    except Exception as e:
        logger.error(f"Error retrieving all user sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat sessions")

@router.get("/sessions/{document_id}", response_model=SessionListResponse)
async def get_document_chat_sessions(
    document_id: str,
    current_user: UserInfo = Depends(verify_token)
):
    """
    Get all chat sessions for a specific document
    """
    try:
        sessions_data = chat_history_manager.get_document_sessions(document_id, current_user.user_id)
        return SessionListResponse(sessions=sessions_data)
    except Exception as e:
        logger.error(f"Error retrieving document sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat sessions")

@router.get("/sessions/{document_id}/latest", response_model=ChatHistoryResponse)
async def get_latest_chat_session(
    document_id: str,
    current_user: UserInfo = Depends(verify_token)
):
    """
    Get the latest chat session for a document with message history
    """
    try:
        session = chat_history_manager.get_latest_session_for_document(document_id, current_user.user_id)
        
        if not session:
            # Create a new session if none exists
            session = chat_history_manager.create_session(document_id, current_user.user_id)
        
        return ChatHistoryResponse(
            session_id=session.session_id,
            document_id=session.document_id,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat(),
            messages=[msg.to_dict() for msg in session.messages]
        )
    except Exception as e:
        logger.error(f"Error retrieving latest session: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat session")

@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    current_user: UserInfo = Depends(verify_token)
):
    """
    Get a specific chat session with full message history
    """
    try:
        session = chat_history_manager.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Verify user has access to this session
        if session.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Access denied to this chat session")
        
        return ChatHistoryResponse(
            session_id=session.session_id,
            document_id=session.document_id,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat(),
            messages=[msg.to_dict() for msg in session.messages]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: UserInfo = Depends(verify_token)
):
    """
    Delete a chat session and its message history
    """
    try:
        session = chat_history_manager.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Verify user has access to this session
        if session.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Access denied to this chat session")
        
        success = chat_history_manager.delete_session(session_id)
        
        if success:
            return {"message": "Chat session deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete chat session")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete chat session")

@router.post("/sessions/{session_id}/export")
async def export_chat_session(
    session_id: str,
    current_user: UserInfo = Depends(verify_token)
):
    """
    Export chat session as markdown
    """
    try:
        # TODO: Implement session export
        # 1. Get session messages from database
        # 2. Format as markdown
        # 3. Return as downloadable file
        
        markdown_content = f"""# Chat Session Export
        
Session ID: {session_id}
User: {current_user.email}
Export Date: {datetime.now().isoformat()}

## Conversation

*This is a placeholder. Implement actual message export.*
"""
        
        return {
            "content": markdown_content,
            "filename": f"chat_session_{session_id}.md"
        }
        
    except Exception as e:
        logger.error(f"Error exporting chat session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to export chat session")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections.remove(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.user_connections:
            await self.user_connections[user_id].send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/{document_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    document_id: str,
    user_id: str = "anonymous"  # TODO: Get from token validation
):
    """
    WebSocket endpoint for real-time chat
    """
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Extract question
            question = message_data.get("text", "")
            
            if question:
                # Send typing indicator
                await websocket.send_text(json.dumps({
                    "type": "typing",
                    "status": "ai_typing"
                }))
                
                # Generate AI response
                ai_response, sources = await generate_ai_response(question, document_id)
                
                # Send response
                response_data = {
                    "type": "message",
                    "text": ai_response,
                    "sender": "ai",
                    "timestamp": datetime.now().isoformat(),
                    "sources": sources
                }
                
                await websocket.send_text(json.dumps(response_data))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"User {user_id} disconnected from chat")