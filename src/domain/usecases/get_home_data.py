import asyncio
from dataclasses import dataclass

from src.domain.entities.package import Package
from src.domain.repositories.package_repository import PackageRepository


@dataclass
class HomeData:
    official_packages: list[Package]
    trending_packages: list[Package]
    service_packages: list[Package]
    ui_control_packages: list[Package]
    python_packages: list[Package]


class GetHomeDataUseCase:
    def __init__(self, repository: PackageRepository):
        self._repository = repository

    async def execute(self, pypi_only: bool = True) -> HomeData:
        results = await asyncio.gather(
            self._repository.get_official_packages(),
            self._repository.get_trending_packages(limit=6, pypi_only=pypi_only),
            self._repository.get_service_packages(limit=6, pypi_only=pypi_only),
            self._repository.get_ui_control_packages(limit=6, pypi_only=pypi_only),
            self._repository.get_python_packages(limit=6, pypi_only=pypi_only),
        )
        return HomeData(
            official_packages=results[0],
            trending_packages=results[1],
            service_packages=results[2],
            ui_control_packages=results[3],
            python_packages=results[4],
        )
