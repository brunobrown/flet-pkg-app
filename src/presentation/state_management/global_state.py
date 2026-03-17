"""Global application state container — single source of truth."""

from dataclasses import dataclass, field

import flet as ft

from src.domain.entities.package import Package
from src.domain.usecases.get_home_data import HomeData


@ft.observable
@dataclass
class PackagesState:
    """State for package search, listing, and home sections."""

    # Search/list
    packages: list[Package] = field(default_factory=list)
    total_count: int = 0
    current_page: int = 1
    search_query: str = ""
    sort_by: str = "default ranking"
    filter_type: str | None = None
    filter_official: bool = False
    filter_has_screenshot: bool = False
    is_loading: bool = False
    error: str = ""

    # Home
    home_data: HomeData | None = None
    home_loading: bool = False

    # Detail
    detail_package: Package | None = None
    detail_loading: bool = False
    detail_package_name: str = ""


@ft.observable
@dataclass
class UserState:
    """Authentication state for GitHub OAuth."""

    github_token: str = ""
    is_authenticated: bool = False
    username: str = ""

    def login(self, token: str, username: str = "") -> None:
        self.github_token = token
        self.is_authenticated = True
        self.username = username

    def logout(self) -> None:
        self.github_token = ""
        self.is_authenticated = False
        self.username = ""


@ft.observable
@dataclass
class ThemeState:
    """Theme preferences."""

    is_dark: bool = True


@ft.observable
@dataclass
class AppState:
    """Root state — aggregates all sub-states."""

    packages: PackagesState = field(default_factory=PackagesState)
    user: UserState = field(default_factory=UserState)
    theme: ThemeState = field(default_factory=ThemeState)

    # Current route — changing this triggers UI re-render
    current_route: str = "/"
    detail_package_name: str = ""
