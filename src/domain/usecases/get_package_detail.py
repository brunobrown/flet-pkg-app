from src.domain.entities.package import Package
from src.domain.repositories.package_repository import PackageRepository


class GetPackageDetailUseCase:
    def __init__(self, repository: PackageRepository):
        self._repository = repository

    async def execute(self, owner: str, repo: str) -> Package:
        return await self._repository.get_package_detail(owner, repo)

    async def execute_by_name(self, package_name: str) -> Package:
        return await self._repository.get_package_by_name(package_name)
