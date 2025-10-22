"""
Configuration settings for PDFPixie
Render + Supabase + AWS S3 Deployment
"""

import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Get environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"
IS_DEVELOPMENT = not IS_PRODUCTION

# ===== AI CONFIGURATION =====
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ===== DATABASE CONFIGURATION (Supabase PostgreSQL) =====
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Supabase/PostgreSQL
    # Replace postgres:// with postgresql:// for SQLAlchemy compatibility
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    logger.info("✅ Using PostgreSQL database (Supabase)")
else:
    # SQLite for development
    DATABASE_URL = f"sqlite:///./data/database/chat_history.db"
    logger.info("✅ Using SQLite database (development)")

# ===== AWS S3 CONFIGURATION =====
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_ENABLED = bool(AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and S3_BUCKET_NAME)

if S3_ENABLED:
    logger.info(f"✅ S3 storage enabled: {S3_BUCKET_NAME}")
else:
    logger.warning("⚠️  S3 storage disabled - using local ephemeral storage")

# ===== FILE STORAGE PATHS =====
if IS_PRODUCTION:
    # Render free tier uses ephemeral storage at /tmp
    # Files are lost on service restart
    DATA_DIR = Path("/tmp/pdfpixie_data")
    logger.warning("⚠️  Using ephemeral storage - files will be lost on restart")
    if not S3_ENABLED:
        logger.warning("💡 Configure AWS S3 for persistent file storage")
else:
    # Development paths
    DATA_DIR = Path("./data")

UPLOADS_DIR = DATA_DIR / "uploads"
CHROMADB_DIR = DATA_DIR / "chromadb"
DATABASE_DIR = DATA_DIR / "database"

# Ensure directories exist
for directory in [DATA_DIR, UPLOADS_DIR, CHROMADB_DIR, DATABASE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ===== CORS CONFIGURATION =====
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

if IS_PRODUCTION:
    ALLOWED_ORIGINS = [
        FRONTEND_URL,  # Vercel frontend
        "https://*.vercel.app",  # All Vercel preview deployments
        "http://localhost:3000",  # Local testing
        "http://localhost:5173",  # Vite dev server
    ]
else:
    ALLOWED_ORIGINS = ["*"]

# ===== FILE UPLOAD LIMITS =====
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".pdf"}

# ===== LOGGING CONFIGURATION =====
LOG_LEVEL = "INFO" if IS_PRODUCTION else "DEBUG"

# Log startup configuration
if IS_DEVELOPMENT:
    logger.info("=" * 60)
    logger.info("PDFPixie Configuration")
    logger.info("=" * 60)
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Database: {'PostgreSQL' if 'postgresql' in DATABASE_URL else 'SQLite'}")
    logger.info(f"S3 Storage: {'Enabled' if S3_ENABLED else 'Disabled'}")
    logger.info(f"Data Directory: {DATA_DIR}")
    logger.info(f"Frontend URL: {FRONTEND_URL}")
    logger.info("=" * 60)
