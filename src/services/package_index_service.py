"""In-memory package index — pre-fetched at startup, re-indexed periodically.

User requests never hit external APIs. All search/filter/sort/pagination
is done against the in-memory list in microseconds.
"""

import asyncio

from config import settings
from src.core.logger import get_logger
from src.data.sources.clickhouse_source import ClickHouseSource
from src.data.sources.package_discovery import PackageDiscovery
from src.data.sources.pypi_source import PyPISource
from src.domain.entities.package import Package, PackageType
from src.services.cache_service import CacheService

logger = get_logger(__name__)


class PackageIndexService:
    """Pre-built in-memory index of all Flet packages.

    - build_index() fetches everything from GitHub + PyPI + ClickHouse once.
    - query() filters/sorts/paginates the in-memory list (zero HTTP).
    - Re-indexes every INDEX_REINDEX_INTERVAL seconds in background.
    """

    def __init__(
        self,
        discovery: PackageDiscovery,
        pypi: PyPISource,
        clickhouse: ClickHouseSource,
        cache: CacheService,
    ):
        self._discovery = discovery
        self._pypi = pypi
        self._ch = clickhouse
        self._cache = cache
        self._packages: list[Package] = []
        self._official_names: set[str] = set()
        self._ready = asyncio.Event()
        self._reindex_task: asyncio.Task | None = None

    @property
    def is_ready(self) -> bool:
        return self._ready.is_set()

    async def wait_until_ready(self) -> None:
        await self._ready.wait()

    # --- Index building ---

    async def build_index(self) -> None:
        """Fetch all packages and build the in-memory index."""
        logger.info("Building package index...")
        try:
            # Fetch community + official in parallel
            community_task = self._discovery.fetch_all_github_packages(pypi_only=False)
            official_task = self._discovery.fetch_official_packages()
            flet_stars_task = self._get_flet_stars()

            community, official, flet_stars = await asyncio.gather(
                community_task, official_task, flet_stars_task
            )

            # Merge: official packages override community duplicates
            pkg_map: dict[str, Package] = {}
            for pkg in community:
                key = pkg.pypi_name or pkg.name
                pkg_map[key] = pkg

            official_names: set[str] = set()
            for pkg in official:
                key = pkg.pypi_name or pkg.name
                official_names.add(key)
                if not pkg.stars:
                    pkg.stars = flet_stars
                pkg_map[key] = pkg

            all_packages = list(pkg_map.values())

            # Verify PyPI existence and enrich versions (parallel)
            await self._verify_pypi_and_enrich(all_packages)

            # Enrich with downloads (batch ClickHouse)
            await self._enrich_downloads(all_packages)

            # Sort by stars (default ranking)
            all_packages.sort(key=lambda p: p.stars, reverse=True)

            # Atomic swap
            self._packages = all_packages
            self._official_names = official_names
            self._ready.set()

            logger.info("Package index built: %d packages", len(all_packages))
        except Exception:
            logger.exception("Failed to build package index")
            if not self._ready.is_set() and not self._packages:
                # First build failed — keep waiting state
                pass

    async def _get_flet_stars(self) -> int:
        cached = self._cache.get("flet_repo_stars")
        if cached is not None:
            return cached
        try:
            gh = self._discovery._github
            repo = await gh.get_repository("flet-dev", "flet")
            stars = repo.get("stargazers_count", 0)
            self._cache.set("flet_repo_stars", stars, ttl=3600)
            return stars
        except Exception:
            return 0

    async def _enrich_downloads(self, packages: list[Package]) -> None:
        """Enrich packages with download counts.

        Uses ClickHouse batch query (same BigQuery source as pepy.tech, fast, no rate limit).
        """
        pypi_pkgs = [p for p in packages if p.pypi_name]
        names = [p.pypi_name for p in pypi_pkgs]
        result: dict[str, int] = {}
        uncached: list[str] = []

        for name in names:
            cached = self._cache.get(f"dl:{name}")
            if cached is not None:
                result[name] = cached
            else:
                uncached.append(name)

        if uncached:
            try:
                ch_data = await self._ch.get_downloads_batch(uncached, days=30)
                for name in uncached:
                    downloads = ch_data.get(name, 0)
                    result[name] = downloads
                    self._cache.set(f"dl:{name}", downloads, ttl=settings.CACHE_TTL_DOWNLOADS)
            except Exception:
                logger.info("ClickHouse unavailable for index enrichment")

        for pkg in pypi_pkgs:
            pkg.downloads = result.get(pkg.pypi_name, pkg.downloads)

    async def _verify_pypi_and_enrich(self, packages: list[Package]) -> None:
        """Verify PyPI existence for each package. Fill version if found.

        Packages not on PyPI get pypi_name cleared so the pypi_only
        filter in query() can exclude them correctly.
        """

        async def _check(pkg: Package) -> None:
            # Official packages are always on PyPI (fetched via fetch_pypi_package)
            if pkg.is_official and pkg.version:
                return
            name = pkg.pypi_name or pkg.name
            try:
                data = await self._pypi.get_package_info(name)
                version = data.get("info", {}).get("version", "")
                if not pkg.version and version:
                    pkg.version = version
                # Confirmed on PyPI — ensure pypi_name is set
                if not pkg.pypi_name:
                    pkg.pypi_name = name
            except Exception:
                # Not on PyPI — clear pypi_name so pypi_only filter works
                pkg.pypi_name = ""

        await asyncio.gather(*[_check(p) for p in packages])

    # --- Lifecycle ---

    async def start(self) -> None:
        """Build index and start background re-indexing loop."""
        await self.build_index()
        interval = settings.get("INDEX_REINDEX_INTERVAL", 3600)
        self._reindex_task = asyncio.create_task(self._reindex_loop(interval))

    async def stop(self) -> None:
        if self._reindex_task and not self._reindex_task.done():
            self._reindex_task.cancel()
            try:
                await self._reindex_task
            except asyncio.CancelledError:
                pass

    async def _reindex_loop(self, interval: int) -> None:
        while True:
            await asyncio.sleep(interval)
            logger.info("Re-indexing packages...")
            try:
                await self.build_index()
            except Exception:
                logger.exception("Re-index failed")

    # --- Query (synchronous, zero HTTP) ---

    def query(
        self,
        text: str = "",
        sort: str = "default ranking",
        package_type: str | None = None,
        official_only: bool = False,
        pypi_only: bool = True,
        page: int = 1,
        per_page: int = 10,
    ) -> tuple[list[Package], int]:
        """Filter, sort, and paginate the in-memory index."""
        result = self._packages

        # Filter: pypi_only
        if pypi_only:
            result = [p for p in result if p.pypi_name]

        # Filter: official only
        if official_only:
            result = [p for p in result if p.is_official]

        # Filter: package type
        if package_type == "Services":
            result = [p for p in result if p.package_type == PackageType.SERVICE]
        elif package_type == "UI Controls":
            result = [p for p in result if p.package_type == PackageType.UI_CONTROL]
        elif package_type == "Python Package":
            result = [p for p in result if p.package_type == PackageType.PYTHON_PACKAGE]

        # Filter: text search
        if text:
            text_lower = text.lower()
            result = [
                p
                for p in result
                if text_lower in p.name.lower()
                or text_lower in (p.pypi_name or "").lower()
                or text_lower in (p.description or "").lower()
                or any(text_lower in t.lower() for t in p.topics)
            ]

        # Sort
        if sort == "most downloads":
            result = sorted(result, key=lambda p: p.downloads, reverse=True)
        elif sort == "most stars":
            result = sorted(result, key=lambda p: p.stars, reverse=True)
        elif sort == "trending":
            result = sorted(result, key=lambda p: p.stars + p.downloads, reverse=True)
        elif sort == "recently updated":
            result = sorted(result, key=lambda p: p.updated_at or "", reverse=True)
        elif sort == "newest package":
            result = sorted(result, key=lambda p: p.created_at or "", reverse=True)
        # "default ranking" keeps the original order (by stars)

        total = len(result)
        start = (page - 1) * per_page
        end = start + per_page
        return result[start:end], total
