from abc import ABC, abstractmethod

from src.domain.entities.package import Package


class PackageRepository(ABC):
    @abstractmethod
    async def search_packages(
        self,
        query: str,
        page: int = 1,
        per_page: int = 10,
        sort: str = "default ranking",
        package_type: str | None = None,
        official_only: bool = False,
        pypi_only: bool = True,
    ) -> tuple[list[Package], int]:
        """Search packages. Returns (packages, total_count)."""

    @abstractmethod
    async def get_package_detail(self, owner: str, repo: str) -> Package:
        """Get detailed package info including README and changelog."""

    @abstractmethod
    async def get_package_by_name(self, package_name: str) -> Package:
        """Get package detail by PyPI name. Resolves GitHub owner/repo automatically."""

    @abstractmethod
    async def get_official_packages(self) -> list[Package]:
        """Get official Flet packages."""

    @abstractmethod
    async def get_trending_packages(self, limit: int = 6) -> list[Package]:
        """Get trending packages."""

    @abstractmethod
    async def get_service_packages(self, limit: int = 6) -> list[Package]:
        """Get service-type extension packages."""

    @abstractmethod
    async def get_ui_control_packages(self, limit: int = 6) -> list[Package]:
        """Get UI control extension packages."""

    @abstractmethod
    async def get_python_packages(self, limit: int = 6) -> list[Package]:
        """Get Python packages that depend on Flet."""

    @abstractmethod
    async def star_repository(self, owner: str, repo: str, token: str) -> bool:
        """Star a GitHub repository. Returns True on success."""

    @abstractmethod
    async def unstar_repository(self, owner: str, repo: str, token: str) -> bool:
        """Unstar a GitHub repository. Returns True on success."""

    @abstractmethod
    async def is_starred(self, owner: str, repo: str, token: str) -> bool:
        """Check if a repository is starred by the authenticated user."""
