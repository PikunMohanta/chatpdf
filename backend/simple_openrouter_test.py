#!/usr/bin/env python3
"""
Simple direct test of OpenRouter API using the openai client
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_openrouter_direct():
    """Test OpenRouter using direct openai client"""
    try:
        import openai
        
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_api_key or openrouter_api_key == "your-openrouter-api-key":
            print("❌ OpenRouter API key not set!")
            return False
        
        print("🔑 OpenRouter API key found")
        print(f"Key preview: {openrouter_api_key[:12]}...")
        
        # Create OpenAI client configured for OpenRouter
        client = openai.OpenAI(
            api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        print("🤖 Testing OpenRouter connection...")
        
        # Test a simple chat completion
        response = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",
            messages=[
                {"role": "user", "content": "Hello! Please respond with 'OpenRouter is working correctly!'"}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        print("✅ OpenRouter connection successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenRouter connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing OpenRouter Direct API Connection\n")
    success = test_openrouter_direct()
    
    if success:
        print("\n🎉 OpenRouter is working correctly!")
    else:
        print("\n❌ OpenRouter test failed")