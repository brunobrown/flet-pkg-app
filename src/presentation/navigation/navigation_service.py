"""Navigation service that encapsulates page-level routing operations."""

import asyncio

import flet as ft

from src.presentation.navigation.app_router import (
    ROUTE_HOME,
    build_detail_route,
    build_packages_route,
)


class NavigationService:
    """Encapsulates all navigation actions for the application."""

    def __init__(self, page: ft.Page):
        self._page = page

    def push(self, route: str) -> None:
        """Push a new route to the browser history."""
        asyncio.create_task(self._page.push_route(route))

    def go_home(self) -> None:
        self.push(ROUTE_HOME)

    def go_packages(self, query: str = "") -> None:
        self.push(build_packages_route(query))

    def go_detail_by_name(self, package_name: str) -> None:
        """Navigate to package detail by package name."""
        self.push(build_detail_route(package_name))

    def go_back(self) -> None:
        """Navigate back by removing the top view."""
        if len(self._page.views) > 1:
            self._page.views.pop()
            top_view = self._page.views[-1]
            self.push(top_view.route)
        else:
            self.go_home()
