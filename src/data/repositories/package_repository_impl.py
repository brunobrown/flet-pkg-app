import asyncio

from config import settings
from src.core.exceptions import PackageNotFoundError
from src.core.logger import get_logger
from src.data.models.mappers import github_repo_to_package, pypi_info_to_package
from src.data.sources.clickhouse_source import ClickHouseSource
from src.data.sources.github_source import GitHubSource
from src.data.sources.package_discovery import PackageDiscovery, classify_by_summary
from src.data.sources.pypi_source import PyPISource
from src.domain.entities.package import Package, SortOption
from src.domain.repositories.package_repository import PackageRepository
from src.services.cache_service import CacheService
from src.services.package_index_service import PackageIndexService

logger = get_logger(__name__)


class PackageRepositoryImpl(PackageRepository):
    def __init__(
        self,
        github_source: GitHubSource,
        pypi_source: PyPISource,
        clickhouse_source: ClickHouseSource,
        cache: CacheService,
        index: PackageIndexService,
        discovery: PackageDiscovery,
    ):
        self._github = github_source
        self._pypi = pypi_source
        self._ch = clickhouse_source
        self._cache = cache
        self._index = index
        self._discovery = discovery

    # --- Downloads (used only by detail pages) ---

    async def _get_downloads(self, name: str) -> int:
        cached = self._cache.get(f"dl:{name}")
        if cached is not None:
            return cached
        try:
            ch_data = await self._ch.get_downloads_batch([name], days=settings.INDEX_DOWNLOAD_DAYS)
            downloads = ch_data.get(name, 0)
            self._cache.set(f"dl:{name}", downloads, ttl=settings.CACHE_TTL_DOWNLOADS)
            return downloads
        except Exception:
            return 0

    async def _get_flet_repo_stars(self) -> int:
        cache_key = "flet_repo_stars"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        try:
            repo = await self._github.get_repository("flet-dev", "flet")
            stars = repo.get("stargazers_count", 0)
            self._cache.set(cache_key, stars)
            return stars
        except Exception:
            return 0

    # --- Search: queries the in-memory index (zero HTTP) ---

    async def search_packages(
        self,
        query: str,
        page: int = 1,
        per_page: int = 10,
        sort: str = SortOption.DEFAULT,
        package_type: str | None = None,
        official_only: bool = False,
        pypi_only: bool = True,
        categories: list[str] | None = None,
    ) -> tuple[list[Package], int]:
        await self._index.wait_until_ready()
        return self._index.query(
            text=query,
            sort=sort,
            package_type=package_type,
            official_only=official_only,
            pypi_only=pypi_only,
            categories=categories,
            page=page,
            per_page=per_page,
        )

    # --- Home page sections: also from the index ---

    async def get_official_packages(self) -> list[Package]:
        await self._index.wait_until_ready()
        packages, _ = self._index.query(official_only=True, sort="most downloads", per_page=5)
        return packages

    async def get_trending_packages(self, limit: int = 6, pypi_only: bool = True) -> list[Package]:
        await self._index.wait_until_ready()
        packages, _ = self._index.query(sort="trending", pypi_only=pypi_only, per_page=limit)
        return packages

    async def get_service_packages(self, limit: int = 6, pypi_only: bool = True) -> list[Package]:
        await self._index.wait_until_ready()
        packages, _ = self._index.query(
            package_type="Services", sort="most downloads", pypi_only=pypi_only, per_page=limit
        )
        return packages

    async def get_ui_control_packages(
        self, limit: int = 6, pypi_only: bool = True
    ) -> list[Package]:
        await self._index.wait_until_ready()
        packages, _ = self._index.query(
            package_type="UI Controls",
            sort="most downloads",
            pypi_only=pypi_only,
            per_page=limit,
        )
        return packages

    async def get_python_packages(self, limit: int = 6, pypi_only: bool = True) -> list[Package]:
        await self._index.wait_until_ready()
        packages, _ = self._index.query(
            package_type="Python Package",
            sort="most downloads",
            pypi_only=pypi_only,
            per_page=limit,
        )
        return packages

    # --- Detail pages: still make HTTP calls (per-package, cached) ---

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
        pkg.package_type = classify_by_summary(pkg.description, pkg.name)
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

        pkg: Package | None = None
        try:
            pypi_data = await self._pypi.get_package_info(package_name)
            pkg = pypi_info_to_package(pypi_data)
            info = pypi_data.get("info", {})
            pkg.package_type = classify_by_summary(info.get("summary", ""), package_name)
            pkg.downloads = await self._get_downloads(package_name)
        except Exception:
            logger.info("Package %s not on PyPI, trying GitHub", package_name)

        if pkg is None:
            pkg = await self._fetch_github_only_package(package_name)
            if pkg is None:
                raise PackageNotFoundError(f"Package '{package_name}' not found on PyPI or GitHub")

        official_names = await self._discovery.get_official_extension_names()
        is_official = package_name in official_names

        if is_official:
            pkg.github_owner = "flet-dev"
            pkg.github_repo = "flet"
            pkg.repository_url = (
                f"https://github.com/flet-dev/flet/tree/main/sdk/python/packages/{package_name}"
            )
            pkg.issues_url = "https://github.com/flet-dev/flet/issues"
            try:
                readme, changelog = await asyncio.gather(
                    self._github.get_file_content(
                        "flet-dev", "flet", f"sdk/python/packages/{package_name}/README.md"
                    ),
                    self._github.get_file_content(
                        "flet-dev", "flet", f"sdk/python/packages/{package_name}/CHANGELOG.md"
                    ),
                )
                pkg.readme = readme
                pkg.changelog = changelog
                pkg.stars = await self._get_flet_repo_stars()
            except Exception:
                logger.warning("Failed to fetch README/changelog for official %s", package_name)
        elif pkg.github_owner and pkg.github_repo:
            # Use github_owner as publisher (always correct for profile URL)
            pkg.publisher = pkg.github_owner
            # Try github_repo first, then package_name as fallback
            # (PyPI URLs may use underscores while GitHub uses hyphens)
            repo_names = [pkg.github_repo]
            if package_name != pkg.github_repo:
                repo_names.append(package_name)
            for repo_name in repo_names:
                try:
                    readme, changelog, repo_data = await asyncio.gather(
                        self._github.get_readme(pkg.github_owner, repo_name),
                        self._github.get_file_content(pkg.github_owner, repo_name, "CHANGELOG.md"),
                        self._github.get_repository(pkg.github_owner, repo_name),
                    )
                    pkg.readme = readme
                    pkg.changelog = changelog
                    pkg.stars = repo_data.get("stargazers_count", 0)
                    pkg.forks = repo_data.get("forks_count", 0)
                    pkg.topics = repo_data.get("topics", [])
                    pkg.github_repo = repo_name
                    if not pkg.issues_url:
                        full_name = repo_data.get("full_name", "")
                        pkg.issues_url = f"https://github.com/{full_name}/issues"
                    break
                except Exception:
                    continue
            else:
                logger.info("No GitHub data for %s", package_name)

        if is_official:
            pkg.is_official = True
            pkg.publisher = "flet.dev"

        # Copy verified status from index if ready (non-blocking)
        if self._index.is_ready:
            idx_pkgs, _ = self._index.query(text=package_name, pypi_only=False, per_page=1)
            if idx_pkgs and idx_pkgs[0].name == pkg.name:
                pkg.is_verified = idx_pkgs[0].is_verified

        self._cache.set(cache_key, pkg)
        return pkg

    async def _fetch_github_only_package(self, package_name: str) -> Package | None:
        try:
            data = await self._github.search_repositories(
                query=f"{package_name} language:python",
                sort="stars",
                per_page=5,
            )
            items = data.get("items", [])
            for item in items:
                if item.get("name", "").lower() == package_name.lower():
                    pkg = github_repo_to_package(item)
                    pkg.package_type = classify_by_summary(pkg.description, pkg.name)
                    return pkg
            if items:
                pkg = github_repo_to_package(items[0])
                pkg.package_type = classify_by_summary(pkg.description, pkg.name)
                return pkg
        except Exception:
            logger.warning("GitHub search failed for %s", package_name)
        return None

    # --- Star/unstar (unchanged) ---

    async def star_repository(self, owner: str, repo: str, token: str) -> bool:
        return await self._github.star_repo(owner, repo, token)

    async def unstar_repository(self, owner: str, repo: str, token: str) -> bool:
        return await self._github.unstar_repo(owner, repo, token)

    async def is_starred(self, owner: str, repo: str, token: str) -> bool:
        return await self._github.is_starred(owner, repo, token)
