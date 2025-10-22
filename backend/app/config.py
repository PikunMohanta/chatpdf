"""
Configuration settings for PDFPixie
Environment-specific configurations for development and production
"""

import os
from pathlib import Path

# Get environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"
IS_DEVELOPMENT = not IS_PRODUCTION

# API Keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Database configuration
# Railway provides DATABASE_URL automatically for PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # PostgreSQL on Railway
    # Railway provides postgres:// but SQLAlchemy needs postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print(f"✅ Using PostgreSQL database")
else:
    # SQLite for development
    DATABASE_URL = f"sqlite:///./data/database/chat_history.db"
    print(f"✅ Using SQLite database (development)")

# Paths configuration
if IS_PRODUCTION:
    # Production paths - Fly.io/Railway provides persistent volumes
    # Check if volume is mounted (both Fly.io and Railway use /data)
    if os.path.exists("/data"):
        DATA_DIR = Path("/data")
        print("✅ Using persistent volume at /data (Fly.io/Railway)")
    else:
        # Fallback to /tmp but warn about data loss
        DATA_DIR = Path("/tmp/pdfpixie")
        print("⚠️  WARNING: Using ephemeral storage - data will be lost on restart!")
    
    UPLOADS_DIR = DATA_DIR / "uploads"
    CHROMADB_DIR = DATA_DIR / "chromadb"
else:
    # Development paths
    DATA_DIR = Path("./data")
    UPLOADS_DIR = DATA_DIR / "uploads"
    CHROMADB_DIR = DATA_DIR / "chromadb"

# Ensure directories exist
for directory in [DATA_DIR, UPLOADS_DIR, CHROMADB_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# CORS configuration
if IS_PRODUCTION:
    ALLOWED_ORIGINS = [
        "https://pdfpixie-frontend.onrender.com",
        "https://pdfpixie.onrender.com",
        "http://localhost:3000",  # For local testing
        "http://localhost:5173",  # Vite dev server
    ]
else:
    ALLOWED_ORIGINS = ["*"]

# Logging configuration
LOG_LEVEL = "INFO" if IS_PRODUCTION else "DEBUG"

# File upload limits
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".pdf"}

print(f"🔧 Configuration loaded for {ENVIRONMENT} environment")
print(f"📁 Data directory: {DATA_DIR}")
print(f"📤 Uploads directory: {UPLOADS_DIR}")
print(f"💾 Database directory: {DATABASE_DIR}")