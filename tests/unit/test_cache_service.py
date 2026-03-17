from src.services.cache_service import CacheService


class TestCacheService:
    def test_set_and_get(self) -> None:
        cache = CacheService(ttl=60)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_missing_key(self) -> None:
        cache = CacheService(ttl=60)
        assert cache.get("nonexistent") is None

    def test_invalidate(self) -> None:
        cache = CacheService(ttl=60)
        cache.set("key1", "value1")
        cache.invalidate("key1")
        assert cache.get("key1") is None

    def test_clear(self) -> None:
        cache = CacheService(ttl=60)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None
