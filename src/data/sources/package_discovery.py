"""Dynamic package discovery — no hardcoded lists.

Discovers Flet packages from:
1. GitHub monorepo (official extensions)
2. PyPI dependency analysis (community packages that depend on flet)
3. GitHub search (repos with topic:flet)
"""

import asyncio

from config import settings
from src.core.logger import get_logger
from src.data.models.mappers import github_repo_to_package, pypi_info_to_package
from src.data.sources.github_source import GitHubSource
from src.data.sources.pypi_source import PyPISource
from src.domain.entities.package import Package, PackageType
from src.services.cache_service import CacheService

logger = get_logger(__name__)


def classify_by_summary(summary: str, name: str) -> PackageType:
    """Classify a package as Service or UI Control based on its name and summary."""
    text = f"{name} {summary}".lower()
    for kw in settings.SERVICE_KEYWORDS:
        if kw in text:
            return PackageType.SERVICE
    for kw in settings.UI_CONTROL_KEYWORDS:
        if kw in text:
            return PackageType.UI_CONTROL
    return PackageType.PYTHON_PACKAGE


def is_flet_dependency(requires_dist: list[str] | None) -> bool:
    """Check if a package depends on flet (including flet[extras])."""
    if not requires_dist:
        return False
    for req in requires_dist:
        dep_name = req.split(";")[0].split(" ")[0].split(">")[0].split("=")[0].split("<")[0]
        # Strip extras: "flet[all]" → "flet"
        base_name = dep_name.split("[")[0].strip().lower()
        if base_name == "flet":
            return True
    return False


def _is_excluded(pkg: Package) -> bool:
    name = pkg.pypi_name.lower() if pkg.pypi_name else pkg.name.lower()
    return name in settings.EXCLUDED_PACKAGES


