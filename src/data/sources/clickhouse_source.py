"""ClickHouse public PyPI stats — batch queries, no rate limiting, <10ms responses."""

import re
from typing import Any

import httpx

from config import settings
from src.core.logger import get_logger

logger = get_logger(__name__)

# Package names: only alphanumeric, hyphens, underscores, dots
_SAFE_NAME_RE = re.compile(r"^[a-zA-Z0-9._-]+$")


def _sanitize_name(name: str) -> str:
    """Validate and return a safe package name for SQL queries."""
    if not _SAFE_NAME_RE.match(name):
        raise ValueError(f"Invalid package name: {name!r}")
    return name


class ClickHouseSource:
    def __init__(self):
        self._client = httpx.AsyncClient(
            timeout=15.0,
            limits=httpx.Limits(max_connections=5, max_keepalive_connections=3),
        )

    async def _query(self, sql: str) -> list[dict[str, Any]]:
        """Execute a SQL query against the ClickHouse public PyPI dataset."""
        try:
            response = await self._client.get(
                settings.CLICKHOUSE_URL,
                params={
                    "query": sql,
                    "user": settings.CLICKHOUSE_USER,
                    "password": settings.CLICKHOUSE_PASSWORD,
                    "default_format": "JSON",
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except httpx.HTTPError as e:
            logger.warning("ClickHouse query failed: %s", e)
            return []

    async def get_downloads_batch(self, package_names: list[str], days: int = 30) -> dict[str, int]:
        """Get download counts for multiple packages in a single query."""
        if not package_names:
            return {}

        safe_names = []
        for name in package_names:
            try:
                safe_names.append(_sanitize_name(name))
            except ValueError:
                logger.warning("Skipping invalid package name: %s", name)

        if not safe_names:
            return {}

        escaped = ", ".join(f"'{n}'" for n in safe_names)
        days = int(days)
        sql = (
            f"SELECT project, sum(count) as downloads "
            f"FROM pypi.pypi_downloads_per_day "
            f"WHERE project IN ({escaped}) AND date >= today() - {days} "
            f"GROUP BY project"
        )
        rows = await self._query(sql)
        return {row["project"]: int(row["downloads"]) for row in rows}

    async def get_downloads(self, package_name: str, days: int = 30) -> int:
        """Get download count for a single package."""
        result = await self.get_downloads_batch([package_name], days)
        return result.get(package_name, 0)

    async def get_total_downloads(self, package_name: str) -> int:
        """Get all-time total downloads."""
        name = _sanitize_name(package_name)
        sql = (
            f"SELECT sum(count) as total FROM pypi.pypi_downloads_per_day WHERE project = '{name}'"
        )
        rows = await self._query(sql)
        if rows:
            return int(rows[0]["total"])
        return 0

    async def get_downloads_by_version(
        self, package_name: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Get downloads broken down by version."""
        name = _sanitize_name(package_name)
        limit = int(limit)
        sql = (
            f"SELECT version, sum(count) as downloads "
            f"FROM pypi.pypi_downloads_per_day_by_version "
            f"WHERE project = '{name}' "
            f"GROUP BY version ORDER BY downloads DESC LIMIT {limit}"
        )
        return await self._query(sql)

    async def get_downloads_trend(self, package_name: str, weeks: int = 8) -> list[dict[str, Any]]:
        """Get weekly download trend."""
        name = _sanitize_name(package_name)
        days = int(weeks) * 7
        sql = (
            f"SELECT toStartOfWeek(date)::Date32 AS week, sum(count) AS downloads "
            f"FROM pypi.pypi_downloads_per_day "
            f"WHERE project = '{name}' AND date >= today() - {days} "
            f"GROUP BY week ORDER BY week DESC"
        )
        return await self._query(sql)

    async def get_package_metadata(self, package_name: str) -> dict[str, Any] | None:
        """Get package metadata from ClickHouse pypi.projects table."""
        name = _sanitize_name(package_name)
        sql = (
            f"SELECT name, version, summary, author, license, home_page, requires_dist "
            f"FROM pypi.projects "
            f"WHERE name = '{name}' "
            f"ORDER BY upload_time DESC LIMIT 1"
        )
        rows = await self._query(sql)
        return rows[0] if rows else None

    async def close(self) -> None:
        await self._client.aclose()
