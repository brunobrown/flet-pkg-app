"""Tests for CacheService LRU eviction and TTL behavior."""

import time

from src.services.cache_service import CacheService


class TestLRUEviction:
    def test_evicts_lru_when_full(self) -> None:
        cache = CacheService(ttl=60, max_entries=3)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        # Cache full — next set evicts least recently used ("a")
        cache.set("d", 4)
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("d") == 4

    def test_get_moves_to_end(self) -> None:
        cache = CacheService(ttl=60, max_entries=3)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        # Access "a" — moves it to end (most recently used)
        cache.get("a")
        # Now "b" is LRU
        cache.set("d", 4)
        assert cache.get("a") == 1  # Still here (was accessed)
        assert cache.get("b") is None  # Evicted (was LRU)

    def test_update_existing_key_no_extra_eviction(self) -> None:
        cache = CacheService(ttl=60, max_entries=3)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        # Update existing key — should not evict anyone
        cache.set("a", 10)
        assert cache.get("a") == 10
        assert cache.get("b") == 2
        assert cache.get("c") == 3

    def test_max_entries_respected(self) -> None:
        cache = CacheService(ttl=60, max_entries=2)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        cache.set("d", 4)
        # Only 2 entries should remain
        count = sum(1 for k in ["a", "b", "c", "d"] if cache.get(k) is not None)
        assert count == 2


class TestTTLExpiration:
    def test_expired_entry_returns_none(self) -> None:
        cache = CacheService(ttl=1, max_entries=100)
        cache.set("key", "value", ttl=0)
        # TTL=0 means already expired on next read
        time.sleep(0.01)
        assert cache.get("key") is None

    def test_custom_ttl_per_key(self) -> None:
        cache = CacheService(ttl=60, max_entries=100)
        cache.set("short", "value", ttl=0)
        cache.set("long", "value", ttl=3600)
        time.sleep(0.01)
        assert cache.get("short") is None
        assert cache.get("long") == "value"
