import time
from datetime import datetime, timezone
from redis_connection import get_redis

class RateLimiter:
    def __init__(self):
        self.redis = get_redis()

    @staticmethod
    def _get_current_timestamp() -> int:
        """Get the current Unix timestamp as an integer."""
        return int(time.time())

    @staticmethod
    def _get_start_of_day_timestamp() -> int:
        """Get the Unix timestamp for the start of the current day (UTC)."""
        return int(datetime.now(timezone.utc)
                  .replace(hour=0, minute=0, second=0, microsecond=0)
                  .timestamp())

    def _increment_key(self, key: str, expiration: int) -> int:
        if self.redis.get(key) is None:
            self.redis.setex(key, expiration, 1)
            return 1
        return self.redis.incr(key)

    def _is_within_limit(self, key: str, limit: int, expiration: int) -> bool:
        count = self._increment_key(key, expiration)
        return count <= limit

    def _check_rate_limit(self, token: str, rate_limit: int) -> bool:
        """Check if the request is within the per-second rate limit."""
        now = self._get_current_timestamp()
        rate_key = f"rate:{token}:{now}"
        return self._is_within_limit(rate_key, rate_limit, expiration=1)

    def _check_daily_limit(self, token: str, daily_limit: int) -> bool:
        """Check if the request is within the daily limit."""
        day_start = self._get_start_of_day_timestamp()
        daily_key = f"daily:{token}:{day_start}"
        return self._is_within_limit(daily_key, daily_limit, expiration=86400)

    def is_allowed(self, token: str, rate_limit: int, daily_limit: int = None) -> bool:
        if not self._check_rate_limit(token, rate_limit):
            return False
            
        if daily_limit is not None and not self._check_daily_limit(token, daily_limit):
            return False
            
        return True


