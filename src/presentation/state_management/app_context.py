"""Application context — provides state, services, and actions to all components."""

from collections.abc import Callable
from dataclasses import dataclass

import flet as ft

from src.presentation.state_management.global_state import AppState
from src.services.api_service import ApiService


@dataclass
class AppContextValue:
    """Value provided to all components via ft.use_context(AppCtx)."""

    state: AppState
    api: ApiService
    navigate: Callable[[str], None]
    go_back: Callable[[], str | None]
    toggle_theme: Callable[[], None]
    toggle_pypi_filter: Callable[[], None]
    search: Callable[[str], None]
    reload_packages: Callable[[], None]
    copy_to_clipboard: Callable[[str], None]


AppCtx = ft.create_context(None)
