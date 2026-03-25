"""PyPI API source — package info and download stats (fallback for ClickHouse)."""

import asyncio
from typing import Any

import httpx

from config import settings
from src.core.exceptions import ApiError
from src.core.logger import get_logger

logger = get_logger(__name__)


class PyPISource:
    def __init__(self):
        self._pypi_client = httpx.AsyncClient(
            base_url=settings.PYPI_API_BASE,
            timeout=30.0,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )
        self._stats_client = httpx.AsyncClient(
            base_url=settings.PYPISTATS_API_BASE,
            timeout=15.0,
            limits=httpx.Limits(max_connections=5, max_keepalive_connections=3),
        )
        self._stats_semaphore = asyncio.Semaphore(settings.PYPISTATS_MAX_CONCURRENT)

    async def get_package_info(self, package_name: str) -> dict[str, Any]:
        try:
            response = await self._pypi_client.get(f"/pypi/{package_name}/json")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise ApiError(f"PyPI API error for {package_name}: {e}", e.response.status_code) from e

    async def get_recent_downloads(self, package_name: str) -> int:
        """Get recent downloads with semaphore + retry for 429."""
        for attempt in range(settings.MAX_RETRIES + 1):
            try:
                async with self._stats_semaphore:
                    response = await self._stats_client.get(
                        f"/packages/{package_name}/recent",
                    )
                if response.status_code == 429:
                    if attempt < settings.MAX_RETRIES:
                        wait = float(response.headers.get("Retry-After", 2**attempt))
                        logger.warning(
                            "429 from pypistats for %s, retry %d in %ss",
                            package_name,
                            attempt + 1,
                            wait,
                        )
                        await asyncio.sleep(wait)
                        continue
                    logger.warning("pypistats 429 exhausted retries for %s", package_name)
                    return 0
                response.raise_for_status()
                data = response.json()
                return data.get("data", {}).get("last_month", 0)
            except httpx.HTTPError:
                logger.warning("Could not fetch download stats for %s", package_name)
                return 0
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
        await self._pypi_client.aclose()
        await self._stats_client.aclose()
