"""
Chat History Management System
Handles saving and retrieving chat conversations for documents
"""
import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ChatMessage:
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

class ChatSession:
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

class ChatHistoryManager:
    def __init__(self, storage_dir: str = "./data/chat_history"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Chat history manager initialized with storage: {self.storage_dir}")
    
    def _get_session_file_path(self, session_id: str) -> Path:
        return self.storage_dir / f"session_{session_id}.json"
    
    def _get_document_sessions_file_path(self, document_id: str, user_id: str) -> Path:
        return self.storage_dir / f"doc_{document_id}_{user_id}_sessions.json"
    
    def create_session(self, document_id: str, user_id: str) -> ChatSession:
        """Create a new chat session for a document and user"""
        session_id = str(uuid.uuid4())
        session = ChatSession(session_id, document_id, user_id)
        
        # Save the session
        self.save_session(session)
        
        # Update the document sessions index
        self._update_document_sessions_index(session)
        
        logger.info(f"Created new chat session {session_id} for document {document_id}, user {user_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve a specific chat session"""
        session_file = self._get_session_file_path(session_id)
        
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ChatSession.from_dict(data)
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return None
    
    def save_session(self, session: ChatSession):
        """Save a chat session to storage"""
        session_file = self._get_session_file_path(session.session_id)
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
            
            # Update the document sessions index
            self._update_document_sessions_index(session)
            
            logger.info(f"Saved chat session {session.session_id} with {len(session.messages)} messages")
        except Exception as e:
            logger.error(f"Error saving session {session.session_id}: {e}")
            raise
    
    def get_all_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a user across all documents"""
        try:
            user_sessions = self._load_user_sessions()
            sessions_data = []
            
            user_docs = user_sessions.get(user_id, {})
            for document_id, doc_sessions in user_docs.items():
                for session_id in doc_sessions:
                    session = self.get_session(session_id)
                    if session:
                        sessions_data.append({
                            "session_id": session.session_id,
                            "document_id": session.document_id,
                            "document_name": f"Document {session.document_id}",  # You might want to store actual document names
                            "created_at": session.created_at.isoformat(),
                            "updated_at": session.updated_at.isoformat(),
                            "message_count": len(session.messages),
                            "last_message": session.messages[-1].content if session.messages else None
                        })
            
            # Sort by most recently updated
            sessions_data.sort(key=lambda x: x["updated_at"], reverse=True)
            return sessions_data
            
        except Exception as e:
            logger.error(f"Error getting all user sessions: {e}")
            return []

    def get_document_sessions(self, document_id: str, user_id: str) -> List[Dict]:
        """Get all chat sessions for a document and user"""
        sessions_file = self._get_document_sessions_file_path(document_id, user_id)
        
        if not sessions_file.exists():
            return []
        
        try:
            with open(sessions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('sessions', [])
        except Exception as e:
            logger.error(f"Error loading document sessions for {document_id}, {user_id}: {e}")
            return []
    
    def get_latest_session_for_document(self, document_id: str, user_id: str) -> Optional[ChatSession]:
        """Get the most recent chat session for a document and user"""
        sessions = self.get_document_sessions(document_id, user_id)
        
        if not sessions:
            return None
        
        # Sort by updated_at and get the latest
        latest_session_info = sorted(sessions, key=lambda x: x['updated_at'], reverse=True)[0]
        return self.get_session(latest_session_info['session_id'])
    
    def _update_document_sessions_index(self, session: ChatSession):
        """Update the index of sessions for a document"""
        sessions_file = self._get_document_sessions_file_path(session.document_id, session.user_id)
        
        # Load existing sessions
        sessions_data = {'sessions': []}
        if sessions_file.exists():
            try:
                with open(sessions_file, 'r', encoding='utf-8') as f:
                    sessions_data = json.load(f)
            except:
                pass
        
        # Update or add the session info
        session_info = {
            'session_id': session.session_id,
            'created_at': session.created_at.isoformat(),
            'updated_at': session.updated_at.isoformat(),
            'message_count': len(session.messages),
            'last_message_preview': session.messages[-1].text[:100] + "..." if session.messages else ""
        }
        
        # Remove existing entry for this session if it exists
        sessions_data['sessions'] = [s for s in sessions_data['sessions'] if s['session_id'] != session.session_id]
        
        # Add the updated session info
        sessions_data['sessions'].append(session_info)
        
        # Save the updated index
        try:
            with open(sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error updating document sessions index: {e}")
    
    def add_message_to_session(self, session_id: str, message: ChatMessage) -> bool:
        """Add a message to an existing session"""
        session = self.get_session(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return False
        
        session.add_message(message)
        self.save_session(session)
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session"""
        session_file = self._get_session_file_path(session_id)
        
        if not session_file.exists():
            return False
        
        try:
            # Get session info before deleting
            session = self.get_session(session_id)
            
            # Delete the session file
            session_file.unlink()
            
            # Update the document sessions index
            if session:
                sessions_file = self._get_document_sessions_file_path(session.document_id, session.user_id)
                if sessions_file.exists():
                    with open(sessions_file, 'r', encoding='utf-8') as f:
                        sessions_data = json.load(f)
                    
                    # Remove the session from the index
                    sessions_data['sessions'] = [s for s in sessions_data['sessions'] if s['session_id'] != session_id]
                    
                    with open(sessions_file, 'w', encoding='utf-8') as f:
                        json.dump(sessions_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Deleted chat session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False

# Global chat history manager instance
chat_history_manager = ChatHistoryManager()