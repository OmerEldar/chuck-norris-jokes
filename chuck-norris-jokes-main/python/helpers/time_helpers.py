import time
from datetime import datetime, timezone

def get_current_timestamp() -> int:
    """Get the current Unix timestamp as an integer."""
    return int(time.time())

def get_start_of_day_timestamp() -> int:
    """Get the Unix timestamp for the start of the current day (UTC)."""
    return int(datetime.now(timezone.utc)
              .replace(hour=0, minute=0, second=0, microsecond=0)
              .timestamp()) 