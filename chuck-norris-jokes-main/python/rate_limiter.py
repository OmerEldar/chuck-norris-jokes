from helpers.time_helpers import get_current_timestamp, get_start_of_day_timestamp
from redis_connection import get_redis

SECONDS_IN_DAY = 86400

class RateLimiter:
    def __init__(self):
        # *******************************************************
        # The system will crach if redis connection is lost.
        # Connection recovery is not implemented.
        # *******************************************************
        self.redis = get_redis()

    def _increment_key(self, key: str, expiration: int) -> int:
        if self.redis.get(key) is None:
            self.redis.setex(key, expiration, 1)
            return 1
        return self.redis.incr(key)

    def _is_within_limit(self, count: int, limit: int) -> bool:
        return count <= limit

    def _is_within_rate_limit(self, token: str, rate_limit: int) -> bool:
        rate_limit_key = f"rate:{token}:{get_current_timestamp()}"
        count = self._increment_key(rate_limit_key, expiration=1)
        return self._is_within_limit(count, rate_limit)

    def _is_within_daily_limit(self, token: str, daily_limit: int) -> bool:
        daily_limit_key = f"daily:{token}:{get_start_of_day_timestamp()}"
        count = self._increment_key(daily_limit_key, expiration=SECONDS_IN_DAY)
        return self._is_within_limit(count, daily_limit)

    # ****************************************************************************************************
    # Performing input validations under controlled environment can introduce unnecessary overhead.
    # Note: the only user jenerated content is the token but we already filtering it in the Auth middleware.
    # ********************************************************
    # def _validate_inputs(self, token: str, rate_limit: int, daily_limit: int = None) -> None:
    #     if not token or not isinstance(token, str):
    #         raise ValueError("Token must be a non-empty string")
            
    #     if not isinstance(rate_limit, int) or rate_limit <= 0:
    #         raise ValueError("Rate limit must be a positive integer")
            
    #     if daily_limit is not None and (not isinstance(daily_limit, int) or daily_limit <= 0):
    #         raise ValueError("Daily limit must be a positive integer")

    def is_allowed(self, token: str, rate_limit: int, daily_limit: int = None) -> bool:

        if not self._is_within_rate_limit(token, rate_limit):
            return False
            
        if daily_limit is not None and not self._is_within_daily_limit(token, daily_limit):
            return False
            
        return True


