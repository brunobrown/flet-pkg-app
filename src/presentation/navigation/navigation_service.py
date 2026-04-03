"""Navigation service — encapsulates URL pushing and route deduplication."""

import logging
import time

import flet as ft

from src.domain.entities.package import SortOption
from src.presentation.navigation.app_router import build_navigate_url, build_packages_url

logger = logging.getLogger(__name__)

# Minimum interval (seconds) before the same route is re-processed.
# Prevents double-fire on fast clicks, but allows reconnection re-processing.
_DEDUP_WINDOW = 2.0


class NavigationService:
    """Manages browser URL navigation with deduplication.

    Handles:
    - navigate(target): convert target string → URL → push_route
    - sync_and_reload(): update URL from current state + load data
    - Deduplication: _last_handled_route prevents double-load within _DEDUP_WINDOW
    """

    def __init__(self, page: ft.Page):
        self._page = page
        self._last_handled_route: str = ""
        self._last_handled_time: float = 0.0

    @property
    def last_handled_route(self) -> str:
        return self._last_handled_route

    @last_handled_route.setter
    def last_handled_route(self, value: str) -> None:
        self._last_handled_route = value

    def should_handle(self, route: str) -> bool:
        """Check if this route should be handled (not a recent duplicate)."""
        now = time.monotonic()
        if route == self._last_handled_route:
            elapsed = now - self._last_handled_time
            if elapsed < _DEDUP_WINDOW:
                logger.debug("[NAV] Route dedup SKIP: %s (%.1fs ago)", route, elapsed)
                return False
            logger.debug("[NAV] Route stale re-process: %s (%.1fs ago)", route, elapsed)
        self._last_handled_route = route
        self._last_handled_time = now
        return True

    def reset(self) -> None:
        """Reset deduplication state — used on reconnection."""
        logger.debug("Navigation state reset")
        self._last_handled_route = ""
        self._last_handled_time = 0.0

    def push(self, route: str) -> None:
        """Push a URL to the browser history (fires on_route_change)."""
        self._page.run_task(self._page.push_route, route)

    def navigate(self, target: str) -> None:
        """Convert internal target to URL and push."""
        url = build_navigate_url(target)
        self.push(url)

    def push_packages_url(
        self,
        query: str = "",
        sort: str = SortOption.DEFAULT,
        filter_type: str | None = None,
        official: bool = False,
        categories: list[str] | None = None,
        page_num: int = 1,
    ) -> str:
        """Build packages URL from params, mark as handled, and push.

        Returns the built URL for caller use.
        """
        url = build_packages_url(
            query=query,
            sort=sort,
            filter_type=filter_type,
            official=official,
            categories=categories,
            page_num=page_num,
        )
        self._last_handled_route = url
        self._last_handled_time = time.monotonic()
        self.push(url)
        return url
