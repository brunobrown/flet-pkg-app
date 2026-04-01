import base64
from typing import Any

import httpx

from config import settings
from src.core.exceptions import ApiError
from src.core.logger import get_logger

logger = get_logger(__name__)


class GitHubSource:
    def __init__(self, token: str = ""):
        headers: dict[str, str] = {
            "Accept": "application/vnd.github.v3+json",
        }
        if token:
            headers["Authorization"] = f"token {token}"
        self._client = httpx.AsyncClient(
            base_url=settings.GITHUB_API_BASE,
            headers=headers,
            timeout=10.0,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )

    async def search_repositories(
        self,
        query: str,
        sort: str = "stars",
        order: str = "desc",
        page: int = 1,
        per_page: int = 10,
    ) -> dict[str, Any]:
        try:
            response = await self._client.get(
                "/search/repositories",
                params={
                    "q": query,
                    "sort": sort,
                    "order": order,
                    "page": page,
                    "per_page": per_page,
                },
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error("GitHub search error: %s", e)
            raise ApiError(f"GitHub API error: {e}", e.response.status_code) from e

    async def get_repository(self, owner: str, repo: str) -> dict[str, Any]:
        try:
            response = await self._client.get(f"/repos/{owner}/{repo}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise ApiError(f"GitHub repo error: {e}", e.response.status_code) from e

    async def get_readme(self, owner: str, repo: str) -> str:
        try:
            response = await self._client.get(
                f"/repos/{owner}/{repo}/readme",
                headers={"Accept": "application/vnd.github.v3+json"},
            )
            response.raise_for_status()
            data = response.json()
            content = data.get("content", "")
            if content:
                return base64.b64decode(content).decode("utf-8", errors="replace")
            return ""
        except httpx.HTTPStatusError:
            return ""

    async def get_file_content(self, owner: str, repo: str, path: str) -> str:
        try:
            response = await self._client.get(
                f"/repos/{owner}/{repo}/contents/{path}",
            )
            response.raise_for_status()
            data = response.json()
            content = data.get("content", "")
            if content:
                return base64.b64decode(content).decode("utf-8", errors="replace")
            return ""
        except httpx.HTTPStatusError:
            return ""

    async def get_repo_contents(
        self, owner: str, repo: str, path: str = ""
    ) -> list[dict[str, Any]]:
        try:
            response = await self._client.get(
                f"/repos/{owner}/{repo}/contents/{path}",
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                return data
            return []
        except httpx.HTTPStatusError:
            return []

    async def star_repo(self, owner: str, repo: str, token: str) -> bool:
        try:
            response = await self._client.put(
                f"/user/starred/{owner}/{repo}",
                headers={"Authorization": f"token {token}"},
                content=b"",
            )
            return response.status_code == 204
        except httpx.HTTPError:
            return False

    async def unstar_repo(self, owner: str, repo: str, token: str) -> bool:
        try:
            response = await self._client.delete(
                f"/user/starred/{owner}/{repo}",
                headers={"Authorization": f"token {token}"},
            )
            return response.status_code == 204
        except httpx.HTTPError:
            return False

    async def is_starred(self, owner: str, repo: str, token: str) -> bool:
        try:
            response = await self._client.get(
                f"/user/starred/{owner}/{repo}",
                headers={"Authorization": f"token {token}"},
            )
            return response.status_code == 204
        except httpx.HTTPError:
            return False

    async def close(self) -> None:
        await self._client.aclose()
