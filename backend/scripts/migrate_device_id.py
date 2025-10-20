"""
Database Migration Script for Device ID Support

This script helps migrate existing chat sessions to support device-specific isolation.
Run this after updating the code to add device_id support.

Options:
1. Fresh start: Delete existing database (recommended for development)
2. Migrate: Assign device IDs to existing sessions (for production)
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import Base, engine, get_db_session, ChatSessionDB
from sqlalchemy import inspect
import uuid


def check_device_id_column_exists():
    """Check if device_id column already exists in the database"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('chat_sessions')]
    return 'device_id' in columns


def migrate_existing_sessions():
    """Assign unique device IDs to existing sessions without device_id"""
    print("🔄 Starting migration of existing sessions...")
    
    db = get_db_session()
    try:
        # Find all sessions without device_id
        sessions = db.query(ChatSessionDB).filter(
            ChatSessionDB.device_id.is_(None)
        ).all()
        
        if not sessions:
            print("✅ No sessions need migration (all have device_id)")
            return
        
        print(f"📊 Found {len(sessions)} sessions without device_id")
        
        # Group by user_id to assign same device_id to same user's sessions
        user_device_map = {}
        
        for session in sessions:
            user_id = session.user_id
            
            # Create or reuse device_id for this user
            if user_id not in user_device_map:
                # Generate legacy device_id
                user_device_map[user_id] = f"legacy_device_{uuid.uuid4().hex[:12]}"
            
            session.device_id = user_device_map[user_id]
            print(f"  ✓ Session {session.session_id[:8]}... → {session.device_id}")
        
        db.commit()
        print(f"\n✅ Successfully migrated {len(sessions)} sessions")
        print(f"📋 Created {len(user_device_map)} legacy device IDs")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        db.close()


def fresh_start():
    """Delete existing database and start fresh"""
    db_path = Path(backend_dir) / "data" / "database" / "chat_history.db"
    
    if db_path.exists():
        print(f"🗑️  Deleting existing database: {db_path}")
        db_path.unlink()
        print("✅ Database deleted")
    else:
        print("ℹ️  No existing database found")
    
    print("\n🔨 Creating new database with device_id support...")
    Base.metadata.create_all(bind=engine)
    print("✅ New database created successfully")


def show_status():
    """Show current database status"""
    print("\n" + "="*50)
    print("DATABASE STATUS")
    print("="*50)
    
    # Check if device_id column exists
    has_device_id = check_device_id_column_exists()
    print(f"device_id column exists: {'✅ Yes' if has_device_id else '❌ No'}")
    
    if not has_device_id:
        print("\n⚠️  WARNING: device_id column not found!")
        print("   The database schema needs to be updated.")
        print("   Run option 1 (Fresh Start) to recreate the database.")
        return
    
    # Count sessions
    db = get_db_session()
    try:
        total_sessions = db.query(ChatSessionDB).count()
        sessions_with_device_id = db.query(ChatSessionDB).filter(
            ChatSessionDB.device_id.isnot(None)
        ).count()
        sessions_without_device_id = total_sessions - sessions_with_device_id
        
        print(f"\nTotal sessions: {total_sessions}")
        print(f"  With device_id: {sessions_with_device_id}")
        print(f"  Without device_id: {sessions_without_device_id}")
        
        if sessions_without_device_id > 0:
            print(f"\n⚠️  {sessions_without_device_id} sessions need migration")
            print("   Run option 2 (Migrate) to assign device IDs")
        else:
            print("\n✅ All sessions have device_id")
            
    except Exception as e:
        print(f"\n❌ Error checking status: {e}")
    finally:
        db.close()


def main():
    """Main menu"""
    print("\n" + "="*60)
    print("🔧 CHAT HISTORY DATABASE MIGRATION")
    print("="*60)
    print("\nThis script helps add device_id support to your database.")
    print("\nOptions:")
    print("  1. Fresh Start - Delete database and start clean (RECOMMENDED for dev)")
    print("  2. Migrate - Add device_id to existing sessions (for production)")
    print("  3. Show Status - Check current database state")
    print("  4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            confirm = input("\n⚠️  This will DELETE all existing chat history. Continue? (yes/no): ")
            if confirm.lower() == 'yes':
                fresh_start()
                show_status()
            else:
                print("❌ Cancelled")
                
        elif choice == '2':
            print("\nℹ️  This will assign device IDs to existing sessions.")
            print("   Sessions from the same user will get the same device_id.")
            confirm = input("Continue? (yes/no): ")
            if confirm.lower() == 'yes':
                migrate_existing_sessions()
                show_status()
            else:
                print("❌ Cancelled")
                
        elif choice == '3':
            show_status()
            
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
