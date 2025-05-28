import secrets
from typing import Optional, List
from datetime import datetime

from .models import Token, Usage
from .database import Database

class AuthService:
    """Authentication service for token management"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def create_token(self, is_admin: bool = False) -> Token:
        """Create a new authentication token"""
        token_value = secrets.token_urlsafe(32)
        token_data = {
            "token": token_value,
            "isAdmin": is_admin,
            "createdAt": datetime.utcnow()
        }
        
        # Save to database
        await self.db.create_token(token_data)
        
        return Token(**token_data)
    
    async def validate_token(self, token_value: str) -> Optional[Token]:
        """Validate a token and return token data if valid"""
        token_data = await self.db.get_token(token_value)
        if token_data:
            # Remove MongoDB's _id field
            token_data.pop('_id', None)
            return Token(**token_data)
        return None
    
    async def get_all_tokens(self) -> List[Token]:
        """Get all tokens"""
        tokens_data = await self.db.get_all_tokens()
        tokens = []
        for token_data in tokens_data:
            # Remove MongoDB's _id field
            token_data.pop('_id', None)
            tokens.append(Token(**token_data))
        return tokens
    
    async def delete_token(self, token_value: str) -> bool:
        """Delete a token"""
        return await self.db.delete_token(token_value)
    
    async def log_usage(self, token_value: str, endpoint: str) -> Usage:
        """Log API usage"""
        usage_data = {
            "token": token_value,
            "endpoint": endpoint,
            "timestamp": datetime.utcnow()
        }
        
        # Save to database
        await self.db.log_usage(usage_data)
        
        return Usage(**usage_data) 