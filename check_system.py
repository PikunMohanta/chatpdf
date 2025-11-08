#!/usr/bin/env python3
"""
PDFPixie System Check
Verifies that all components are properly configured and working
"""
import os
import sys
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def check_environment():
    """Check environment variables"""
    print("\n" + "="*50)
    print("1. Checking Environment Variables")
    print("="*50)
    
    # Load .env file
    env_path = Path(__file__).parent / 'backend' / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print_success(f"Found .env file: {env_path}")
    else:
        print_error(f".env file not found at {env_path}")
        return False
    
    # Check OpenRouter API key
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    if openrouter_key and openrouter_key != 'your-openrouter-api-key':
        print_success(f"OpenRouter API Key: {openrouter_key[:20]}...")
    else:
        print_error("OpenRouter API Key not configured")
        return False
    
    return True

def check_openrouter_api():
    """Test OpenRouter API connection"""
    print("\n" + "="*50)
    print("2. Testing OpenRouter API")
    print("="*50)
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'http://localhost:3000',
        'X-Title': 'PDFPixie Test'
    }
    
    # Test models endpoint
    try:
        print_info("Testing models endpoint...")
        resp = requests.get('https://openrouter.ai/api/v1/models', headers=headers, timeout=10)
        if resp.status_code == 200:
            print_success("Models endpoint is accessible")
        else:
            print_error(f"Models endpoint returned status {resp.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to connect to OpenRouter: {e}")
        return False
    
    # Test chat completion
    try:
        print_info("Testing chat completion...")
        data = {
            "model": "meta-llama/llama-3.1-8b-instruct",
            "messages": [{"role": "user", "content": "Say 'API is working!' in 5 words or less."}],
            "max_tokens": 20
        }
        resp = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        if resp.status_code == 200:
            result = resp.json()
            response_text = result["choices"][0]["message"]["content"]
            print_success(f"Chat completion works! Response: {response_text}")
        else:
            print_error(f"Chat completion failed with status {resp.status_code}")
            print_error(f"Response: {resp.text}")
            return False
    except Exception as e:
        print_error(f"Chat completion error: {e}")
        return False
    
    return True

def check_backend():
    """Check if backend is running"""
    print("\n" + "="*50)
    print("3. Checking Backend Server")
    print("="*50)
    
    try:
        resp = requests.get('http://localhost:8000/health', timeout=5)
        if resp.status_code == 200:
            print_success("Backend is running on http://localhost:8000")
            data = resp.json()
            print_info(f"Service: {data.get('service', 'unknown')}")
            print_info(f"Status: {data.get('status', 'unknown')}")
            return True
        else:
            print_error(f"Backend returned status {resp.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Backend is NOT running on http://localhost:8000")
        print_warning("Please start the backend with: cd backend && uvicorn main:socket_app --reload")
        return False
    except Exception as e:
        print_error(f"Error checking backend: {e}")
        return False

def check_frontend():
    """Check if frontend is running"""
    print("\n" + "="*50)
    print("4. Checking Frontend Server")
    print("="*50)
    
    try:
        resp = requests.get('http://localhost:5173', timeout=5)
        if resp.status_code == 200:
            print_success("Frontend is running on http://localhost:5173")
            return True
        else:
            print_warning(f"Frontend returned status {resp.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Frontend is NOT running on http://localhost:5173")
        print_warning("Please start the frontend with: cd frontend && npm run dev")
        return False
    except Exception as e:
        print_error(f"Error checking frontend: {e}")
        return False

def check_directories():
    """Check required directories"""
    print("\n" + "="*50)
    print("5. Checking Directory Structure")
    print("="*50)
    
    required_dirs = [
        'backend/data',
        'backend/data/uploads',
        'backend/data/chromadb',
        'backend/data/mock_embeddings',
        'backend/data/database',
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = Path(__file__).parent / dir_path
        if full_path.exists():
            print_success(f"{dir_path}")
        else:
            print_warning(f"{dir_path} (creating...)")
            full_path.mkdir(parents=True, exist_ok=True)
    
    return all_exist

def check_dependencies():
    """Check Python dependencies"""
    print("\n" + "="*50)
    print("6. Checking Python Dependencies")
    print("="*50)
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'python-socketio',
        'python-dotenv',
        'requests',
        'PyMuPDF',
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package.replace('-', '_').lower())
            print_success(package)
        except ImportError:
            print_error(f"{package} is not installed")
            all_installed = False
    
    return all_installed

def main():
    print(f"{Colors.BLUE}{'='*50}")
    print("PDFPixie System Check")
    print(f"{'='*50}{Colors.END}")
    
    results = {
        'environment': check_environment(),
        'openrouter': check_openrouter_api(),
        'backend': check_backend(),
        'frontend': check_frontend(),
        'directories': check_directories(),
        'dependencies': check_dependencies(),
    }
    
    print("\n" + "="*50)
    print("Summary")
    print("="*50)
    
    all_passed = all(results.values())
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check.capitalize():20s} {status}")
    
    print("\n" + "="*50)
    if all_passed:
        print_success("All checks passed! Your PDFPixie instance is ready.")
        print_info("\nYou can now:")
        print_info("  1. Open http://localhost:5173 in your browser")
        print_info("  2. Upload a PDF document")
        print_info("  3. Start chatting with your PDF!")
    else:
        print_error("Some checks failed. Please fix the issues above.")
        print_info("\nQuick fixes:")
        print_info("  - Start backend: cd backend && uvicorn main:socket_app --reload")
        print_info("  - Start frontend: cd frontend && npm run dev")
        print_info("  - Install deps: cd backend && pip install -r requirements.txt")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
