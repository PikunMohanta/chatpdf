#!/usr/bin/env python3
"""
Check what user IDs are in the database and what the current session isolation is producing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import get_db_session, ChatSessionDB
from app.auth import generate_user_id_from_request
import hashlib
from datetime import datetime

def check_database_users():
    """Check what user IDs exist in the database"""
    print("🔍 Checking user IDs in database...")
    
    db = get_db_session()
    try:
        sessions = db.query(ChatSessionDB).all()
        user_ids = {}
        
        for session in sessions:
            user_id = session.user_id
            if user_id not in user_ids:
                user_ids[user_id] = 0
            user_ids[user_id] += 1
        
        print(f"Found {len(user_ids)} unique user IDs:")
        for user_id, count in user_ids.items():
            print(f"  - {user_id}: {count} sessions")
        
        return user_ids
        
    finally:
        db.close()

def test_user_id_generation():
    """Test what user IDs are being generated"""
    print("\n🔧 Testing user ID generation...")
    
    # Mock request objects
    class MockRequest:
        def __init__(self, ip, user_agent):
            self.client = MockClient(ip)
            self.headers = {"user-agent": user_agent}
    
    class MockClient:
        def __init__(self, host):
            self.host = host
    
    # Test different browser scenarios
    test_cases = [
        ("127.0.0.1", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
        ("127.0.0.1", "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)"),
        ("192.168.1.100", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
    ]
    
    print("Simulated user ID generation:")
    for ip, user_agent in test_cases:
        request = MockRequest(ip, user_agent)
        user_id = generate_user_id_from_request(request)
        print(f"  - IP: {ip}, UA: {user_agent[:50]}... → {user_id}")
    
    return test_cases

def suggest_fix():
    """Suggest how to fix the session visibility issue"""
    print("\n💡 Potential fixes:")
    
    # Check if we have anonymous sessions
    db = get_db_session()
    try:
        anonymous_sessions = db.query(ChatSessionDB).filter(
            ChatSessionDB.user_id == "anonymous"
        ).count()
        
        if anonymous_sessions > 0:
            print(f"Found {anonymous_sessions} sessions with user_id='anonymous'")
            print("These sessions might not be visible with the new session isolation.")
            print("\nOptions to fix:")
            print("1. Keep old 'anonymous' sessions visible to all users (less secure)")
            print("2. Migrate old sessions to a default user ID")
            print("3. Add a legacy mode that shows old 'anonymous' sessions")
            
            return "anonymous_sessions_found"
        else:
            print("No 'anonymous' sessions found. The issue might be elsewhere.")
            return "no_anonymous_sessions"
            
    finally:
        db.close()

if __name__ == "__main__":
    print("🔍 PDFPixie Session Investigation")
    print("=" * 50)
    
    user_ids = check_database_users()
    test_user_id_generation()
    issue_type = suggest_fix()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print(f"- Total user IDs in database: {len(user_ids)}")
    print(f"- Session isolation is generating unique user IDs")
    
    if "anonymous" in user_ids:
        print(f"- Found {user_ids['anonymous']} sessions with old 'anonymous' user_id")
        print("- These sessions won't be visible with new session isolation")
        print("- Consider implementing a migration strategy")
    else:
        print("- No 'anonymous' sessions found")
        print("- Database and session isolation should be working correctly")