#!/usr/bin/env python3
"""
Test the chat functionality through the backend API
"""
import requests
import json

def test_backend_api():
    """Test the backend chat API endpoint"""
    try:
        base_url = "http://127.0.0.1:8000"
        
        # Test health endpoint first
        health_response = requests.get(f"{base_url}/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ Backend health check passed")
        else:
            print(f"❌ Backend health check failed: {health_response.status_code}")
            return False
        
        # Test chat endpoint with authentication
        chat_data = {
            "text": "Hello, can you help me test OpenRouter?",
            "document_id": "test"
        }
        
        # Add authentication header (dev token)
        headers = {
            "Authorization": "Bearer dev-token",
            "Content-Type": "application/json"
        }
        
        chat_response = requests.post(
            f"{base_url}/api/chat/query",
            json=chat_data,
            headers=headers,
            timeout=30
        )
        
        if chat_response.status_code == 200:
            result = chat_response.json()
            print("✅ Chat API working!")
            print(f"Response: {result}")
            return True
        else:
            print(f"❌ Chat API failed: {chat_response.status_code}")
            print(f"Response: {chat_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Backend API test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Backend Chat API\n")
    test_backend_api()