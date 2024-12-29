import pytest
from unittest.mock import Mock, patch, call
from redis import Redis
from rate_limiter import RateLimiter, SECONDS_IN_DAY

class TestRateLimiter:
    @pytest.fixture
    def redis_mock(self):
        return Mock(spec=Redis)

    @pytest.fixture
    def mock_get_redis(self, redis_mock):
        with patch('rate_limiter.get_redis', return_value=redis_mock):
            yield redis_mock
            
    @pytest.fixture
    def limiter(self, mock_get_redis):
        return RateLimiter()

    def test_init(self, mock_get_redis):
        limiter = RateLimiter()
        assert limiter.redis is mock_get_redis

    def test_increment_key_new(self, limiter, mock_get_redis):
        mock_get_redis.get.return_value = None
        
        count = limiter._increment_key("test:key", expiration=60)
        
        assert count == 1
        mock_get_redis.setex.assert_called_once_with("test:key", 60, 1)

    def test_increment_key_existing(self, limiter, mock_get_redis):
        mock_get_redis.incr.return_value = 6
        
        count = limiter._increment_key("test:key", expiration=60)
        
        assert count == 6
        mock_get_redis.incr.assert_called_once_with("test:key")

    def test_is_within_limit_under(self, limiter):
        assert limiter._is_within_limit(count=3, limit=5) is True

    def test_is_within_limit_equal(self, limiter):
        assert limiter._is_within_limit(count=5, limit=5) is True

    def test_is_within_limit_over(self, limiter):
        assert limiter._is_within_limit(count=6, limit=5) is False

    def test_is_within_limit_zero(self, limiter):
        assert limiter._is_within_limit(count=1, limit=0) is False

    def test_is_within_limit_negative(self, limiter):
        assert limiter._is_within_limit(count=-1, limit=5) is True

    def test_is_within_rate_limit_under(self, limiter):
        """Test rate limit when under limit"""
        with patch.object(RateLimiter, '_increment_key', return_value=1):
            assert limiter._is_within_rate_limit("test-token", rate_limit=2) is True

    def test_is_within_rate_limit_over(self, limiter):
        """Test rate limit when over limit"""
        with patch.object(RateLimiter, '_increment_key', return_value=3):
            assert limiter._is_within_rate_limit("test-token", rate_limit=2) is False

    def test_is_within_rate_limit_at_limit(self, limiter):
        """Test rate limit when at limit"""
        with patch.object(RateLimiter, '_increment_key', return_value=2):
            assert limiter._is_within_rate_limit("test-token", rate_limit=2) is True

    def test_is_within_daily_limit_under(self, limiter):
        """Test daily limit when under limit"""
        with patch.object(RateLimiter, '_increment_key', return_value=10):
            assert limiter._is_within_daily_limit("test-token", daily_limit=50) is True

    def test_is_within_daily_limit_over(self, limiter):
        """Test daily limit when over limit"""
        with patch.object(RateLimiter, '_increment_key', return_value=51):
            assert limiter._is_within_daily_limit("test-token", daily_limit=50) is False

    def test_is_within_daily_limit_at_limit(self, limiter):
        """Test daily limit when at limit"""
        with patch.object(RateLimiter, '_increment_key', return_value=50):
            assert limiter._is_within_daily_limit("test-token", daily_limit=50) is True

    def test_is_allowed_rate_limit_pass(self, limiter):
        """Test when rate limit passes without daily limit"""
        with patch.object(RateLimiter, '_is_within_rate_limit', return_value=True):
            assert limiter.is_allowed("test-token", rate_limit=2) is True

    def test_is_allowed_rate_limit_fail(self, limiter):
        """Test when rate limit fails"""
        with patch.object(RateLimiter, '_is_within_rate_limit', return_value=False):
            assert limiter.is_allowed("test-token", rate_limit=2) is False

    def test_is_allowed_both_limits_pass(self, limiter):
        """Test when both rate and daily limits pass"""
        with patch.object(RateLimiter, '_is_within_rate_limit', return_value=True), \
             patch.object(RateLimiter, '_is_within_daily_limit', return_value=True):
            assert limiter.is_allowed("test-token", rate_limit=2, daily_limit=50) is True

    def test_is_allowed_daily_limit_fail(self, limiter):
        """Test when daily limit fails"""
        with patch.object(RateLimiter, '_is_within_rate_limit', return_value=True), \
             patch.object(RateLimiter, '_is_within_daily_limit', return_value=False):
            assert limiter.is_allowed("test-token", rate_limit=2, daily_limit=50) is False

    def test_is_allowed_invalid_token(self, limiter):
        """Test with invalid token"""
        with pytest.raises(ValueError, match="Token must be a non-empty string"):
            limiter.is_allowed("", rate_limit=2)
        with pytest.raises(ValueError, match="Token must be a non-empty string"):
            limiter.is_allowed(None, rate_limit=2)
        with pytest.raises(ValueError, match="Token must be a non-empty string"):
            limiter.is_allowed(123, rate_limit=2)

    def test_is_allowed_invalid_rate_limit(self, limiter):
        """Test with invalid rate limit"""
        with pytest.raises(ValueError, match="Rate limit must be a positive integer"):
            limiter.is_allowed("test-token", rate_limit=0)
        with pytest.raises(ValueError, match="Rate limit must be a positive integer"):
            limiter.is_allowed("test-token", rate_limit=-1)
        with pytest.raises(ValueError, match="Rate limit must be a positive integer"):
            limiter.is_allowed("test-token", rate_limit="2")

    def test_is_allowed_invalid_daily_limit(self, limiter):
        """Test with invalid daily limit"""
        with pytest.raises(ValueError, match="Daily limit must be a positive integer"):
            limiter.is_allowed("test-token", rate_limit=2, daily_limit=0)
        with pytest.raises(ValueError, match="Daily limit must be a positive integer"):
            limiter.is_allowed("test-token", rate_limit=2, daily_limit=-1)
        with pytest.raises(ValueError, match="Daily limit must be a positive integer"):
            limiter.is_allowed("test-token", rate_limit=2, daily_limit="50")

    def test_validate_inputs_valid(self, limiter):
        """Test validation with valid inputs"""
        # Should not raise any exceptions
        limiter._validate_inputs("test-token", rate_limit=5, daily_limit=10)
        limiter._validate_inputs("test-token", rate_limit=5, daily_limit=None)

    def test_validate_inputs_invalid_token(self, limiter):
        """Test validation with invalid token"""
        with pytest.raises(ValueError, match="Token must be a non-empty string"):
            limiter._validate_inputs("", rate_limit=5)
        with pytest.raises(ValueError, match="Token must be a non-empty string"):
            limiter._validate_inputs(None, rate_limit=5)
        with pytest.raises(ValueError, match="Token must be a non-empty string"):
            limiter._validate_inputs(123, rate_limit=5)

    def test_validate_inputs_invalid_rate_limit(self, limiter):
        """Test validation with invalid rate limit"""
        with pytest.raises(ValueError, match="Rate limit must be a positive integer"):
            limiter._validate_inputs("test-token", rate_limit=0)
        with pytest.raises(ValueError, match="Rate limit must be a positive integer"):
            limiter._validate_inputs("test-token", rate_limit=-1)
        with pytest.raises(ValueError, match="Rate limit must be a positive integer"):
            limiter._validate_inputs("test-token", rate_limit="5")

    def test_validate_inputs_invalid_daily_limit(self, limiter):
        """Test validation with invalid daily limit"""
        with pytest.raises(ValueError, match="Daily limit must be a positive integer"):
            limiter._validate_inputs("test-token", rate_limit=5, daily_limit=0)
        with pytest.raises(ValueError, match="Daily limit must be a positive integer"):
            limiter._validate_inputs("test-token", rate_limit=5, daily_limit=-1)
        with pytest.raises(ValueError, match="Daily limit must be a positive integer"):
            limiter._validate_inputs("test-token", rate_limit=5, daily_limit="10")