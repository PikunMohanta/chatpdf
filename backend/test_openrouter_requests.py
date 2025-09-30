#!/usr/bin/env python3
"""
Test OpenRouter using direct HTTP requests
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_openrouter_requests():
    """Test OpenRouter using requests library"""
    try:
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_api_key or openrouter_api_key == "your-openrouter-api-key":
            print("❌ OpenRouter API key not set!")
            return False
        
        print("🔑 OpenRouter API key found")
        print(f"Key preview: {openrouter_api_key[:12]}...")
        
        print("🤖 Testing OpenRouter connection with requests...")
        
        # Test API connection with direct HTTP request
        headers = {
            "Authorization": f"Bearer {openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Newchat PDF Assistant"
        }
        
        data = {
            "model": "meta-llama/llama-3.1-8b-instruct",
            "messages": [
                {"role": "user", "content": "Hello! Please respond with 'OpenRouter is working correctly!'"}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result["choices"][0]["message"]["content"]
            print("✅ OpenRouter connection successful!")
            print(f"Response: {message}")
            return True
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ OpenRouter connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing OpenRouter with HTTP Requests\n")
    success = test_openrouter_requests()
    
    if success:
        print("\n🎉 OpenRouter is working correctly!")
        print("The issue is with the OpenAI client library, not OpenRouter itself.")
    else:
        print("\n❌ OpenRouter test failed")