from unittest import TestCase
from unittest.mock import patch, call

class TestRateLimiter(TestCase):
    @patch('rate_limiter.get_current_timestamp')
    def test_rate_limit_exceeded(self, mock_time, limiter, mock_get_redis):
        """Should block when rate limit exceeded"""
        timestamp = 1000
        mock_time.return_value = timestamp
        mock_get_redis.get.return_value = "1"
        mock_get_redis.incr.return_value = 2
        
        result = limiter.is_allowed("test-token", rate_limit=1, daily_limit=50)
        
        assert result is False
        assert mock_get_redis.get.call_args_list[0] == call(f"rate:test-token:{timestamp}")

    @patch('rate_limiter.get_start_of_day_timestamp')
    @patch('rate_limiter.get_current_timestamp')
    def test_daily_limit_exceeded(self, mock_time, mock_day_start, limiter, mock_get_redis):
        """Should block when daily limit exceeded"""
        current = 1000
        day_start = 900
        mock_time.return_value = current
        mock_day_start.return_value = day_start
        
        # Configure mock responses
        def get_side_effect(key):
            if key == f"rate:test-token:{current}":
                return None
            if key == f"daily:test-token:{day_start}":
                return "5"
            return None
            
        mock_get_redis.get.side_effect = get_side_effect
        mock_get_redis.incr.return_value = 6
        
        result = limiter.is_allowed("test-token", rate_limit=1, daily_limit=5)
        
        assert result is False
        # Verify calls with actual timestamps
        calls = [call(f"rate:test-token:{current}"), call(f"daily:test-token:{day_start}")]
        mock_get_redis.get.assert_has_calls(calls, any_order=True) 