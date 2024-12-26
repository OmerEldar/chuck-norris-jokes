import time
from redis import Redis
from datetime import datetime, timezone

class RateLimiter:
    def __init__(self):
        self.redis = Redis(host='localhost', port=6379, db=0)
    
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
                self.redis.setex(daily_key, 86400, 1)  # 24 hours in seconds
            elif int(current_daily) >= daily_limit:
                return False
            else:
                self.redis.incr(daily_key)
                
        return True 