#!/usr/bin/env python3
"""
Test script for chat history persistence
"""

import sys
import os
import requests
import json
from pathlib import Path

# Add the app directory to the path
backend_dir = Path(__file__).parent
app_dir = backend_dir / "app"
sys.path.insert(0, str(app_dir))

# Test settings
BASE_URL = "http://localhost:8080"
DEV_TOKEN = "dev-token-123"
HEADERS = {
    "Authorization": f"Bearer {DEV_TOKEN}",
    "Content-Type": "application/json"
}

def test_chat_with_history():
    """Test chat endpoint with history persistence"""
    print("🧪 Testing chat history persistence...")
    
    # Test data
    test_document_id = "test-doc-chat-history"
    test_query = "What is this document about?"
    
    # Step 1: Send a chat message
    print(f"📤 Sending chat message: '{test_query}'")
    chat_payload = {
        "query": test_query,
        "document_id": test_document_id
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/query",
            headers=HEADERS,
            json=chat_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            chat_data = response.json()
            print(f"✅ Chat response received: {chat_data.get('answer', 'No answer')[:100]}...")
            session_id = chat_data.get('session_id')
            print(f"📋 Session ID: {session_id}")
            
            # Step 2: Get latest session for document
            print(f"\n🔍 Getting latest session for document: {test_document_id}")
            latest_response = requests.get(
                f"{BASE_URL}/chat/sessions/{test_document_id}/latest",
                headers=HEADERS,
                timeout=10
            )
            
            if latest_response.status_code == 200:
                session_data = latest_response.json()
                print(f"✅ Retrieved session with {len(session_data.get('messages', []))} messages")
                
                # Display messages
                for i, msg in enumerate(session_data.get('messages', [])):
                    print(f"  Message {i+1}: [{msg['role']}] {msg['content'][:50]}...")
                
                # Step 3: Get chat history by session ID
                if session_id:
                    print(f"\n📜 Getting chat history for session: {session_id}")
                    history_response = requests.get(
                        f"{BASE_URL}/chat/history/{session_id}",
                        headers=HEADERS,
                        timeout=10
                    )
                    
                    if history_response.status_code == 200:
                        history_data = history_response.json()
                        print(f"✅ Retrieved history with {len(history_data.get('messages', []))} messages")
                        return True
                    else:
                        print(f"❌ Failed to get chat history: {history_response.status_code}")
                        print(f"Response: {history_response.text}")
                
            else:
                print(f"❌ Failed to get latest session: {latest_response.status_code}")
                print(f"Response: {latest_response.text}")
                
        else:
            print(f"❌ Chat failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        
    return False

def test_document_sessions():
    """Test getting all sessions for a document"""
    print("\n🗂️ Testing document sessions retrieval...")
    
    test_document_id = "test-doc-chat-history"
    
    try:
        response = requests.get(
            f"{BASE_URL}/chat/sessions/{test_document_id}",
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            sessions_data = response.json()
            sessions = sessions_data.get('sessions', [])
            print(f"✅ Found {len(sessions)} sessions for document")
            
            for i, session in enumerate(sessions):
                print(f"  Session {i+1}: {session['session_id']} - {session['message_count']} messages")
            
            return True
        else:
            print(f"❌ Failed to get document sessions: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        
    return False

def check_server():
    """Check if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        # Try both ports
        try:
            response = requests.get("http://localhost:8080/health", timeout=5)
            if response.status_code == 200:
                global BASE_URL
                BASE_URL = "http://localhost:8080"
                return True
        except:
            pass
        return False

def main():
    print("🧪 Chat History Test Suite")
    print("=" * 50)
    
    # Check if server is running
    if not check_server():
        print("❌ Server is not running at http://localhost:8000")
        print("Please start the server with: uvicorn main:app --reload")
        return
    
    print("✅ Server is running")
    
    # Run tests
    test_results = []
    
    # Test 1: Chat with history
    test_results.append(test_chat_with_history())
    
    # Test 2: Document sessions
    test_results.append(test_document_sessions())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    passed = sum(test_results)
    total = len(test_results)
    print(f"✅ {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Chat history system is working.")
    else:
        print("⚠️ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()