#!/usr/bin/env python3
"""
Clean up script to remove legacy documents and start fresh
Removes all old data, sessions, uploads, and test files
"""

import os
import shutil
import sqlite3
from pathlib import Path

def remove_directory(path, description):
    """Remove a directory and all its contents"""
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            print(f"✅ Removed {description}: {path}")
            return True
        except Exception as e:
            print(f"❌ Failed to remove {description}: {e}")
            return False
    else:
        print(f"ℹ️  {description} doesn't exist: {path}")
        return True

def remove_file(path, description):
    """Remove a single file"""
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"✅ Removed {description}: {path}")
            return True
        except Exception as e:
            print(f"❌ Failed to remove {description}: {e}")
            return False
    else:
        print(f"ℹ️  {description} doesn't exist: {path}")
        return True

def clear_database():
    """Clear all data from the SQLite database"""
    db_path = "backend/data/database/chat_history.db"
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Delete all messages first (due to foreign key constraints)
            cursor.execute("DELETE FROM chat_messages")
            messages_deleted = cursor.rowcount
            
            # Delete all sessions
            cursor.execute("DELETE FROM chat_sessions")
            sessions_deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            print(f"✅ Cleared database: {sessions_deleted} sessions, {messages_deleted} messages deleted")
            return True
        except Exception as e:
            print(f"❌ Failed to clear database: {e}")
            return False
    else:
        print("ℹ️  Database doesn't exist")
        return True

def main():
    """Main cleanup function"""
    print("🧹 PDFPixie Fresh Start Cleanup")
    print("=" * 50)
    print("This will remove ALL legacy data, sessions, uploads, and test files.")
    print("⚠️  This action cannot be undone!")
    
    response = input("\nDo you want to proceed? (yes/no): ").lower().strip()
    if response not in ['yes', 'y']:
        print("❌ Cleanup cancelled by user")
        return
    
    print("\n🗑️  Starting cleanup...")
    
    # Files and directories to remove
    cleanup_items = [
        # Legacy chat history JSON files
        ("backend/data/chat_history", "Legacy JSON chat history"),
        
        # Mock embeddings
        ("backend/data/mock_embeddings", "Mock embeddings data"),
        
        # Uploaded files
        ("backend/data/uploads", "Uploaded PDF files"),
        
        # ChromaDB data (will be recreated on next run)
        ("backend/data/chromadb", "ChromaDB vector database"),
        ("data/chromadb", "Root ChromaDB data"),
        ("data/database", "Root database data"),
        
        # Test files
        ("test_database.py", "Database test script"),
        ("test_legacy_fix.py", "Legacy fix test script"),
        ("test_session_isolation.py", "Session isolation test script"),
        ("debug_sessions.py", "Session debug script"),
        ("cleanup_fresh_start.py", "This cleanup script"),
        
        # Documentation files (keep essential ones)
        ("COMPLETE_TESTING_GUIDE.md", "Complete testing guide"),
        ("DEVICE_ISOLATION_IMPLEMENTATION.md", "Device isolation implementation guide"),
        ("DEVICE_ISOLATION_QUICKSTART.md", "Device isolation quickstart"),
        ("TESTING_DEVICE_ISOLATION.md", "Testing device isolation guide"),
        ("README_IMPLEMENTATION_COMPLETE.md", "Implementation complete readme"),
        
        # Cache directories
        ("backend/__pycache__", "Backend Python cache"),
        ("backend/app/__pycache__", "Backend app Python cache"),
    ]
    
    success_count = 0
    total_count = len(cleanup_items)
    
    # Remove directories and files
    for path, description in cleanup_items:
        if os.path.isdir(path):
            if remove_directory(path, description):
                success_count += 1
        else:
            if remove_file(path, description):
                success_count += 1
    
    # Clear database
    print("\n💾 Clearing database...")
    if clear_database():
        success_count += 1
    total_count += 1
    
    # Recreate necessary directories
    print("\n📁 Recreating necessary directories...")
    necessary_dirs = [
        "backend/data/uploads",
        "backend/data/database",
    ]
    
    for dir_path in necessary_dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Cleanup Summary: {success_count}/{total_count} items processed successfully")
    
    if success_count == total_count:
        print("🎉 Fresh start complete! All legacy data removed.")
        print("\n📋 What's been cleaned:")
        print("  ✅ All old chat sessions and messages")
        print("  ✅ All uploaded PDF files")
        print("  ✅ All vector embeddings and search indexes")
        print("  ✅ All test and debug files")
        print("  ✅ Legacy JSON files")
        print("  ✅ Cache files")
        
        print("\n🚀 Ready for fresh start:")
        print("  📤 Upload new PDFs")
        print("  💬 Create new chat sessions")
        print("  🔒 All sessions will be properly isolated")
        print("  🗃️  All data will be stored in SQLite database")
        
    else:
        print("⚠️  Some items couldn't be cleaned. Check the errors above.")

if __name__ == "__main__":
    main()
