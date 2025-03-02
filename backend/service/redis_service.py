import redis
import os
from typing import Optional

from backend.utils.lazy_module import LazyModule 
import json
# pip install redis hiredis 

redis = LazyModule("redis")
from datetime import timedelta

import json
import redis

class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0):
        # db 0 is default for redis among 16 other logical databases
        self.client = redis.Redis(host=host, port=port, db=db)

    def get(self, key):
        """Get value from Redis and deserialize if it's JSON"""
        data = self.client.get(key)
        if data:
            # Check if it's bytes and decode it first
            if isinstance(data, bytes):
                try:
                    return json.loads(data.decode('utf-8'))
                except json.JSONDecodeError:
                    return data.decode('utf-8')
            return data
        return None
    
    def set(self, key, value, ex=None):
        """Set value in Redis with optional expiry, serializing if needed"""
        # Serialize value if it's a dict or list
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        self.client.set(name=key, value=value, ex=ex)
    
    def exists(self, key):
        """Check if key exists in Redis"""
        return self.client.exists(key) > 0
    
    def delete(self, key):
        """Delete key from Redis"""
        self.client.delete(key)      
    
    def generate_cache_key(self, prefix, identifier):
        """
        Generate a consistent cache key with a prefix and identifier.
        """
        return f"{prefix}:{identifier}"


# class RedisService:
#     def __init__(self):
#         """Initialize Redis connection with environment variables"""
#         self.client = redis.Redis(
#             host=os.getenv('REDIS_HOST', 'localhost'),
#             port=int(os.getenv('REDIS_PORT', 6379)),
#             db=int(os.getenv('REDIS_DB', 0)),
#             password=os.getenv('REDIS_PASSWORD', None),
#             decode_responses=True
#         )
#         self.default_expiry = 3600  # 1 hour default

#     def get_resume_status(self, resume_id: str) -> Optional[str]:
#         """
#         Get the processing status of a resume
        
#         Args:
#             resume_id (str): The ID of the resume
            
#         Returns:
#             Optional[str]: The status if found, None otherwise
#         """
#         return self.client.get(f"resume:{resume_id}:status")

#     def set_resume_status(self, resume_id: str, status: str, expire: int = None):
#         """
#         Set the processing status of a resume
        
#         Args:
#             resume_id (str): The ID of the resume
#             status (str): The status to set
#             expire (int, optional): Expiration time in seconds
#         """
#         key = f"resume:{resume_id}:status"
#         self.client.set(key, status)
#         if expire or self.default_expiry:
#             self.client.expire(key, expire or self.default_expiry)

#     def clear_resume_status(self, resume_id: str):
#         """
#         Clear the status for a resume
        
#         Args:
#             resume_id (str): The ID of the resume
#         """
#         self.client.delete(f"resume:{resume_id}:status")

#     def get_cache(self, key: str) -> Optional[str]:
#         """
#         Get a cached value
        
#         Args:
#             key (str): The cache key
            
#         Returns:
#             Optional[str]: The cached value if found, None otherwise
#         """
#         return self.client.get(key)

#     def set_cache(self, key: str, value: str, expire: int = None):
#         """
#         Set a cached value
        
#         Args:
#             key (str): The cache key
#             value (str): The value to cache
#             expire (int, optional): Expiration time in seconds
#         """
#         self.client.set(key, value)
#         if expire or self.default_expiry:
#             self.client.expire(key, expire or self.default_expiry)

#     def clear_cache(self, key: str):
#         """
#         Clear a cached value
        
#         Args:
#             key (str): The cache key
#         """
#         self.client.delete(key) 