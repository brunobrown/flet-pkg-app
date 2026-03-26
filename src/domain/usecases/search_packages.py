from src.domain.entities.package import Package
from src.domain.repositories.package_repository import PackageRepository


class SearchPackagesUseCase:
    def __init__(self, repository: PackageRepository):
        self._repository = repository

    async def execute(
        self,
        query: str,
        page: int = 1,
        per_page: int = 10,
        sort: str = "default ranking",
        package_type: str | None = None,
        official_only: bool = False,
        pypi_only: bool = True,
    ) -> tuple[list[Package], int]:
        return await self._repository.search_packages(
            query=query,
            page=page,
            per_page=per_page,
            sort=sort,
            package_type=package_type,
            official_only=official_only,
            pypi_only=pypi_only,
        )
