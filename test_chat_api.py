"""
Simple Chat API REST Endpoint Test
"""
import sys
import os

# Test if required packages are available
try:
    import requests
    print("✅ requests package available")
except ImportError:
    print("❌ requests not available - installing...")
    os.system("pip install requests")
    import requests

def test_health():
    """Test health endpoint"""
    print("\n" + "="*50)
    print("Testing Health Endpoint")
    print("="*50)
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_root():
    """Test root endpoint"""
    print("\n" + "="*50)
    print("Testing Root Endpoint")
    print("="*50)
    try:
        response = requests.get("http://localhost:8000/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_docs():
    """Test API docs endpoint"""
    print("\n" + "="*50)
    print("Testing API Documentation")
    print("="*50)
    try:
        response = requests.get("http://localhost:8000/docs")
        print(f"Status: {response.status_code}")
        print(f"API Docs available at: http://localhost:8000/docs")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_chat_history():
    """Test chat history endpoint (requires auth)"""
    print("\n" + "="*50)
    print("Testing Chat History Endpoint")
    print("="*50)
    try:
        headers = {"Authorization": "Bearer dev-token"}
        response = requests.get(
            "http://localhost:8000/api/chat/history/test-doc",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Session ID: {data.get('session_id', 'N/A')}")
            print(f"Messages: {len(data.get('messages', []))}")
        else:
            print(f"Response: {response.text[:200]}")
        return response.status_code in [200, 404]  # 404 is OK if no history
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "="*70)
    print(" " * 20 + "Chat API Test Suite")
    print("="*70)
    
    # Check if backend is running
    print("\n🔍 Checking if backend is running on http://localhost:8000...")
    
    results = {
        "Health Check": test_health(),
        "Root Endpoint": test_root(),
        "API Documentation": test_docs(),
        "Chat History": test_chat_history(),
    }
    
    # Summary
    print("\n" + "="*70)
    print(" " * 25 + "Test Summary")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Chat API is working!")
        print("\n📝 Next steps:")
        print("   1. Upload a PDF via frontend (http://localhost:3001)")
        print("   2. Test WebSocket chat connection")
        print("   3. Send a chat message and verify response")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("   Make sure the backend server is running:")
        print("   cd backend && uv run uvicorn main:app --reload")
    
    print("="*70)

if __name__ == "__main__":
    main()
