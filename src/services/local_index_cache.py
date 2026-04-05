"""Persistent local cache for the package index — stale-while-revalidate pattern.

Serializes the in-memory package list to a JSON file on disk.
On startup, loads cached data instantly (if fresh enough), then re-indexes in background.
Works on both web (server) and mobile (app storage).
"""

import json
import time
from dataclasses import asdict
from pathlib import Path

from config import settings
from src.core.logger import get_logger
from src.domain.entities.package import Package, PackageType

logger = get_logger(__name__)

# Default cache TTL: 6 hours
_DEFAULT_TTL = settings.get("LOCAL_INDEX_CACHE_TTL", 21600)


def _get_cache_path() -> Path:
    """Return platform-appropriate cache directory."""
    cache_dir = Path(settings.get("LOCAL_INDEX_CACHE_DIR", ".cache"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "package_index.json"


def _package_to_dict(pkg: Package) -> dict:
    """Serialize Package to dict, converting enums to strings."""
    d = asdict(pkg)
    d["package_type"] = pkg.package_type.value
    # Exclude heavy fields not needed for index (loaded on detail page)
    d.pop("readme", None)
    d.pop("changelog", None)
    d.pop("dependencies", None)
    return d


def _dict_to_package(d: dict) -> Package:
    """Deserialize dict to Package, restoring enums."""
    d.pop("readme", None)
    d.pop("changelog", None)
    d.pop("dependencies", None)
    pt = d.pop("package_type", "Python Package")
    try:
        package_type = PackageType(pt)
    except ValueError:
        package_type = PackageType.PYTHON_PACKAGE
    return Package(**d, package_type=package_type)


class LocalIndexCache:
    """Persistent JSON cache for the package index.

    Usage:
        cache = LocalIndexCache()
        packages = cache.load()      # Returns list or None if stale/missing
        cache.save(packages)         # Persists after successful index build
        cache.is_fresh()             # True if cache exists and TTL not expired
    """

    def __init__(self, ttl: int = _DEFAULT_TTL):
        self._ttl = ttl
        self._path = _get_cache_path()

    def is_fresh(self) -> bool:
        """Check if cached index exists and is within TTL."""
        if not self._path.exists():
            return False
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            saved_at = data.get("saved_at", 0)
            return (time.time() - saved_at) < self._ttl
        except (json.JSONDecodeError, OSError):
            return False

    def load(self) -> list[Package] | None:
        """Load cached packages from disk. Returns None if missing or corrupt."""
        if not self._path.exists():
            return None
        try:
            raw = self._path.read_text(encoding="utf-8")
            data = json.loads(raw)
            packages = [_dict_to_package(d) for d in data.get("packages", [])]
            saved_at = data.get("saved_at", 0)
            age_min = int((time.time() - saved_at) / 60)
            logger.info("Loaded %d packages from local cache (%d min old)", len(packages), age_min)
            return packages
        except (json.JSONDecodeError, OSError, TypeError, KeyError) as e:
            logger.warning("Failed to load local index cache: %s", e)
            return None

    def save(self, packages: list[Package]) -> None:
        """Persist package list to disk as JSON."""
        try:
            data = {
                "saved_at": time.time(),
                "count": len(packages),
                "packages": [_package_to_dict(p) for p in packages],
            }
            self._path.write_text(
                json.dumps(data, ensure_ascii=False, separators=(",", ":")),
                encoding="utf-8",
            )
            logger.info("Saved %d packages to local cache", len(packages))
        except OSError as e:
            logger.warning("Failed to save local index cache: %s", e)
