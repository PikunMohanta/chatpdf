#!/usr/bin/env python3
"""
Quick test script that checks if OpenRouter is working
without disrupting the server
"""
import os
from dotenv import load_dotenv

load_dotenv()

def check_openrouter_config():
    """Check OpenRouter configuration"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key or api_key == "your-openrouter-api-key":
        print("❌ OpenRouter API key not configured")
        return False
    
    print("✅ OpenRouter API key is configured")
    print(f"Key preview: {api_key[:12]}...")
    
    # Import our custom client
    try:
        from app.openrouter_client import get_openrouter_client, is_openrouter_enabled
        
        if is_openrouter_enabled():
            print("✅ OpenRouter client is working")
            
            # Test a simple chat completion
            client = get_openrouter_client()
            messages = [{"role": "user", "content": "Say 'OpenRouter test successful!'"}]
            response = client.chat_completion(messages)
            
            if response:
                print(f"✅ OpenRouter response: {response}")
                return True
            else:
                print("❌ OpenRouter response failed")
                return False
        else:
            print("❌ OpenRouter client not available")
            return False
            
    except Exception as e:
        print(f"❌ Error testing OpenRouter: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Quick OpenRouter Configuration Check\n")
    
    success = check_openrouter_config()
    
    if success:
        print("\n🎉 OpenRouter is configured and working!")
        print("Your Newchat app can now use OpenRouter for AI responses.")
    else:
        print("\n❌ OpenRouter needs attention")
        print("Check your API key and network connection.")