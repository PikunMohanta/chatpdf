"""
Quick test to verify chat functionality with existing documents
"""
import socketio
import asyncio
import sys

# Use an existing document ID from the uploads
DOCUMENT_ID = "00557f6e-dec2-4f7d-a412-f410926d658f"
TEST_QUERY = "What is this document about?"

async def test_chat():
    print("🧪 Testing Chat Functionality")
    print("=" * 50)
    print(f"Document ID: {DOCUMENT_ID}")
    print(f"Query: {TEST_QUERY}")
    print("=" * 50)
    
    # Create Socket.IO client
    sio = socketio.AsyncClient()
    
    response_received = False
    
    @sio.event
    async def connect():
        print("✅ Connected to server!")
        print(f"📤 Sending query...")
        await sio.emit('query', {
            'document_id': DOCUMENT_ID,
            'query': TEST_QUERY
        })
    
    @sio.event
    async def connected(data):
        print(f"📥 Server greeting: {data}")
    
    @sio.event
    async def response(data):
        nonlocal response_received
        response_received = True
        print("\n" + "=" * 50)
        print("✅ RESPONSE RECEIVED!")
        print("=" * 50)
        print(f"Message: {data['message']}")
        print(f"Sources: {len(data.get('sources', []))} chunks")
        print("=" * 50)
        await sio.disconnect()
    
    @sio.event
    async def error(data):
        print(f"❌ Error: {data}")
        await sio.disconnect()
    
    @sio.event
    async def disconnect():
        print("👋 Disconnected")
    
    try:
        # Connect to server
        print("🔌 Connecting to http://localhost:8000...")
        await sio.connect('http://localhost:8000')
        
        # Wait for response (max 30 seconds)
        for i in range(30):
            await asyncio.sleep(1)
            if response_received or not sio.connected:
                break
            if i % 5 == 0:
                print(f"⏳ Waiting... ({i}s)")
        
        if not response_received:
            print("⚠️  No response received within timeout")
            await sio.disconnect()
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_chat())
    sys.exit(0 if result else 1)
