#!/usr/bin/env python3
"""
Quick test to verify the backend chat API is working
Run this while the backend server is running
"""

import requests
import json
import sys

def test_chat_api():
    print("Testing Newchat Backend API...")
    
    # Test health endpoint first
    try:
        health_response = requests.get('http://127.0.0.1:8000/health', timeout=5)
        print(f"Health check: {health_response.status_code} - {health_response.json()}")
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return False
    
    # Test chat endpoint
    headers = {
        'Authorization': 'Bearer dev-token',
        'Content-Type': 'application/json'
    }
    
    data = {
        'text': 'Hello, can you help me with this document?',
        'document_id': 'test-doc-123'
    }
    
    try:
        print(f"\nSending chat request...")
        print(f"URL: http://127.0.0.1:8000/api/chat/query")
        print(f"Headers: {headers}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(
            'http://127.0.0.1:8000/api/chat/query',
            json=data,
            headers=headers,
            timeout=30
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"\n✅ Success! Response:")
            print(json.dumps(response_data, indent=2))
            
            if 'response' in response_data and response_data['response']:
                print(f"\n🤖 AI Response: {response_data['response']}")
                return True
            else:
                print(f"\n❌ No 'response' field in response data")
                return False
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_chat_api()
    sys.exit(0 if success else 1)