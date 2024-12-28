from redis import Redis
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class RedisConnectionError(Exception):
    """Custom exception for Redis connection errors"""
    pass

class RedisConnection:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """Initialize Redis connection"""
        try:
            self.client = Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True
            )
            # Verify connection
            self.client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise RedisConnectionError(f"Could not connect to Redis: {e}")

    def get_client(self) -> Redis:
        """Get Redis client"""
        return self.client 