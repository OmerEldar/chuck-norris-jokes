import time
from redis import Redis
from datetime import datetime, timezone
from typing import Optional
from redis_connection import RedisConnection

class RateLimiter:
    def __init__(self, redis_connection: Optional[RedisConnection] = None):
        """Initialize RateLimiter with Redis connection"""
        self.redis = redis_connection.get_client() if redis_connection else RedisConnection().get_client()
    
    def is_allowed(self, token: str, rate_limit: int, daily_limit: int = None) -> bool:
        now = time.time()
        day_start = int(datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
        
        # Check rate limit (requests per second)
        rate_key = f"rate:{token}:{int(now)}"
        current_rate = self.redis.get(rate_key)
        
        if current_rate is None:
            self.redis.setex(rate_key, 1, 1)
        elif int(current_rate) >= rate_limit:
            return False
        else:
            self.redis.incr(rate_key)
            
        # Check daily limit if applicable
        if daily_limit is not None:
            daily_key = f"daily:{token}:{day_start}"
            current_daily = self.redis.get(daily_key)
            
            if current_daily is None:
                self.redis.setex(daily_key, 86400, 1)
            elif int(current_daily) >= daily_limit:
                return False
            else:
                self.redis.incr(daily_key)
                
        return True     




#     import time
# from redis import Redis
# from datetime import datetime, timezone


# class RateLimiter:
#     def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
#         """
#         Initialize the RateLimiter with a Redis connection.
#         """
#         self.redis = Redis(host=redis_host, port=redis_port, db=redis_db)

#     @staticmethod
#     def _get_current_timestamp() -> int:
#         """
#         Get the current Unix timestamp as an integer.
#         """
#         return int(time.time())

#     @staticmethod
#     def _get_start_of_day_timestamp() -> int:
#         """
#         Get the Unix timestamp for the start of the current day (UTC).
#         """
#         return int(datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())

#     def _increment_key(self, key: str, expiration: int) -> int:
#         """
#         Increment a Redis key, setting its expiration if it does not exist.
#         Returns the current value of the key after incrementing.
#         """
#         if self.redis.get(key) is None:
#             self.redis.setex(key, expiration, 1)
#             return 1
#         return self.redis.incr(key)

#     def _is_within_limit(self, key: str, limit: int, expiration: int) -> bool:
#         """
#         Check if a Redis key is within its limit and update its count.
#         """
#         count = self._increment_key(key, expiration)
#         return count <= limit

#     def is_allowed(self, token: str, rate_limit: int, daily_limit: int = None) -> bool:
#         """
#         Check if a request is allowed based on rate and daily limits.

#         :param token: Unique identifier for the user or client.
#         :param rate_limit: Maximum number of requests per second.
#         :param daily_limit: Maximum number of requests per day (optional).
#         :return: True if the request is allowed, False otherwise.
#         """
#         now = self._get_current_timestamp()
#         day_start = self._get_start_of_day_timestamp()

#         # Check rate limit
#         rate_key = f"rate:{token}:{now}"
#         if not self._is_within_limit(rate_key, rate_limit, expiration=1):
#             return False

#         # Check daily limit, if applicable
#         if daily_limit is not None:
#             daily_key = f"daily:{token}:{day_start}"
#             if not self._is_within_limit(daily_key, daily_limit, expiration=86400):
#                 return False

#         return True
