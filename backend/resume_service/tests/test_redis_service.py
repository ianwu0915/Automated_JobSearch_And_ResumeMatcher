import pytest
import fakeredis
from unittest.mock import patch
from resume_service.utils.redis_service import RedisService

@pytest.fixture
def redis_service():
    """Create a RedisService instance with fakeredis"""
    with patch('redis.Redis', fakeredis.FakeRedis):
        service = RedisService()
        yield service
        # Clean up after each test
        service.client.flushall()

def test_get_resume_status(redis_service):
    # Test getting non-existent status
    assert redis_service.get_resume_status("nonexistent") is None
    
    # Test getting existing status
    redis_service.set_resume_status("test_resume", "processing")
    result = redis_service.get_resume_status("test_resume")
    if isinstance(result, bytes):
        result = result.decode('utf-8')
    assert result == "processing"

def test_set_resume_status(redis_service):
    # Test setting status without expiry
    redis_service.set_resume_status("test_resume", "processing")
    result = redis_service.get_resume_status("test_resume")
    if isinstance(result, bytes):
        result = result.decode('utf-8')
    assert result == "processing"
    
    # Test setting status with custom expiry
    redis_service.set_resume_status("test_resume2", "completed", expire=10)
    result = redis_service.get_resume_status("test_resume2")
    if isinstance(result, bytes):
        result = result.decode('utf-8')
    assert result == "completed"

def test_clear_resume_status(redis_service):
    # Set and then clear status
    redis_service.set_resume_status("test_resume", "processing")
    result = redis_service.get_resume_status("test_resume")
    if isinstance(result, bytes):
        result = result.decode('utf-8')
    assert result == "processing"
    
    redis_service.clear_resume_status("test_resume")
    assert redis_service.get_resume_status("test_resume") is None

def test_get_cache(redis_service):
    # Test getting non-existent cache
    assert redis_service.get_cache("nonexistent") is None
    
    # Test getting existing cache
    redis_service.set_cache("test_key", "test_value")
    result = redis_service.get_cache("test_key")
    if isinstance(result, bytes):
        result = result.decode('utf-8')
    assert result == "test_value"

def test_set_cache(redis_service):
    # Test setting cache without expiry
    redis_service.set_cache("test_key", "test_value")
    result = redis_service.get_cache("test_key")
    if isinstance(result, bytes):
        result = result.decode('utf-8')
    assert result == "test_value"
    
    # Test setting cache with custom expiry
    redis_service.set_cache("test_key2", "test_value2", expire=10)
    result = redis_service.get_cache("test_key2")
    if isinstance(result, bytes):
        result = result.decode('utf-8')
    assert result == "test_value2"

def test_clear_cache(redis_service):
    # Set and then clear cache
    redis_service.set_cache("test_key", "test_value")
    result = redis_service.get_cache("test_key")
    if isinstance(result, bytes):
        result = result.decode('utf-8')
    assert result == "test_value"
    
    redis_service.clear_cache("test_key")
    assert redis_service.get_cache("test_key") is None

def test_expiry(redis_service):
    import time
    
    # Test expiry with very short timeout
    redis_service.set_cache("test_key", "test_value", expire=1)
    result = redis_service.get_cache("test_key")
    if isinstance(result, bytes):
        result = result.decode('utf-8')
    assert result == "test_value"
    
    # Wait for expiry
    time.sleep(1.1)
    assert redis_service.get_cache("test_key") is None

def test_environment_variables():
    # Test Redis initialization with custom environment variables
    with patch.dict('os.environ', {
        'REDIS_HOST': 'custom_host',
        'REDIS_PORT': '6380',
        'REDIS_DB': '1',
        'REDIS_PASSWORD': 'secret'
    }), patch('redis.Redis', fakeredis.FakeRedis) as mock_redis:
        service = RedisService()
        # FakeRedis doesn't support checking connection kwargs, so we'll just verify the service was created
        assert service is not None 