"""
Database-backed Chat History Management System
Uses SQLite with SQLAlchemy ORM instead of JSON files
"""
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging

from .database import get_db_session, ChatSessionDB, ChatMessageDB

logger = logging.getLogger(__name__)

class ChatMessage:
    """Chat message model (same interface as before for compatibility)"""
    def __init__(self, message_id: str, text: str, sender: str, timestamp: datetime, sources: List[str] = None):
        self.message_id = message_id
        self.text = text
        self.sender = sender  # 'user' or 'ai'
        self.timestamp = timestamp
        self.sources = sources or []
    
    def to_dict(self) -> Dict:
        return {
            'message_id': self.message_id,
            'text': self.text,
            'sender': self.sender,
            'timestamp': self.timestamp.isoformat(),
            'sources': self.sources
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ChatMessage':
        return cls(
            message_id=data['message_id'],
            text=data['text'],
            sender=data['sender'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            sources=data.get('sources', [])
        )
    
    @classmethod
    def from_db(cls, db_message: ChatMessageDB) -> 'ChatMessage':
        """Create ChatMessage from database model"""
        sources = json.loads(db_message.sources) if db_message.sources else []
        return cls(
            message_id=db_message.message_id,
            text=db_message.text,
            sender=db_message.sender,
            timestamp=db_message.timestamp,
            sources=sources
        )

class ChatSession:
    """Chat session model (same interface as before for compatibility)"""
    def __init__(self, session_id: str, document_id: str, user_id: str, created_at: datetime = None):
        self.session_id = session_id
        self.document_id = document_id
        self.user_id = user_id
        self.created_at = created_at or datetime.now()
        self.updated_at = datetime.now()
        self.messages: List[ChatMessage] = []
    
    def add_message(self, message: ChatMessage):
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'session_id': self.session_id,
            'document_id': self.document_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'messages': [msg.to_dict() for msg in self.messages]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ChatSession':
        session = cls(
            session_id=data['session_id'],
            document_id=data['document_id'],
            user_id=data['user_id'],
            created_at=datetime.fromisoformat(data['created_at'])
        )
        session.updated_at = datetime.fromisoformat(data['updated_at'])
        session.messages = [ChatMessage.from_dict(msg) for msg in data.get('messages', [])]
        return session
    
    @classmethod
    def from_db(cls, db_session: ChatSessionDB) -> 'ChatSession':
        """Create ChatSession from database model"""
        session = cls(
            session_id=db_session.session_id,
            document_id=db_session.document_id,
            user_id=db_session.user_id,
            created_at=db_session.created_at
        )
        session.updated_at = db_session.updated_at
        session.messages = [ChatMessage.from_db(msg) for msg in db_session.messages]
        return session

class ChatHistoryManager:
    """
    Database-backed chat history manager
    Maintains same interface as file-based version for compatibility
    """
    def __init__(self):
        logger.info("Chat history manager initialized with SQLite database")
    
    def create_session(self, document_id: str, user_id: str) -> ChatSession:
        """Create a new chat session for a document and user"""
        session_id = str(uuid.uuid4())
        
        db = get_db_session()
        try:
            # Create database session
            db_session = ChatSessionDB(
                session_id=session_id,
                document_id=document_id,
                user_id=user_id,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(db_session)
            db.commit()
            db.refresh(db_session)
            
            logger.info(f"Created new chat session {session_id} for document {document_id}, user {user_id}")
            
            # Return as ChatSession object
            return ChatSession.from_db(db_session)
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating session: {e}")
            raise
        finally:
            db.close()
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve a specific chat session with all messages"""
        db = get_db_session()
        try:
            db_session = db.query(ChatSessionDB).filter(
                ChatSessionDB.session_id == session_id
            ).first()
            
            if not db_session:
                return None
            
            return ChatSession.from_db(db_session)
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return None
        finally:
            db.close()
    
    def save_session(self, session: ChatSession):
        """Save/update a chat session (for compatibility - prefer add_message_to_session)"""
        db = get_db_session()
        try:
            # Update session timestamp
            db_session = db.query(ChatSessionDB).filter(
                ChatSessionDB.session_id == session.session_id
            ).first()
            
            if db_session:
                db_session.updated_at = session.updated_at
                db.commit()
                logger.info(f"Updated session {session.session_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving session {session.session_id}: {e}")
            raise
        finally:
            db.close()
    
    def get_all_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a user across all documents"""
        db = get_db_session()
        try:
            db_sessions = db.query(ChatSessionDB).filter(
                ChatSessionDB.user_id == user_id
            ).order_by(ChatSessionDB.updated_at.desc()).all()
            
            sessions_data = []
            for db_session in db_sessions:
                # Get message count
                message_count = len(db_session.messages)
                last_message = db_session.messages[-1].text[:100] if db_session.messages else None
                
                sessions_data.append({
                    "session_id": db_session.session_id,
                    "document_id": db_session.document_id,
                    "document_name": f"Document {db_session.document_id}",
                    "created_at": db_session.created_at.isoformat(),
                    "updated_at": db_session.updated_at.isoformat(),
                    "message_count": message_count,
                    "last_message": last_message
                })
            
            return sessions_data
        except Exception as e:
            logger.error(f"Error getting all user sessions: {e}")
            return []
        finally:
            db.close()
    
    def get_document_sessions(self, document_id: str, user_id: str) -> List[Dict]:
        """Get all chat sessions for a document and user"""
        db = get_db_session()
        try:
            db_sessions = db.query(ChatSessionDB).filter(
                ChatSessionDB.document_id == document_id,
                ChatSessionDB.user_id == user_id
            ).order_by(ChatSessionDB.updated_at.desc()).all()
            
            sessions = []
            for db_session in db_sessions:
                message_count = len(db_session.messages)
                last_message_preview = db_session.messages[-1].text[:100] + "..." if db_session.messages else ""
                
                sessions.append({
                    'session_id': db_session.session_id,
                    'created_at': db_session.created_at.isoformat(),
                    'updated_at': db_session.updated_at.isoformat(),
                    'message_count': message_count,
                    'last_message_preview': last_message_preview
                })
            
            return sessions
        except Exception as e:
            logger.error(f"Error loading document sessions for {document_id}, {user_id}: {e}")
            return []
        finally:
            db.close()
    
    def get_latest_session_for_document(self, document_id: str, user_id: str) -> Optional[ChatSession]:
        """Get the most recent chat session for a document and user"""
        db = get_db_session()
        try:
            db_session = db.query(ChatSessionDB).filter(
                ChatSessionDB.document_id == document_id,
                ChatSessionDB.user_id == user_id
            ).order_by(ChatSessionDB.updated_at.desc()).first()
            
            if not db_session:
                return None
            
            return ChatSession.from_db(db_session)
        except Exception as e:
            logger.error(f"Error getting latest session: {e}")
            return None
        finally:
            db.close()
    
    def add_message_to_session(self, session_id: str, message: ChatMessage) -> bool:
        """Add a message to an existing session"""
        db = get_db_session()
        try:
            # Check if session exists
            db_session = db.query(ChatSessionDB).filter(
                ChatSessionDB.session_id == session_id
            ).first()
            
            if not db_session:
                logger.error(f"Session {session_id} not found")
                return False
            
            # Create database message
            db_message = ChatMessageDB(
                message_id=message.message_id,
                session_id=session_id,
                text=message.text,
                sender=message.sender,
                timestamp=message.timestamp,
                sources=json.dumps(message.sources) if message.sources else None
            )
            
            db.add(db_message)
            
            # Update session timestamp
            db_session.updated_at = datetime.now()
            
            db.commit()
            logger.info(f"Added message {message.message_id} to session {session_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding message to session {session_id}: {e}")
            return False
        finally:
            db.close()
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session and all its messages"""
        db = get_db_session()
        try:
            db_session = db.query(ChatSessionDB).filter(
                ChatSessionDB.session_id == session_id
            ).first()
            
            if not db_session:
                return False
            
            # Delete session (cascade will delete messages)
            db.delete(db_session)
            db.commit()
            
            logger.info(f"Deleted chat session {session_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting session {session_id}: {e}")
            return False
        finally:
            db.close()

# Global chat history manager instance
chat_history_manager = ChatHistoryManager()
