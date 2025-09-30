#!/usr/bin/env python3
"""
Test OpenRouter with a simple chat without requiring document upload
"""
import requests
import json

def test_simple_chat():
    """Test basic chat functionality"""
    base_url = "http://127.0.0.1:8000"
    
    try:
        # Add authentication header for development
        headers = {
            "Authorization": "Bearer dev-token",
            "Content-Type": "application/json"
        }
        
        # Test with a simple question that doesn't require a specific document
        chat_data = {
            "text": "Hello! Can you tell me what you are and how you can help me?",
            "document_id": "general"  # Use a general document ID
        }
        
        print("🤖 Testing OpenRouter chat functionality...")
        print(f"Question: {chat_data['text']}")
        
        response = requests.post(
            f"{base_url}/api/chat/query",
            json=chat_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat response received!")
            print(f"Response: {result.get('response', 'No response field')}")
            
            # Check if it's a real OpenRouter response (not a mock)
            response_text = result.get('response', '')
            if 'mock' in response_text.lower() or 'development mode' in response_text.lower():
                print("⚠️ Received mock response - OpenRouter might not be configured properly")
                return False
            else:
                print("🎉 Real OpenRouter response received!")
                return True
        else:
            print(f"❌ Chat request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_with_context():
    """Test chat with some context"""
    base_url = "http://127.0.0.1:8000"
    
    try:
        headers = {
            "Authorization": "Bearer dev-token",
            "Content-Type": "application/json"
        }
        
        chat_data = {
            "text": "What is artificial intelligence and how does it work?",
            "document_id": "ai_context"
        }
        
        print("\n🧠 Testing OpenRouter with AI question...")
        print(f"Question: {chat_data['text']}")
        
        response = requests.post(
            f"{base_url}/api/chat/query",
            json=chat_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI question response received!")
            print(f"Response: {result.get('response', 'No response field')}")
            return True
        else:
            print(f"❌ AI question failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ AI question test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing OpenRouter Chat Functionality\n")
    
    # Test basic chat
    basic_success = test_simple_chat()
    
    # Test with AI question
    ai_success = test_with_context()
    
    print(f"\n📊 Test Results:")
    print(f"Basic Chat: {'✅ PASS' if basic_success else '❌ FAIL'}")
    print(f"AI Question: {'✅ PASS' if ai_success else '❌ FAIL'}")
    
    if basic_success and ai_success:
        print("\n🎉 OpenRouter is working correctly!")
    else:
        print("\n⚠️ OpenRouter needs troubleshooting")