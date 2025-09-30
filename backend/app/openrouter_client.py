"""
Custom OpenRouter client to bypass OpenAI client library issues
"""
import requests
import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger(__name__)

class OpenRouterClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Newchat PDF Assistant"
        }
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "meta-llama/llama-3.1-8b-instruct",
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Optional[str]:
        """
        Create a chat completion using OpenRouter API
        """
        try:
            data = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"OpenRouter client error: {str(e)}")
            return None
    
    def is_available(self) -> bool:
        """Check if OpenRouter is available"""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False

# Global OpenRouter client instance
openrouter_client = None

def get_openrouter_client() -> Optional[OpenRouterClient]:
    """Get the global OpenRouter client instance"""
    global openrouter_client
    
    if openrouter_client is None:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key and api_key != "your-openrouter-api-key":
            openrouter_client = OpenRouterClient(api_key)
    
    return openrouter_client

def is_openrouter_enabled() -> bool:
    """Check if OpenRouter is configured and available"""
    client = get_openrouter_client()
    return client is not None and client.is_available()

def generate_response(messages: List[Dict[str, str]]) -> str:
    """
    Generate a response using OpenRouter or mock response
    """
    client = get_openrouter_client()
    
    if client:
        response = client.chat_completion(messages)
        if response:
            return response
    
    # Fallback to mock response
    user_message = messages[-1]["content"] if messages else "Hello"
    return f"Mock response: I received your message '{user_message}'. This is a development response since OpenRouter is not configured."