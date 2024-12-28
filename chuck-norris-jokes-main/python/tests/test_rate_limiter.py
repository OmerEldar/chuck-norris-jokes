import pytest
from unittest.mock import Mock, patch
from redis import Redis
from rate_limiter import RateLimiter
from redis_connection import RedisConnection, RedisConnectionError

class TestRateLimiter:
    @pytest.fixture
    def redis_mock(self):
        """Create mock Redis client"""
        mock = Mock(spec=Redis)
        return mock

    @pytest.fixture
    def redis_connection(self, redis_mock):
        """Create RedisConnection with mock client"""
        connection = Mock(spec=RedisConnection)
        connection.get_client.return_value = redis_mock
        return connection

    def test_init_with_connection(self, redis_connection, redis_mock):
        """Should use provided Redis connection"""
        limiter = RateLimiter(redis_connection)
        assert limiter.redis is redis_mock

    @patch('rate_limiter.RedisConnection')
    def test_init_without_connection(self, mock_connection_class):
        """Should create new connection if none provided"""
        mock_redis = Mock(spec=Redis)
        mock_connection = Mock()
        mock_connection.get_client.return_value = mock_redis
        mock_connection_class.return_value = mock_connection

        limiter = RateLimiter()

        assert limiter.redis is mock_redis

    def test_rate_limit_exceeded(self, redis_connection, redis_mock):
        """Should block when rate limit exceeded"""
        limiter = RateLimiter(redis_connection)
        redis_mock.get.return_value = "1"
        
        result = limiter.is_allowed("test-token", rate_limit=1, daily_limit=50)
        
        assert result is False

    def test_daily_limit_exceeded(self, redis_connection, redis_mock):
        """Should block when daily limit exceeded"""
        limiter = RateLimiter(redis_connection)
        redis_mock.get.side_effect = ["0", "50"]
        
        result = limiter.is_allowed("test-token", rate_limit=1, daily_limit=50)
        
        assert result is False