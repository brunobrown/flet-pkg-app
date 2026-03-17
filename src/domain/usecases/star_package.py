from src.domain.repositories.package_repository import PackageRepository


class StarPackageUseCase:
    def __init__(self, repository: PackageRepository):
        self._repository = repository

    async def star(self, owner: str, repo: str, token: str) -> bool:
        return await self._repository.star_repository(owner, repo, token)

    async def unstar(self, owner: str, repo: str, token: str) -> bool:
        return await self._repository.unstar_repository(owner, repo, token)

    async def is_starred(self, owner: str, repo: str, token: str) -> bool:
        return await self._repository.is_starred(owner, repo, token)
