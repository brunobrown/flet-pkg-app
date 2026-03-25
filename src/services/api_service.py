from config import settings
from src.data.repositories.package_repository_impl import PackageRepositoryImpl
from src.data.sources.clickhouse_source import ClickHouseSource
from src.data.sources.github_source import GitHubSource
from src.data.sources.pypi_source import PyPISource
from src.domain.repositories.package_repository import PackageRepository
from src.services.cache_service import CacheService


class ApiService:
    """Factory that creates and wires up all data layer dependencies."""

    def __init__(self):
        self._github_source = GitHubSource(token=settings.GITHUB_TOKEN)
        self._pypi_source = PyPISource()
        self._clickhouse_source = ClickHouseSource()
        self._cache = CacheService(ttl=settings.CACHE_TTL_SECONDS)
        self._repository = PackageRepositoryImpl(
            github_source=self._github_source,
            pypi_source=self._pypi_source,
            clickhouse_source=self._clickhouse_source,
            cache=self._cache,
        )

    @property
    def repository(self) -> PackageRepository:
        return self._repository

    @property
    def cache(self) -> CacheService:
        return self._cache

    async def close(self) -> None:
        await self._github_source.close()
        await self._pypi_source.close()
        await self._clickhouse_source.close()
