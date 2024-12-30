from datetime import datetime, timedelta
import json
import logging
from typing import Dict, Any
from dataclasses import dataclass
from .file_helper import FileHelper

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class CacheEntry:
    data: Dict[str, Any]
    timestamp: datetime

class CachedAccountsFileHelper:
    def __init__(self, refresh_interval: int = 300):
        self._refresh_interval = refresh_interval
        self._cache: Dict[str, CacheEntry] = {}
        self._file_helper = FileHelper()

    def read_json_file(self, file_path: str) -> Dict[str, Any]:
        """Read file with caching and automatic refresh"""
        current_time = datetime.now()
        cache_entry = self._cache.get(file_path)
        
        should_refresh = (
            cache_entry is None or
            current_time - cache_entry.timestamp > timedelta(seconds=self._refresh_interval)
        )
        
        if should_refresh:
            try:
                new_data = self._file_helper.read_json_file(file_path)
                
                # It is not fully imutable.
                self._cache[file_path] = CacheEntry(
                    data=new_data,
                    timestamp=current_time
                )
                logger.info(f"Refreshed cache for {file_path}")
                
            except Exception as e:
                logger.error(f"Error refreshing cache for {file_path}: {e}")
                if cache_entry:
                    logger.warning(f"Using cached data for {file_path}")
                    return cache_entry.data
                raise

        return self._cache[file_path].data