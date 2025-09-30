#!/usr/bin/env python3

# Direct test of the chat functionality without server
import sys
import os
sys.path.append('./backend')

from backend.app.chat import generate_ai_response
import asyncio

async def test_chat():
    print("Testing chat functionality directly...")
    
    # Test with a real document ID
    document_id = 'eab39c08-0c87-461e-a232-b5975c91efbf'
    question = 'What is this document about? Can you summarize the main topic?'
    
    print(f"Document ID: {document_id}")
    print(f"Question: {question}")
    
    try:
        response, sources = await generate_ai_response(question, document_id)
        print(f"\nAI Response:")
        print(response)
        
        if sources:
            print(f"\nSources ({len(sources)}):")
            for i, source in enumerate(sources):
                print(f"{i+1}. {source}")
        else:
            print("\nNo sources found")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat())