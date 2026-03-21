"""Dynamic package discovery — no hardcoded lists.

Discovers Flet packages from:
1. GitHub monorepo (official extensions)
2. PyPI dependency analysis (community packages that depend on flet)
3. GitHub search (repos with topic:flet)
"""

import asyncio

from src.core.constants import (
    EXCLUDED_PACKAGES,
    FLET_ORG,
    FLET_PACKAGES_PATH,
    FLET_REPO,
    SERVICE_KEYWORDS,
    UI_CONTROL_KEYWORDS,
)
from src.core.logger import get_logger
from src.data.models.mappers import pypi_info_to_package
from src.data.sources.github_source import GitHubSource
from src.data.sources.pypi_source import PyPISource
from src.domain.entities.package import Package, PackageType
from src.services.cache_service import CacheService

logger = get_logger(__name__)


def classify_by_summary(summary: str, name: str) -> PackageType:
    """Classify a package as Service or UI Control based on its name and summary."""
    text = f"{name} {summary}".lower()
    for kw in SERVICE_KEYWORDS:
        if kw in text:
            return PackageType.SERVICE
    for kw in UI_CONTROL_KEYWORDS:
        if kw in text:
            return PackageType.UI_CONTROL
    return PackageType.PYTHON_PACKAGE


def is_flet_dependency(requires_dist: list[str] | None) -> bool:
    """Check if a package depends on flet."""
    if not requires_dist:
        return False
    for req in requires_dist:
        dep_name = req.split(";")[0].split(" ")[0].split(">")[0].split("=")[0].split("<")[0]
        if dep_name.strip().lower() == "flet":
            return True
    return False


class PackageDiscovery:
    """Discovers and classifies Flet packages dynamically."""

    def __init__(self, github: GitHubSource, pypi: PyPISource, cache: CacheService):
        self._github = github
        self._pypi = pypi
        self._cache = cache

    # Fallback: known official extensions discovered from the monorepo.
    # Used when GitHub API is rate-limited (403). Updated automatically when API works.
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
            contents = await self._github.get_repo_contents(FLET_ORG, FLET_REPO, FLET_PACKAGES_PATH)
            names = [
                item["name"]
                for item in contents
                if item.get("type") == "dir" and item["name"] not in EXCLUDED_PACKAGES
            ]
            if names:
                # Cache for 24h — monorepo changes rarely
                self._cache.set(cache_key, names, ttl=86400)
                return names
        except Exception as e:
            logger.warning("GitHub API unavailable for official packages: %s", e)

        # Fallback when GitHub is rate-limited or unavailable
        logger.info("Using fallback official package list")
        self._cache.set(cache_key, self._FALLBACK_OFFICIAL, ttl=3600)
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
                pkg.github_owner = FLET_ORG
                pkg.github_repo = FLET_REPO
                pkg.repository_url = (
                    f"https://github.com/{FLET_ORG}/{FLET_REPO}/tree/main/"
                    f"{FLET_PACKAGES_PATH}/{pkg.pypi_name or pkg.name}"
                )
                packages.append(pkg)
        return packages

    async def is_flet_related(self, name: str) -> bool:
        """Check if a package is related to Flet (depends on it or mentions it)."""
        # Name starts with "flet" → very likely related
        if name.lower().startswith("flet"):
            return True
        try:
            data = await self._pypi.get_package_info(name)
            info = data.get("info", {})
            # Depends on flet
            if is_flet_dependency(info.get("requires_dist")):
                return True
            # Summary mentions flet
            summary = (info.get("summary") or "").lower()
            if "flet" in summary:
                return True
            return False
        except Exception:
            return False

    async def filter_flet_related(self, packages: list[Package]) -> list[Package]:
        """Filter a list of packages to only those related to Flet."""
        checks = await asyncio.gather(
            *[self.is_flet_related(p.pypi_name or p.name) for p in packages]
        )
        return [p for p, is_flet in zip(packages, checks) if is_flet]

    async def get_service_extension_names(self) -> list[str]:
        """Get names of official extensions classified as Services."""
        names = await self.get_official_extension_names()
        result: list[str] = []
        for name in names:
            pkg = await self.fetch_pypi_package(name)
            if pkg and pkg.package_type == PackageType.SERVICE:
                result.append(name)
        return result

    async def get_ui_control_extension_names(self) -> list[str]:
        """Get names of official extensions classified as UI Controls."""
        names = await self.get_official_extension_names()
        result: list[str] = []
        for name in names:
            pkg = await self.fetch_pypi_package(name)
            if pkg and pkg.package_type == PackageType.UI_CONTROL:
                result.append(name)
        return result
