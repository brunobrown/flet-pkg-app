from typing import Any

import httpx

from src.core.constants import PYPI_API_BASE, PYPISTATS_API_BASE
from src.core.exceptions import ApiError
from src.core.logger import get_logger

logger = get_logger(__name__)


class PyPISource:
    def __init__(self):
        self._client = httpx.AsyncClient(timeout=30.0)

    async def get_package_info(self, package_name: str) -> dict[str, Any]:
        try:
            response = await self._client.get(f"{PYPI_API_BASE}/pypi/{package_name}/json")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise ApiError(f"PyPI API error for {package_name}: {e}", e.response.status_code) from e

    async def search_packages(self, query: str) -> list[dict[str, Any]]:
        """Search PyPI using the simple API / XML-RPC is deprecated.
        We use a workaround: search via pypi.org/search is not API-based.
        Instead, we search GitHub for flet-related Python repos and cross-reference PyPI.
        """
        return []

    async def get_recent_downloads(self, package_name: str) -> int:
        try:
            response = await self._client.get(
                f"{PYPISTATS_API_BASE}/packages/{package_name}/recent",
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("last_month", 0)
        except httpx.HTTPError:
            logger.warning("Could not fetch download stats for %s", package_name)
            return 0

    async def get_package_dependencies(self, package_name: str) -> list[str]:
        try:
            info = await self.get_package_info(package_name)
            requires = info.get("info", {}).get("requires_dist", [])
            if requires:
                return [r.split(";")[0].split(" ")[0] for r in requires]
            return []
        except ApiError:
            return []

    async def close(self) -> None:
        await self._client.aclose()
