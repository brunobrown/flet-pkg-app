import time
from typing import Any

from config import settings
from src.core.logger import get_logger

logger = get_logger(__name__)


class CacheService:
    def __init__(self, ttl: int = settings.CACHE_TTL_SECONDS):
        self._default_ttl = ttl
        self._store: dict[str, tuple[Any, float, int]] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, timestamp, ttl = entry
        if time.time() - timestamp > ttl:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        self._store[key] = (value, time.time(), ttl if ttl is not None else self._default_ttl)

    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()
