#!/usr/bin/env python3

import sys
sys.path.append('./backend')

def test_chromadb_availability():
    print("Testing ChromaDB availability...")
    
    try:
        import chromadb
        from chromadb.config import Settings
        CHROMADB_AVAILABLE = True
        print("ChromaDB is available (imported successfully)")
    except ImportError as e:
        CHROMADB_AVAILABLE = False
        print(f"ChromaDB not available: {e}")
    
    print(f"CHROMADB_AVAILABLE: {CHROMADB_AVAILABLE}")
    
    # Check what the chat module sees
    try:
        from backend.app.chat import CHROMADB_ENABLED
        print(f"chat.py CHROMADB_ENABLED: {CHROMADB_ENABLED}")
    except Exception as e:
        print(f"Error getting CHROMADB_ENABLED from chat.py: {e}")

if __name__ == "__main__":
    test_chromadb_availability()