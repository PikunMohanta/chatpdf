"""
Database configuration and models for chat history
Uses SQLite with SQLAlchemy ORM
"""
from sqlalchemy import create_engine, Column, String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from .config import DATABASE_URL, IS_PRODUCTION

# Create engine with appropriate connect_args based on database type
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}  # Needed for SQLite
# PostgreSQL doesn't need check_same_thread parameter

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Database Models
class ChatSessionDB(Base):
    """Chat session database model"""
    __tablename__ = "chat_sessions"
    
    session_id = Column(String(36), primary_key=True, index=True)
    document_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to messages
    messages = relationship("ChatMessageDB", back_populates="session", cascade="all, delete-orphan")

class ChatMessageDB(Base):
    """Chat message database model"""
    __tablename__ = "chat_messages"
    
    message_id = Column(String(36), primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.session_id"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    sender = Column(String(10), nullable=False)  # 'user' or 'ai'
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    sources = Column(Text, nullable=True)  # JSON string of sources
    
    # Relationship to session
    session = relationship("ChatSessionDB", back_populates="messages")

def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session (dependency injection for FastAPI)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """Get database session (for direct use)"""
    return SessionLocal()
