"""
Test Chat API - Socket.IO Connection Test
"""
import socketio
import asyncio
import time

# Create Socket.IO client
sio = socketio.AsyncClient(logger=True, engineio_logger=True)

@sio.event
async def connect():
    print("✅ Connected to server!")
    print("=" * 50)

@sio.event
async def disconnect():
    print("❌ Disconnected from server")

@sio.event
async def connected(data):
    print(f"📨 Server says: {data}")

@sio.event
async def response(data):
    print(f"\n🤖 AI Response:")
    print(f"   Message: {data.get('message', 'No message')[:200]}")
    if data.get('sources'):
        print(f"   Sources: {len(data.get('sources'))} chunks")
    print("=" * 50)

@sio.event
async def error(data):
    print(f"❌ Error: {data}")

async def test_chat():
    """Test chat functionality"""
    try:
        # Connect to server
        print("🔌 Connecting to http://localhost:8000...")
        await sio.connect('http://localhost:8000', transports=['websocket'])
        
        # Wait for connection
        await asyncio.sleep(1)
        
        # Test with a sample document ID (you can change this)
        document_id = "test-doc-123"
        
        print(f"\n📤 Sending query for document: {document_id}")
        print(f"   Question: 'What is this document about?'")
        print("-" * 50)
        
        # Send query
        await sio.emit('query', {
            'document_id': document_id,
            'query': 'What is this document about?'
        })
        
        # Wait for response
        await asyncio.sleep(5)
        
        # Send another query
        print(f"\n📤 Sending second query...")
        print(f"   Question: 'Can you summarize the key points?'")
        print("-" * 50)
        
        await sio.emit('query', {
            'document_id': document_id,
            'query': 'Can you summarize the key points?'
        })
        
        # Wait for response
        await asyncio.sleep(5)
        
        # Disconnect
        await sio.disconnect()
        
        print("\n✅ Test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 50)
    print("    Socket.IO Chat API Test")
    print("=" * 50)
    asyncio.run(test_chat())
