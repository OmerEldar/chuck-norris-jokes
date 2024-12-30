import os
from redis import Redis, ConnectionError
import logging

# Set up logging
logger = logging.getLogger(__name__)

_redis_client = None

# !!!!!! This is a simple solution for now !!!!!
# Robust solution can be achieved using:
#  connection pool 
#  connection recovery
# Handling only CREATE connection (ignoring all the rests like CLOSE, DISCONNECT, etc.)

def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),  # Use environment variable
                port=int(os.getenv('REDIS_PORT', 6379)),    # Use environment variable
                db=0
            )
            _redis_client.ping()  # Verify connection
            logger.info("Successfully connected to Redis")
        except ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    return _redis_client