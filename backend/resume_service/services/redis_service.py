import redis
import os
from typing import Optional

class RedisService:
    def __init__(self):
        """Initialize Redis connection with environment variables"""
        self.client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            password=os.getenv('REDIS_PASSWORD', None),
            decode_responses=True
        )
        self.default_expiry = 3600  # 1 hour default

    def get_resume_status(self, resume_id: str) -> Optional[str]:
        """
        Get the processing status of a resume
        
        Args:
            resume_id (str): The ID of the resume
            
        Returns:
            Optional[str]: The status if found, None otherwise
        """
        return self.client.get(f"resume:{resume_id}:status")

    def set_resume_status(self, resume_id: str, status: str, expire: int = None):
        """
        Set the processing status of a resume
        
        Args:
            resume_id (str): The ID of the resume
            status (str): The status to set
            expire (int, optional): Expiration time in seconds
        """
        key = f"resume:{resume_id}:status"
        self.client.set(key, status)
        if expire or self.default_expiry:
            self.client.expire(key, expire or self.default_expiry)

    def clear_resume_status(self, resume_id: str):
        """
        Clear the status for a resume
        
        Args:
            resume_id (str): The ID of the resume
        """
        self.client.delete(f"resume:{resume_id}:status")

    def get_cache(self, key: str) -> Optional[str]:
        """
        Get a cached value
        
        Args:
            key (str): The cache key
            
        Returns:
            Optional[str]: The cached value if found, None otherwise
        """
        return self.client.get(key)

    def set_cache(self, key: str, value: str, expire: int = None):
        """
        Set a cached value
        
        Args:
            key (str): The cache key
            value (str): The value to cache
            expire (int, optional): Expiration time in seconds
        """
        self.client.set(key, value)
        if expire or self.default_expiry:
            self.client.expire(key, expire or self.default_expiry)

    def clear_cache(self, key: str):
        """
        Clear a cached value
        
        Args:
            key (str): The cache key
        """
        self.client.delete(key) 