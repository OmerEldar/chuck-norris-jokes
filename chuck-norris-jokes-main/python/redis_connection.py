from redis import Redis
import logging

logger = logging.getLogger(__name__)

# Module-level singleton
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
            _redis_client = Redis(host='localhost', port=6379, db=0)
            _redis_client.ping()  # Verify connection
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    return _redis_client