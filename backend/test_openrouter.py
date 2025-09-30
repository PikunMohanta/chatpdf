#!/usr/bin/env python3
"""
Simple test script to verify OpenRouter API integration
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openrouter_connection():
    """Test OpenRouter API connection"""
    try:
        from langchain_openai import ChatOpenAI
        
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_api_key or openrouter_api_key == "your-openrouter-api-key":
            print("❌ OpenRouter API key not set!")
            print("Please set OPENROUTER_API_KEY in your .env file")
            return False
        
        print("🔑 OpenRouter API key found")
        print(f"Key preview: {openrouter_api_key[:8]}...")
        
        # Initialize OpenRouter client
        llm = ChatOpenAI(
            openai_api_key=openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.7,
            max_tokens=100,
            model="meta-llama/llama-3.1-8b-instruct"
        )
        
        print("🤖 Testing OpenRouter connection...")
        
        # Test a simple chat completion
        response = llm.invoke("Hello! Please respond with 'OpenRouter is working correctly!'")
        
        print("✅ OpenRouter connection successful!")
        print(f"Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenRouter connection failed: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure your OpenRouter API key is valid")
        print("2. Check that you have credits in your OpenRouter account")
        print("3. Ensure the model 'anthropic/claude-3-haiku' is available")
        return False

def test_embeddings():
    """Test OpenRouter embeddings"""
    try:
        from langchain_openai import OpenAIEmbeddings
        
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_api_key or openrouter_api_key == "your-openrouter-api-key":
            print("⚠️ Skipping embeddings test - no API key")
            return True
        
        print("🔗 Testing OpenRouter embeddings...")
        
        embeddings = OpenAIEmbeddings(
            api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            model="text-embedding-ada-002"
        )
        
        # Test embedding a simple text
        result = embeddings.embed_query("This is a test document")
        
        print(f"✅ Embeddings working! Vector length: {len(result)}")
        return True
        
    except Exception as e:
        print(f"⚠️ Embeddings test failed: {str(e)}")
        print("This might be normal if OpenRouter doesn't support embeddings")
        print("The app will fall back to mock embeddings for local development")
        return True

if __name__ == "__main__":
    print("🚀 Testing OpenRouter API Integration\n")
    
    chat_success = test_openrouter_connection()
    print()
    
    embedding_success = test_embeddings()
    print()
    
    if chat_success:
        print("🎉 OpenRouter is ready to use!")
        print("\nNext steps:")
        print("1. Make sure to set your actual OpenRouter API key in .env")
        print("2. Start the backend server: uvicorn main:app --reload")
        print("3. Test the chat functionality in the frontend")
    else:
        print("❌ OpenRouter setup needs attention")
        sys.exit(1)