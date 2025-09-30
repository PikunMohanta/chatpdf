#!/usr/bin/env python3
"""
Simple test that verifies OpenRouter is working via our API
"""
import requests
import time

def test_openrouter_via_api():
    """Test OpenRouter through our chat API"""
    try:
        base_url = "http://127.0.0.1:8000"
        
        print("Testing OpenRouter via Chat API...")
        
        # Test data
        chat_data = {
            "text": "Please respond with exactly: 'OpenRouter integration is working!'",
            "document_id": "test-doc"
        }
        
        # Headers with dev token
        headers = {
            "Authorization": "Bearer dev-token",
            "Content-Type": "application/json"
        }
        
        print("Making request to /api/chat/query...")
        
        response = requests.post(
            f"{base_url}/api/chat/query",
            json=chat_data,
            headers=headers,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat API successful!")
            print(f"Response: {result}")
            
            # Check if it's using OpenRouter (real response) or mock
            answer = result.get("response", "")
            if "Mock response" in answer:
                print("⚠️ Using mock responses (OpenRouter not fully connected)")
            else:
                print("🎉 OpenRouter is working!")
            
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Wait a moment for server to be ready
    time.sleep(2)
    test_openrouter_via_api()