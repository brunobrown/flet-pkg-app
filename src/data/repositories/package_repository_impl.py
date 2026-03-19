import asyncio

from src.core.constants import (
    CACHE_TTL_DOWNLOADS,
    EXCLUDED_PACKAGES,
    KNOWN_SERVICE_EXTENSIONS,
    KNOWN_UI_CONTROL_EXTENSIONS,
    OFFICIAL_EXTENSION_PACKAGES,
)
from src.core.logger import get_logger
from src.data.models.mappers import github_repo_to_package, pypi_info_to_package
from src.data.sources.clickhouse_source import ClickHouseSource
from src.data.sources.github_source import GitHubSource
from src.data.sources.pypi_source import PyPISource
from src.domain.entities.package import Package, PackageType
from src.domain.repositories.package_repository import PackageRepository
from src.services.cache_service import CacheService

logger = get_logger(__name__)


def _classify_package(pkg: Package) -> None:
    """Classify a package as Service, UI Control, or Python Package."""
    name_lower = pkg.pypi_name.lower() if pkg.pypi_name else pkg.name.lower()

    if name_lower in KNOWN_SERVICE_EXTENSIONS:
        pkg.package_type = PackageType.SERVICE
    elif name_lower in KNOWN_UI_CONTROL_EXTENSIONS:
        pkg.package_type = PackageType.UI_CONTROL

    topics_lower = [t.lower() for t in pkg.topics]
    if pkg.package_type == PackageType.PYTHON_PACKAGE:
        if "service" in topics_lower or "services" in topics_lower:
            pkg.package_type = PackageType.SERVICE
        elif (
            "ui" in topics_lower
            or "ui-control" in topics_lower
            or "control" in topics_lower
            or "widget" in topics_lower
        ):
            pkg.package_type = PackageType.UI_CONTROL


def _is_excluded(pkg: Package) -> bool:
    name_lower = pkg.pypi_name.lower() if pkg.pypi_name else pkg.name.lower()
    return name_lower in EXCLUDED_PACKAGES


def _filter_excluded(packages: list[Package]) -> list[Package]:
    return [p for p in packages if not _is_excluded(p)]


