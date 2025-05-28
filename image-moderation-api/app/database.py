import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List, Dict, Any
from datetime import datetime

class Database:
    """MongoDB database management class"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.tokens_collection = None
        self.usages_collection = None
        
    async def connect(self):
        """Connect to MongoDB"""
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        db_name = os.getenv("DB_NAME", "image_moderation")
        
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]
        self.tokens_collection = self.db.tokens
        self.usages_collection = self.db.usages
        
        # Create indexes for better performance
        await self.create_indexes()
        
        # Create initial admin token if none exists
        await self.create_initial_admin_token()
        
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
    
    async def create_indexes(self):
        """Create database indexes"""
        await self.tokens_collection.create_index("token", unique=True)
        await self.tokens_collection.create_index("createdAt")
        await self.usages_collection.create_index("token")
        await self.usages_collection.create_index("timestamp")
        
    async def create_initial_admin_token(self):
        """Create an initial admin token if none exists"""
        admin_count = await self.tokens_collection.count_documents({"isAdmin": True})
        if admin_count == 0:
            import secrets
            admin_token = secrets.token_urlsafe(32)
            await self.tokens_collection.insert_one({
                "token": admin_token,
                "isAdmin": True,
                "createdAt": datetime.utcnow()
            })
            print(f"Initial admin token created: {admin_token}")
    
    # Token operations
    async def create_token(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new token"""
        result = await self.tokens_collection.insert_one(token_data)
        return await self.tokens_collection.find_one({"_id": result.inserted_id})
    
    async def get_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get a token by value"""
        return await self.tokens_collection.find_one({"token": token})
    
    async def get_all_tokens(self) -> List[Dict[str, Any]]:
        """Get all tokens"""
        cursor = self.tokens_collection.find().sort("createdAt", -1)
        return await cursor.to_list(None)
    
    async def delete_token(self, token: str) -> bool:
        """Delete a token"""
        result = await self.tokens_collection.delete_one({"token": token})
        return result.deleted_count > 0
    
    # Usage operations
    async def log_usage(self, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log API usage"""
        result = await self.usages_collection.insert_one(usage_data)
        return await self.usages_collection.find_one({"_id": result.inserted_id})
    
    async def get_usage_stats(self, token: str = None) -> Dict[str, Any]:
        """Get usage statistics"""
        match_filter = {"token": token} if token else {}
        
        pipeline = [
            {"$match": match_filter},
            {"$group": {
                "_id": "$endpoint",
                "count": {"$sum": 1},
                "last_used": {"$max": "$timestamp"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        cursor = self.usages_collection.aggregate(pipeline)
        usage_by_endpoint = await cursor.to_list(None)
        
        total_requests = await self.usages_collection.count_documents(match_filter)
        
        return {
            "total_requests": total_requests,
            "usage_by_endpoint": usage_by_endpoint
        } 