class PackageDiscovery:
    """Discovers and classifies Flet packages dynamically."""

    def __init__(self, github: GitHubSource, pypi: PyPISource, cache: CacheService):
        self._github = github
        self._pypi = pypi
        self._cache = cache

    # Fallback: known official extensions discovered from the monorepo.
    _FALLBACK_OFFICIAL = [
        "flet-ads",
        "flet-audio",
        "flet-audio-recorder",
        "flet-camera",
        "flet-charts",
        "flet-code-editor",
        "flet-color-pickers",
        "flet-datatable2",
        "flet-flashlight",
        "flet-geolocator",
        "flet-lottie",
        "flet-map",
        "flet-permission-handler",
        "flet-rive",
        "flet-secure-storage",
        "flet-video",
        "flet-webview",
    ]

    async def get_official_extension_names(self) -> list[str]:
        """Discover official extensions from the GitHub monorepo (with fallback)."""
        cache_key = "discovery:official_names"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            contents = await self._github.get_repo_contents(
                settings.FLET_ORG, settings.FLET_REPO, settings.FLET_PACKAGES_PATH
            )
            names = [
                item["name"]
                for item in contents
                if item.get("type") == "dir" and item["name"] not in settings.EXCLUDED_PACKAGES
            ]
            if names:
                self._cache.set(cache_key, names, ttl=settings.CACHE_TTL_DISCOVERY)
                return names
        except Exception as e:
            logger.warning("GitHub API unavailable for official packages: %s", e)

        logger.info("Using fallback official package list")
        self._cache.set(cache_key, self._FALLBACK_OFFICIAL, ttl=settings.INDEX_REINDEX_INTERVAL)
        return self._FALLBACK_OFFICIAL

    async def fetch_pypi_package(self, name: str) -> Package | None:
        """Fetch a package from PyPI and classify it."""
        try:
            data = await self._pypi.get_package_info(name)
            pkg = pypi_info_to_package(data)
            info = data.get("info", {})
            summary = info.get("summary", "") or ""
            pkg.package_type = classify_by_summary(summary, name)
            return pkg
        except Exception:
            return None

    async def fetch_official_packages(self) -> list[Package]:
        """Fetch all official extension packages from monorepo + PyPI."""
        names = await self.get_official_extension_names()
        if not names:
            return []

        results = await asyncio.gather(*[self.fetch_pypi_package(n) for n in names])
        packages: list[Package] = []
        for pkg in results:
            if isinstance(pkg, Package):
                pkg.is_official = True
                pkg.publisher = "flet.dev"
                pkg.github_owner = settings.FLET_ORG
                pkg.github_repo = settings.FLET_REPO
                pkg.repository_url = (
                    f"https://github.com/{settings.FLET_ORG}/{settings.FLET_REPO}/tree/main/"
                    f"{settings.FLET_PACKAGES_PATH}/{pkg.pypi_name or pkg.name}"
                )
                packages.append(pkg)
        return packages

    # --- Smart flet-related check with cache ---

    async def is_flet_related(
        self, name: str, pypi_only: bool = True, topics: list[str] | None = None
    ) -> bool:
        """Check if a package is related to Flet.

        Uses fast heuristics first (name prefix, topics) to skip PyPI calls.
        Results are cached for 24h to speed up re-indexing.
        """
        name_lower = name.lower()

        # Check cache first
        cache_key = f"flet_related:{name_lower}:{pypi_only}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        # Fast path: obvious flet package by name
        if name_lower.startswith(("flet-", "flet_")):
            if not pypi_only:
                self._cache.set(cache_key, True, ttl=settings.CACHE_TTL_DISCOVERY)
                return True
            # Verify it exists on PyPI
            try:
                await self._pypi.get_package_info(name)
                self._cache.set(cache_key, True, ttl=settings.CACHE_TTL_DISCOVERY)
                return True
            except Exception:
                self._cache.set(cache_key, False, ttl=settings.CACHE_TTL_DISCOVERY)
                return False

        # For non-"flet-" packages: check PyPI metadata for actual flet dependency.
        # Having "flet" in GitHub topics alone is NOT enough — the repo might just
        # be a project that uses Flet, not a reusable package/extension.
        has_flet_topic = topics and "flet" in [t.lower() for t in topics]

        try:
            data = await self._pypi.get_package_info(name)
            info = data.get("info", {})
            related = False
            if is_flet_dependency(info.get("requires_dist")):
                related = True
            elif "flet" in (info.get("summary") or "").lower():
                related = True
            elif "flet" in [k.strip().lower() for k in (info.get("keywords") or "").split(",")]:
                related = True
            self._cache.set(cache_key, related, ttl=settings.CACHE_TTL_DISCOVERY)
            return related
        except Exception:
            # Not on PyPI — accept only if has flet topic AND pypi_only is False
            if not pypi_only and has_flet_topic:
                self._cache.set(cache_key, True, ttl=settings.CACHE_TTL_DISCOVERY)
                return True
            self._cache.set(cache_key, False, ttl=settings.INDEX_REINDEX_INTERVAL)
            return False

    async def filter_flet_related(
        self, packages: list[Package], pypi_only: bool = True
    ) -> list[Package]:
        """Filter packages to only those related to Flet."""
        checks = await asyncio.gather(
            *[self.is_flet_related(p.pypi_name or p.name, pypi_only, p.topics) for p in packages]
        )
        return [p for p, is_flet in zip(packages, checks) if is_flet]

    # --- Parallel GitHub fetch for index building ---

    async def fetch_all_github_packages(self, pypi_only: bool = True) -> list[Package]:
        """Fetch all flet packages from GitHub search (parallel pages) + filter."""
        max_pages = settings.get("INDEX_MAX_GITHUB_PAGES", 5)

        # Fetch all pages in parallel
        async def _fetch_page(page_num: int) -> list[dict]:
            try:
                data = await self._github.search_repositories(
                    query="flet language:python",
                    sort="stars",
                    page=page_num,
                    per_page=100,
                )
                return data.get("items", [])
            except Exception as e:
                logger.error("GitHub search page %d error: %s", page_num, e)
                return []

        page_results = await asyncio.gather(*[_fetch_page(p) for p in range(1, max_pages + 1)])

        # Deduplicate and convert
        seen: set[str] = set()
        all_packages: list[Package] = []
        for items in page_results:
            for item in items:
                pkg = github_repo_to_package(item)
                if _is_excluded(pkg):
                    continue
                key = pkg.pypi_name or pkg.name
                if key in seen:
                    continue
                seen.add(key)
                pkg.package_type = classify_by_summary(pkg.description, pkg.name)
                all_packages.append(pkg)

        # Filter to flet-related only
        all_packages = await self.filter_flet_related(all_packages, pypi_only=pypi_only)
        return all_packages