class PackageRepositoryImpl(PackageRepository):
    def __init__(
        self,
        github_source: GitHubSource,
        pypi_source: PyPISource,
        clickhouse_source: ClickHouseSource,
        cache: CacheService,
    ):
        self._github = github_source
        self._pypi = pypi_source
        self._ch = clickhouse_source
        self._cache = cache

    # --- Downloads: ClickHouse batch with 24h cache ---

    async def _get_downloads_batch(self, names: list[str]) -> dict[str, int]:
        """Get downloads for multiple packages. ClickHouse first, pypistats fallback."""
        # Check cache first
        result: dict[str, int] = {}
        uncached: list[str] = []
        for name in names:
            cached = self._cache.get(f"dl:{name}")
            if cached is not None:
                result[name] = cached
            else:
                uncached.append(name)

        if not uncached:
            return result

        # Try ClickHouse batch (1 query for all)
        try:
            ch_data = await self._ch.get_downloads_batch(uncached, days=30)
            for name in uncached:
                downloads = ch_data.get(name, 0)
                result[name] = downloads
                self._cache.set(f"dl:{name}", downloads, ttl=CACHE_TTL_DOWNLOADS)
            return result
        except Exception:
            logger.info("ClickHouse unavailable, falling back to pypistats")

        # Fallback: pypistats (with semaphore + retry)
        for name in uncached:
            downloads = await self._pypi.get_recent_downloads(name)
            result[name] = downloads
            self._cache.set(f"dl:{name}", downloads, ttl=CACHE_TTL_DOWNLOADS)

        return result

    async def _get_downloads(self, name: str) -> int:
        batch = await self._get_downloads_batch([name])
        return batch.get(name, 0)

    # --- Enrich packages with downloads + version ---

    async def _enrich_with_downloads(self, packages: list[Package]) -> None:
        """Batch-enrich packages with download stats."""
        names = [p.pypi_name or p.name for p in packages]
        downloads = await self._get_downloads_batch(names)
        for pkg in packages:
            key = pkg.pypi_name or pkg.name
            pkg.downloads = downloads.get(key, 0)

    async def _enrich_with_pypi(self, packages: list[Package]) -> None:
        """Enrich with downloads (batch) + version (individual)."""
        await self._enrich_with_downloads(packages)

        async def _fill_version(pkg: Package) -> None:
            if not pkg.version:
                try:
                    pypi_data = await self._pypi.get_package_info(pkg.pypi_name)
                    info = pypi_data.get("info", {})
                    pkg.version = info.get("version", "")
                except Exception:
                    pass

        await asyncio.gather(*[_fill_version(p) for p in packages if not p.version])

    # --- Public methods ---

    async def search_packages(
        self,
        query: str,
        page: int = 1,
        per_page: int = 10,
        sort: str = "default ranking",
        package_type: str | None = None,
        official_only: bool = False,
    ) -> tuple[list[Package], int]:
        cache_key = f"search:{query}:{page}:{per_page}:{sort}:{package_type}:{official_only}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        gh_sort = "stars"
        if sort == "recently updated":
            gh_sort = "updated"
        elif sort == "newest package":
            gh_sort = "updated"

        search_q = f"{query} flet language:python" if query else "flet language:python"
        if official_only:
            search_q += " user:flet-dev"

        try:
            data = await self._github.search_repositories(
                query=search_q,
                sort=gh_sort,
                page=page,
                per_page=per_page + 5,
            )
            total = min(data.get("total_count", 0), 1000)
            items = data.get("items", [])

            packages = [github_repo_to_package(item) for item in items]
            for pkg in packages:
                _classify_package(pkg)
            packages = _filter_excluded(packages)

            if package_type == "Services":
                packages = [p for p in packages if p.package_type == PackageType.SERVICE]
            elif package_type == "UI Controls":
                packages = [p for p in packages if p.package_type == PackageType.UI_CONTROL]

            packages = packages[:per_page]
            await self._enrich_with_pypi(packages)

            if sort == "most downloads":
                packages.sort(key=lambda p: p.downloads, reverse=True)

            result = (packages, total)
            self._cache.set(cache_key, result)
            return result
        except Exception as e:
            logger.error("Search error: %s", e)
            return [], 0

    async def get_package_detail(self, owner: str, repo: str) -> Package:
        cache_key = f"detail:{owner}/{repo}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        repo_data, readme, changelog = await asyncio.gather(
            self._github.get_repository(owner, repo),
            self._github.get_readme(owner, repo),
            self._github.get_file_content(owner, repo, "CHANGELOG.md"),
        )

        pkg = github_repo_to_package(repo_data)
        _classify_package(pkg)
        pkg.readme = readme
        pkg.changelog = changelog

        try:
            pypi_data = await self._pypi.get_package_info(pkg.pypi_name)
            pypi_pkg = pypi_info_to_package(pypi_data)
            pkg.version = pypi_pkg.version
            pkg.dependencies = pypi_pkg.dependencies
            if not pkg.license:
                pkg.license = pypi_pkg.license
            if not pkg.documentation_url:
                pkg.documentation_url = pypi_pkg.documentation_url
            pkg.downloads = await self._get_downloads(pkg.pypi_name)
        except Exception:
            logger.info("No PyPI data for %s", pkg.pypi_name)

        self._cache.set(cache_key, pkg)
        return pkg

    async def get_package_by_name(self, package_name: str) -> Package:
        cache_key = f"detail_name:{package_name}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        pypi_data = await self._pypi.get_package_info(package_name)
        pkg = pypi_info_to_package(pypi_data)
        _classify_package(pkg)

        pkg.downloads = await self._get_downloads(package_name)

        if pkg.github_owner and pkg.github_repo:
            try:
                readme, changelog = await asyncio.gather(
                    self._github.get_readme(pkg.github_owner, pkg.github_repo),
                    self._github.get_file_content(
                        pkg.github_owner, pkg.github_repo, "CHANGELOG.md"
                    ),
                )
                pkg.readme = readme
                pkg.changelog = changelog

                repo_data = await self._github.get_repository(pkg.github_owner, pkg.github_repo)
                pkg.stars = repo_data.get("stargazers_count", 0)
                pkg.forks = repo_data.get("forks_count", 0)
                pkg.topics = repo_data.get("topics", [])
                if not pkg.issues_url:
                    full_name = repo_data.get("full_name", "")
                    pkg.issues_url = f"https://github.com/{full_name}/issues"
            except Exception:
                logger.info("No GitHub data for %s", package_name)
        else:
            pkg.github_owner = "flet-dev"
            pkg.github_repo = "flet"
            pkg.repository_url = (
                f"https://github.com/flet-dev/flet/tree/main/sdk/python/packages/{package_name}"
            )
            pkg.issues_url = "https://github.com/flet-dev/flet/issues"
            try:
                readme = await self._github.get_file_content(
                    "flet-dev", "flet", f"sdk/python/packages/{package_name}/README.md"
                )
                pkg.readme = readme
                repo_data = await self._github.get_repository("flet-dev", "flet")
                pkg.stars = repo_data.get("stargazers_count", 0)
                pkg.forks = repo_data.get("forks_count", 0)
            except Exception:
                pass

        if package_name in OFFICIAL_EXTENSION_PACKAGES:
            pkg.is_official = True
            pkg.publisher = "flet.dev"

        self._cache.set(cache_key, pkg)
        return pkg

    async def get_official_packages(self) -> list[Package]:
        cache_key = "official_packages"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            # Batch: fetch all PyPI info in parallel
            async def _fetch(name: str) -> Package | None:
                try:
                    pypi_data = await self._pypi.get_package_info(name)
                    pkg = pypi_info_to_package(pypi_data)
                    _classify_package(pkg)
                    pkg.is_official = True
                    pkg.publisher = "flet.dev"
                    if not pkg.github_owner:
                        pkg.github_owner = "flet-dev"
                        pkg.github_repo = "flet"
                        pkg.repository_url = (
                            f"https://github.com/flet-dev/flet/tree/main/sdk/python/packages/{name}"
                        )
                    return pkg
                except Exception:
                    logger.warning("Could not fetch official package: %s", name)
                    return None

            results = await asyncio.gather(*[_fetch(n) for n in OFFICIAL_EXTENSION_PACKAGES])
            packages = [p for p in results if p is not None]

            # Single batch query for all downloads
            await self._enrich_with_downloads(packages)

            packages.sort(key=lambda p: p.downloads, reverse=True)
            self._cache.set(cache_key, packages[:5])
            return packages[:5]
        except Exception as e:
            logger.error("Error fetching official packages: %s", e)
            return []

    async def get_trending_packages(self, limit: int = 6) -> list[Package]:
        cache_key = f"trending:{limit}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            data = await self._github.search_repositories(
                query="flet topic:flet language:python pushed:>2025-01-01",
                sort="stars",
                per_page=limit + 10,
            )
            items = data.get("items", [])
            packages = [github_repo_to_package(item) for item in items]
            for pkg in packages:
                _classify_package(pkg)
            packages = _filter_excluded(packages)
            await self._enrich_with_pypi(packages)
            packages = packages[:limit]
            self._cache.set(cache_key, packages)
            return packages
        except Exception as e:
            logger.error("Error fetching trending packages: %s", e)
            return []

    async def get_service_packages(self, limit: int = 6) -> list[Package]:
        cache_key = f"services:{limit}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            service_names = list(KNOWN_SERVICE_EXTENSIONS)

            async def _fetch(name: str) -> Package | None:
                try:
                    pypi_data = await self._pypi.get_package_info(name)
                    pkg = pypi_info_to_package(pypi_data)
                    pkg.package_type = PackageType.SERVICE
                    if name in set(OFFICIAL_EXTENSION_PACKAGES):
                        pkg.is_official = True
                        pkg.publisher = "flet.dev"
                    return pkg
                except Exception:
                    return None

            results = await asyncio.gather(*[_fetch(n) for n in service_names])
            packages = [p for p in results if p is not None]
            await self._enrich_with_downloads(packages)
            packages.sort(key=lambda p: p.downloads, reverse=True)

            self._cache.set(cache_key, packages[:limit])
            return packages[:limit]
        except Exception as e:
            logger.error("Error fetching service packages: %s", e)
            return []

    async def get_ui_control_packages(self, limit: int = 6) -> list[Package]:
        cache_key = f"ui_controls:{limit}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            ui_names = list(KNOWN_UI_CONTROL_EXTENSIONS)

            async def _fetch(name: str) -> Package | None:
                try:
                    pypi_data = await self._pypi.get_package_info(name)
                    pkg = pypi_info_to_package(pypi_data)
                    pkg.package_type = PackageType.UI_CONTROL
                    if name in set(OFFICIAL_EXTENSION_PACKAGES):
                        pkg.is_official = True
                        pkg.publisher = "flet.dev"
                    return pkg
                except Exception:
                    return None

            results = await asyncio.gather(*[_fetch(n) for n in ui_names])
            packages = [p for p in results if p is not None]
            await self._enrich_with_downloads(packages)
            packages.sort(key=lambda p: p.downloads, reverse=True)

            self._cache.set(cache_key, packages[:limit])
            return packages[:limit]
        except Exception as e:
            logger.error("Error fetching UI control packages: %s", e)
            return []

    async def get_python_packages(self, limit: int = 6) -> list[Package]:
        cache_key = f"python_packages:{limit}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            data = await self._github.search_repositories(
                query="topic:flet language:python NOT flet-dev",
                sort="stars",
                per_page=limit + 10,
            )
            items = data.get("items", [])
            packages = [github_repo_to_package(item) for item in items]
            packages = _filter_excluded(packages)

            all_extensions = KNOWN_SERVICE_EXTENSIONS | KNOWN_UI_CONTROL_EXTENSIONS
            packages = [
                p
                for p in packages
                if p.pypi_name.lower() not in all_extensions
                and p.name.lower() not in all_extensions
            ]

            for pkg in packages:
                pkg.package_type = PackageType.PYTHON_PACKAGE

            await self._enrich_with_pypi(packages)
            packages = packages[:limit]
            self._cache.set(cache_key, packages)
            return packages
        except Exception as e:
            logger.error("Error fetching Python packages: %s", e)
            return []

    async def star_repository(self, owner: str, repo: str, token: str) -> bool:
        return await self._github.star_repo(owner, repo, token)

    async def unstar_repository(self, owner: str, repo: str, token: str) -> bool:
        return await self._github.unstar_repo(owner, repo, token)

    async def is_starred(self, owner: str, repo: str, token: str) -> bool:
        return await self._github.is_starred(owner, repo, token)
