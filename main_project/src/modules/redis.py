from utils.lazy_module import LazyModule 
import json
# pip install redis hiredis 

redis = LazyModule("redis")
from datetime import timedelta

class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0):
        # db 0 is default for redis among 16 other logical databases
        self.client = redis.Redis(host=host, port=port, db=db)

    def get(self, key):
        data = self.client.get(key)
        return json.loads(data) if data else None
    
    def set(self, key, value, ex=None):
        self.client.set(name=key, value=json.dumps(value), nx=True, ex=ex)
    
    def exists(self, key):
        return self.client.exists(key) > 0
    
    def delete(self, key):
        self.client.delete(key)
    
    
    
    
    
            
            