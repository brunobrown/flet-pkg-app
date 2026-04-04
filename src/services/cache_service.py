import asyncio
import time
from collections import OrderedDict
from typing import Any

from config import settings
from src.core.logger import get_logger

logger = get_logger(__name__)


class CacheService:
    """In-memory cache with TTL expiration and LRU eviction.

    Entries expire after `ttl` seconds. When `max_entries` is reached,
    the least recently used entry is evicted on write.

    Write operations are protected by an asyncio.Lock to prevent
    interleaving during concurrent async tasks (e.g., index enrichment).
    """

    def __init__(
        self,
        ttl: int = settings.CACHE_TTL_SECONDS,
        max_entries: int = settings.get("CACHE_MAX_ENTRIES", 10000),
    ):
        self._default_ttl = ttl
        self._max_entries = max_entries
        self._store: OrderedDict[str, tuple[Any, float, int]] = OrderedDict()
        self._lock = asyncio.Lock()

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, timestamp, ttl = entry
        if time.time() - timestamp > ttl:
            del self._store[key]
            return None
        # Move to end (most recently used)
        self._store.move_to_end(key)
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        # If key exists, remove first to avoid unnecessary eviction
        if key in self._store:
            del self._store[key]
        # Evict LRU entries if at capacity
        while len(self._store) >= self._max_entries:
            self._store.popitem(last=False)
        self._store[key] = (value, time.time(), ttl if ttl is not None else self._default_ttl)

    async def async_set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Thread-safe set for use in concurrent async contexts (e.g., asyncio.gather)."""
        async with self._lock:
            self.set(key, value, ttl)

    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()
