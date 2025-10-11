"""
Database viewer script - View chat history database contents
Run this to inspect the SQLite database without needing sqlite3 command-line tool
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import get_db_session, ChatSessionDB, ChatMessageDB, init_db
from datetime import datetime

# Initialize database (create tables if they don't exist)
init_db()

def view_database():
    """View all sessions and messages in the database"""
    db = get_db_session()
    
    try:
        # Get all sessions
        sessions = db.query(ChatSessionDB).order_by(ChatSessionDB.created_at.desc()).all()
        
        print("=" * 80)
        print("CHAT HISTORY DATABASE CONTENTS")
        print("=" * 80)
        print(f"\nTotal Sessions: {len(sessions)}")
        print(f"Database Location: backend/data/database/chat_history.db\n")
        
        if not sessions:
            print("⚠️  No sessions found in database yet.")
            print("   Send some messages to create chat history!\n")
            return
        
        for i, session in enumerate(sessions, 1):
            print(f"\n{'─' * 80}")
            print(f"SESSION {i}")
            print(f"{'─' * 80}")
            print(f"Session ID:    {session.session_id}")
            print(f"Document ID:   {session.document_id}")
            print(f"User ID:       {session.user_id}")
            print(f"Created:       {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Last Updated:  {session.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Message Count: {len(session.messages)}")
            
            if session.messages:
                print(f"\nMessages:")
                print(f"{'─' * 80}")
                
                for j, message in enumerate(session.messages, 1):
                    sender_icon = "👤" if message.sender == "user" else "🤖"
                    print(f"\n{j}. {sender_icon} {message.sender.upper()} [{message.timestamp.strftime('%H:%M:%S')}]")
                    
                    # Truncate long messages
                    text = message.text
                    if len(text) > 200:
                        text = text[:200] + "..."
                    
                    print(f"   {text}")
                    
                    if message.sources:
                        import json
                        sources = json.loads(message.sources)
                        if sources:
                            print(f"   📚 Sources: {len(sources)} references")
        
        print(f"\n{'=' * 80}\n")
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def count_records():
    """Quick count of records"""
    db = get_db_session()
    
    try:
        session_count = db.query(ChatSessionDB).count()
        message_count = db.query(ChatMessageDB).count()
        
        print("\n" + "=" * 80)
        print("DATABASE STATISTICS")
        print("=" * 80)
        print(f"Total Sessions: {session_count}")
        print(f"Total Messages: {message_count}")
        
        if session_count > 0:
            avg_messages = message_count / session_count
            print(f"Avg Messages per Session: {avg_messages:.1f}")
            
            # Most recent session
            latest = db.query(ChatSessionDB).order_by(ChatSessionDB.updated_at.desc()).first()
            if latest:
                print(f"\nMost Recent Session:")
                print(f"  Session ID: {latest.session_id}")
                print(f"  Updated: {latest.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Messages: {len(latest.messages)}")
        
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="View chat history database")
    parser.add_argument("--stats", action="store_true", help="Show statistics only")
    parser.add_argument("--full", action="store_true", help="Show full content (default)")
    
    args = parser.parse_args()
    
    if args.stats:
        count_records()
    else:
        view_database()
