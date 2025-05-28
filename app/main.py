from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from datetime import datetime, timezone

from .database import Database
from .models import Token, Usage, ModerationResult
from .auth import AuthService
from .moderation import ModerationService

app = FastAPI(
    title="Image Moderation API",
    description="API for image content moderation with token-based authentication",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services
db = Database()
auth_service = AuthService(db)
moderation_service = ModerationService()

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await db.connect()

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await db.disconnect()

# Dependency for token validation
async def get_current_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Token:
    """Validate and return the current token"""
    token_data = await auth_service.validate_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return token_data

# Dependency for admin token validation
async def get_admin_token(token: Token = Depends(get_current_token)) -> Token:
    """Ensure the current token has admin privileges"""
    if not token.isAdmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return token

# Authentication endpoints (Admin-only)
@app.post("/auth/tokens", response_model=Token)
async def create_token(
    isAdmin: bool = False,
    admin_token: Token = Depends(get_admin_token)
):
    """Create a new authentication token"""
    token = await auth_service.create_token(isAdmin)
    await auth_service.log_usage(admin_token.token, "/auth/tokens")
    return token

@app.get("/auth/tokens", response_model=List[Token])
async def get_tokens(admin_token: Token = Depends(get_admin_token)):
    """Get all authentication tokens"""
    tokens = await auth_service.get_all_tokens()
    await auth_service.log_usage(admin_token.token, "/auth/tokens")
    return tokens

@app.delete("/auth/tokens/{token_value}")
async def delete_token(
    token_value: str,
    admin_token: Token = Depends(get_admin_token)
):
    """Delete a specific authentication token"""
    success = await auth_service.delete_token(token_value)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    await auth_service.log_usage(admin_token.token, f"/auth/tokens/{token_value}")
    return {"message": "Token deleted successfully"}

# Moderation endpoint
@app.post("/moderate", response_model=ModerationResult)
async def moderate_image(
    file: UploadFile = File(...),
    current_token: Token = Depends(get_current_token)
):
    """Analyze an uploaded image for content safety"""
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Read the image data
    image_data = await file.read()
    
    # Perform moderation
    result = await moderation_service.moderate_image(image_data, file.filename)
    
    # Log usage
    await auth_service.log_usage(current_token.token, "/moderate")
    
    return result

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7000) 