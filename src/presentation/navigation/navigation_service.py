"""Navigation service — encapsulates URL pushing and route deduplication."""

import flet as ft

from src.domain.entities.package import SortOption
from src.presentation.navigation.app_router import build_navigate_url, build_packages_url


class NavigationService:
    """Manages browser URL navigation with deduplication.

    Handles:
    - navigate(target): convert target string → URL → push_route
    - sync_and_reload(): update URL from current state + load data
    - Deduplication: _last_handled_route prevents double-load
    """

    def __init__(self, page: ft.Page):
        self._page = page
        self._last_handled_route: str = ""

    @property
    def last_handled_route(self) -> str:
        return self._last_handled_route

    @last_handled_route.setter
    def last_handled_route(self, value: str) -> None:
        self._last_handled_route = value

    def should_handle(self, route: str) -> bool:
        """Check if this route should be handled (not a duplicate)."""
        if route == self._last_handled_route:
            return False
        self._last_handled_route = route
        return True

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
        self.push(url)
        return url
