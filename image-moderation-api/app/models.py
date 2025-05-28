from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class Token(BaseModel):
    """Token model for authentication"""
    token: str
    isAdmin: bool = False
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Usage(BaseModel):
    """Usage tracking model"""
    token: str
    endpoint: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ModerationCategory(BaseModel):
    """Individual moderation category result"""
    category: str
    confidence: float = Field(ge=0.0, le=1.0)
    flagged: bool

class ModerationResult(BaseModel):
    """Result of image moderation"""
    filename: str
    safe: bool
    categories: List[ModerationCategory]
    overall_confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TokenCreate(BaseModel):
    """Model for token creation request"""
    isAdmin: bool = False 