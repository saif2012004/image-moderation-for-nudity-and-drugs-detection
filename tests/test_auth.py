import pytest
import asyncio
from datetime import datetime
from app.auth import AuthService
from app.database import Database
from app.models import Token

class MockDatabase:
    def __init__(self):
        self.tokens = {}
        self.usages = []
    
    async def connect(self):
        pass
    
    async def disconnect(self):
        pass
    
    async def create_token(self, token_data):
        self.tokens[token_data["token"]] = token_data
        return token_data
    
    async def get_token(self, token):
        return self.tokens.get(token)
    
    async def get_all_tokens(self):
        return list(self.tokens.values())
    
    async def delete_token(self, token):
        if token in self.tokens:
            del self.tokens[token]
            return True
        return False
    
    async def log_usage(self, usage_data):
        self.usages.append(usage_data)
        return usage_data

@pytest.fixture
async def auth_service():
    db = MockDatabase()
    service = AuthService(db)
    return service

@pytest.mark.asyncio
async def test_create_token(auth_service):
    """Test token creation"""
    token = await auth_service.create_token(is_admin=False)
    
    assert isinstance(token, Token)
    assert len(token.token) > 20  # Token should be reasonably long
    assert token.isAdmin == False
    assert isinstance(token.createdAt, datetime)

@pytest.mark.asyncio
async def test_create_admin_token(auth_service):
    """Test admin token creation"""
    token = await auth_service.create_token(is_admin=True)
    
    assert isinstance(token, Token)
    assert token.isAdmin == True

@pytest.mark.asyncio
async def test_validate_token(auth_service):
    """Test token validation"""
    # Create a token first
    created_token = await auth_service.create_token(is_admin=False)
    
    # Validate the token
    validated_token = await auth_service.validate_token(created_token.token)
    
    assert validated_token is not None
    assert validated_token.token == created_token.token
    assert validated_token.isAdmin == created_token.isAdmin

@pytest.mark.asyncio
async def test_validate_invalid_token(auth_service):
    """Test validation of invalid token"""
    result = await auth_service.validate_token("invalid_token")
    assert result is None

@pytest.mark.asyncio
async def test_delete_token(auth_service):
    """Test token deletion"""
    # Create a token first
    token = await auth_service.create_token(is_admin=False)
    
    # Delete the token
    result = await auth_service.delete_token(token.token)
    assert result == True
    
    # Try to validate deleted token
    validated = await auth_service.validate_token(token.token)
    assert validated is None

@pytest.mark.asyncio
async def test_get_all_tokens(auth_service):
    """Test getting all tokens"""
    # Create multiple tokens
    token1 = await auth_service.create_token(is_admin=False)
    token2 = await auth_service.create_token(is_admin=True)
    
    # Get all tokens
    all_tokens = await auth_service.get_all_tokens()
    
    assert len(all_tokens) == 2
    token_values = [t.token for t in all_tokens]
    assert token1.token in token_values
    assert token2.token in token_values

@pytest.mark.asyncio
async def test_log_usage(auth_service):
    """Test usage logging"""
    # Create a token first
    token = await auth_service.create_token(is_admin=False)
    
    # Log usage
    usage = await auth_service.log_usage(token.token, "/moderate")
    
    assert usage.token == token.token
    assert usage.endpoint == "/moderate"
    assert isinstance(usage.timestamp, datetime) 