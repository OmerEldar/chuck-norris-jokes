import pytest
from unittest.mock import patch, MagicMock
from redis import Redis, ConnectionError
from redis_connection import get_redis
import redis_connection
import logging

@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the module-level singleton before each test"""
    redis_connection._redis_client = None
    yield

@pytest.fixture(autouse=True)
def setup_logging(caplog):
    """Setup logging for tests"""
    caplog.set_level(logging.INFO)
    yield

@pytest.fixture
def mock_redis():
    with patch('redis_connection.Redis') as mock:
        # Configure the mock Redis instance
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock

def test_get_redis_creates_connection_once(mock_redis):
    """Test that Redis connection is created only once"""
    # First call
    redis1 = get_redis()
    # Second call
    redis2 = get_redis()
    
    # Redis constructor should be called only once
    mock_redis.assert_called_once_with(host='localhost', port=6379, db=0)
    # Both calls should return the same instance
    assert redis1 == redis2

def test_get_redis_verifies_connection(mock_redis):
    """Test that connection is verified with ping"""
    get_redis()
    mock_redis.return_value.ping.assert_called_once()

def test_get_redis_handles_connection_error(mock_redis):
    """Test that connection error is handled properly"""
    # Configure mock to raise error on ping
    mock_redis.return_value.ping.side_effect = ConnectionError("Connection failed")
    
    with pytest.raises(ConnectionError) as exc_info:
        get_redis()
    
    assert str(exc_info.value) == "Connection failed"

def test_get_redis_logs_success(mock_redis, caplog):
    """Test that successful connection is logged"""
    get_redis()
    assert "Successfully connected to Redis" in caplog.text

def test_get_redis_logs_failure(mock_redis, caplog):
    """Test that connection failure is logged"""
    mock_redis.return_value.ping.side_effect = ConnectionError("Connection failed")
    
    with pytest.raises(ConnectionError):
        get_redis()
    
    assert "Failed to connect to Redis" in caplog.text 