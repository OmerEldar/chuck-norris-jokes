import pytest
from unittest.mock import Mock, patch, call
from redis import Redis
from rate_limiter import RateLimiter

class TestRateLimiter:
    @pytest.fixture
    def redis_mock(self):
        """Create mock Redis client"""
        return Mock(spec=Redis)

    @pytest.fixture
    def mock_get_redis(self, redis_mock):
        """Mock get_redis function"""
        with patch('rate_limiter.get_redis', return_value=redis_mock):
            yield redis_mock
            
    @pytest.fixture
    def limiter(self, mock_get_redis):
        """Create RateLimiter instance with mocked Redis"""
        return RateLimiter()

    def test_init(self, mock_get_redis):
        """Should use Redis connection from get_redis"""
        limiter = RateLimiter()
        assert limiter.redis is mock_get_redis

    def test_increment_key_new(self, limiter, mock_get_redis):
        """Should set expiration for new key"""
        mock_get_redis.get.return_value = None
        
        count = limiter._increment_key("test:key", expiration=60)
        
        assert count == 1
        mock_get_redis.setex.assert_called_once_with("test:key", 60, 1)

    def test_increment_key_existing(self, limiter, mock_get_redis):
        """Should increment existing key"""
        mock_get_redis.incr.return_value = 6
        
        count = limiter._increment_key("test:key", expiration=60)
        
        assert count == 6
        mock_get_redis.incr.assert_called_once_with("test:key")

    def test_is_within_limit_under(self, limiter, mock_get_redis):
        """Should allow when under limit"""
        mock_get_redis.get.return_value = None
        
        result = limiter._is_within_limit("test:key", limit=5, expiration=60)
        
        assert result is True

    def test_is_within_limit_at_limit(self, limiter, mock_get_redis):
        """Should allow when at limit"""
        mock_get_redis.incr.return_value = 5
        
        result = limiter._is_within_limit("test:key", limit=5, expiration=60)
        
        assert result is True

    def test_is_within_limit_over(self, limiter, mock_get_redis):
        """Should block when over limit"""
        mock_get_redis.incr.return_value = 6
        
        result = limiter._is_within_limit("test:key", limit=5, expiration=60)
        
        assert result is False

    def test_rate_limit_exceeded(self, limiter, mock_get_redis):
        """Should block when rate limit exceeded"""
        with patch('rate_limiter.get_current_timestamp', return_value=1000):
            # Configure Redis mock
            mock_get_redis.get.return_value = "1"  # Key exists
            mock_get_redis.incr.return_value = 2   # Over limit
            
            result = limiter.is_allowed("test-token", rate_limit=1, daily_limit=50)
            
            assert result is False
            mock_get_redis.get.assert_called_with("rate:test-token:1000")

    def test_daily_limit_exceeded(self, limiter, mock_get_redis):
        """Should block when daily limit exceeded"""
        with patch('rate_limiter.get_current_timestamp', return_value=1000), \
             patch('rate_limiter.get_start_of_day_timestamp', return_value=900):
            
            # Configure Redis mock for both checks
            def get_side_effect(key):
                if key == "rate:test-token:1000":
                    return None  # Rate limit check passes
                if key == "daily:test-token:900":
                    return "5"   # Daily limit at max
                return None
                
            mock_get_redis.get.side_effect = get_side_effect
            mock_get_redis.incr.return_value = 6  # Over daily limit
            
            result = limiter.is_allowed("test-token", rate_limit=1, daily_limit=5)
            
            assert result is False
            expected_calls = [
                call("rate:test-token:1000"),
                call("daily:test-token:900")
            ]
            mock_get_redis.get.assert_has_calls(expected_calls, any_order=True)

    @patch('utils.time_helpers.get_start_of_day_timestamp')
    @patch('utils.time_helpers.get_current_timestamp')
    def test_within_all_limits(self, mock_time, mock_day_start, limiter, mock_get_redis):
        """Should allow when within both limits"""
        mock_time.return_value = 1000
        mock_day_start.return_value = 900
        mock_get_redis.get.side_effect = [None, None]
        mock_get_redis.incr.side_effect = [1, 1]
        
        result = limiter.is_allowed("test-token", rate_limit=1, daily_limit=5)
        
        assert result is True

    def test_no_daily_limit(self, limiter, mock_get_redis):
        """Should only check rate limit when no daily limit specified"""
        mock_get_redis.get.return_value = None
        
        result = limiter.is_allowed("test-token", rate_limit=1)
        
        assert result is True
        assert mock_get_redis.get.call_count == 1  # Only one Redis get call