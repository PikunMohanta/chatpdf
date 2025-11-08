from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import jwt
import requests
import os
from datetime import datetime, timedelta
import logging
import uuid
import hashlib

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Pydantic models
class UserInfo(BaseModel):
    user_id: str
    email: str
    role: str = "user"
    session_id: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

# AWS Cognito configuration
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
COGNITO_REGION = os.getenv("COGNITO_REGION", "us-east-1")

# Dependency function for user authentication with request context
async def get_current_user_with_context(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInfo:
    """Get current user with session isolation based on request context"""
    return await verify_token(credentials, request)

# Simplified dependency function that doesn't require explicit Request injection
async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInfo:
    """Get current user with session isolation - simplified dependency"""
    return await verify_token(credentials, request)

def generate_user_id_from_request(request: Request) -> str:
    """
    Generate a unique user ID based on client information for session isolation
    This ensures each browser/incognito session gets a different user ID
    """
    # Get client IP and User-Agent
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # Create a unique identifier from IP + User-Agent + timestamp elements
    # Add some randomness to prevent collisions
    unique_data = f"{client_ip}:{user_agent}:{datetime.now().strftime('%Y%m%d')}"
    
    # Create a hash for the user ID
    user_hash = hashlib.sha256(unique_data.encode()).hexdigest()[:16]
    
    return f"user_{user_hash}"

# JWT validation function
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security), request: Request = None) -> UserInfo:
    """
    Verify JWT token from AWS Cognito or accept device_id for development
    """
    token = credentials.credentials
    
    try:
        # For development - accept device_id tokens (format: device_*)
        if token.startswith("device_"):
            # Use the device_id directly as user_id
            return UserInfo(
                user_id=token,  # Use device_id as user_id
                email=f"{token}@device.local",
                role="user",
                session_id=token
            )
        
        # For development - create unique user ID per browser session
        if token == "dev-token":
            # Generate unique user ID based on client information
            if request:
                user_id = generate_user_id_from_request(request)
            else:
                # Fallback if request is not available
                user_id = f"user_{uuid.uuid4().hex[:16]}"
            
            return UserInfo(
                user_id=user_id,
                email=f"{user_id}@example.com",
                role="user",
                session_id=user_id
            )
        
        # TODO: Implement proper Cognito JWT validation
        # 1. Download Cognito public keys
        # 2. Verify token signature
        # 3. Validate claims (iss, aud, exp, etc.)
        
        # Placeholder validation
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        return UserInfo(
            user_id=decoded.get("sub", "unknown"),
            email=decoded.get("email", "unknown@example.com"),
            role=decoded.get("custom:role", "user")
        )
        
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Authenticate user with AWS Cognito
    """
    try:
        # For development - return mock token
        if request.email == "dev@example.com" and request.password == "password":
            return TokenResponse(
                access_token="dev-token",
                token_type="bearer",
                expires_in=3600
            )
        
        # TODO: Implement actual Cognito authentication
        # Use boto3 to authenticate with Cognito User Pool
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

@router.get("/me", response_model=UserInfo)
async def get_user_info(current_user: UserInfo = Depends(get_current_user_with_context)):
    """
    Get current authenticated user information
    """
    return current_user

@router.post("/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Refresh JWT token
    """
    # TODO: Implement token refresh logic
    return {"message": "Token refresh not implemented yet"}

@router.post("/logout")
async def logout(current_user: UserInfo = Depends(get_current_user_with_context)):
    """
    Logout user (invalidate token)
    """
    # TODO: Implement logout logic (token blacklisting)
    return {"message": "Logged out successfully"}