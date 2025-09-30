#!/usr/bin/env python3

import os
import sys
sys.path.append('./backend')

from dotenv import load_dotenv
load_dotenv('./backend/.env')

from backend.app.openrouter_client import get_openrouter_client, is_openrouter_enabled, generate_response

def test_openrouter():
    print("Testing OpenRouter connectivity...")
    
    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    print(f"API Key found: {'Yes' if api_key else 'No'}")
    if api_key:
        print(f"API Key starts with: {api_key[:20]}...")
    
    # Test client initialization
    client = get_openrouter_client()
    print(f"Client initialized: {'Yes' if client else 'No'}")
    
    # Test availability
    if client:
        is_available = client.is_available()
        print(f"OpenRouter available: {is_available}")
        
        if is_available:
            # Test a simple completion
            messages = [
                {"role": "user", "content": "Say hello in a friendly way"}
            ]
            
            print("\nTesting chat completion...")
            response = generate_response(messages)
            print(f"Response: {response}")
        else:
            print("OpenRouter is not available - check connection or API key")
    
    print(f"\nis_openrouter_enabled(): {is_openrouter_enabled()}")

if __name__ == "__main__":
    test_openrouter()