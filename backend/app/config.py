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

# Paths configuration
if IS_PRODUCTION:
    # Production paths - use /tmp for writable storage on Render
    DATA_DIR = Path("/tmp/pdfpixie")
    UPLOADS_DIR = DATA_DIR / "uploads"
    DATABASE_DIR = DATA_DIR / "database"
    CHROMADB_DIR = DATA_DIR / "chromadb"
else:
    # Development paths
    DATA_DIR = Path("./data")
    UPLOADS_DIR = DATA_DIR / "uploads"
    DATABASE_DIR = DATA_DIR / "database"
    CHROMADB_DIR = DATA_DIR / "chromadb"

# Ensure directories exist
for directory in [DATA_DIR, UPLOADS_DIR, DATABASE_DIR, CHROMADB_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Database configuration
DATABASE_URL = f"sqlite:///{DATABASE_DIR}/chat_history.db"

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