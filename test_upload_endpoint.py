import requests

# Test the upload endpoint
print("Testing upload endpoint...")
print("=" * 50)

# Test OPTIONS request (CORS preflight)
try:
    response = requests.options("http://localhost:8000/api/upload")
    print(f"OPTIONS /api/upload: {response.status_code}")
    print(f"CORS headers: {response.headers.get('access-control-allow-origin')}")
except Exception as e:
    print(f"Error: {e}")

print()

# Test health endpoint
try:
    response = requests.get("http://localhost:8000/health")
    print(f"GET /health: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

print()

# List all available routes
try:
    response = requests.get("http://localhost:8000/docs")
    print(f"API Docs available at: http://localhost:8000/docs")
    print(f"Status: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
