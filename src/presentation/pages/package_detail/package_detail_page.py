import flet as ft

from src.presentation.components.common.loading import ErrorMessage, LoadingIndicator
from src.presentation.hooks.use_packages import load_package_detail_by_name
from src.presentation.state_management.global_state import PackagesState, UserState
from src.presentation.themes.colors import DARK_ACCENT, DARK_CARD, DARK_DIVIDER, TAG_BG, TAG_COLOR
from src.services.api_service import ApiService
from src.utils.formatters import format_date, format_number


@ft.component
def PackageDetailPage(
    state: PackagesState,
    user: UserState,
    api: ApiService,
    package_name: str,
    on_copy: object,
    on_back: object,
) -> ft.Control:
    active_tab, set_active_tab = ft.use_state(0)
    is_starred, set_is_starred = ft.use_state(False)
    loading, set_loading = ft.use_state(True)
    error, set_error = ft.use_state("")

    async def _load_detail():
        set_loading(True)
        set_error("")
        try:
            await load_package_detail_by_name(state, api, package_name)
        except Exception as e:
            set_error(str(e))
        set_loading(False)

    ft.use_effect(_load_detail, dependencies=[package_name])

    if loading:
        return LoadingIndicator("Loading package details...")

    if error:
        return ErrorMessage(error)

    pkg = state.detail_package
    if not pkg:
        return ErrorMessage("Package not found")

    def handle_star(_e: ft.ControlEvent) -> None:
        # Star/unstar requires GitHub OAuth — not yet implemented
        pass

    def handle_copy(_e: ft.ControlEvent) -> None:
        if on_copy:
            on_copy(pkg.pip_install_command)

    # Tab contents
    readme_view = ft.Container(
        content=ft.Markdown(
            value=pkg.readme or "No README available",
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            on_tap_link=lambda e: None,
        ),
        padding=20,
    )

    changelog_view = ft.Container(
        content=ft.Markdown(
            value=pkg.changelog or "No changelog available",
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        ),
        padding=20,
    )

    doc_controls: list[ft.Control] = []
    if pkg.documentation_url:
        doc_controls.append(
            ft.TextButton(
                "Documentation",
                icon=ft.Icons.BOOK,
                url=pkg.documentation_url,
                style=ft.ButtonStyle(color=DARK_ACCENT),
            )
        )
    if pkg.repository_url:
        doc_controls.append(
            ft.TextButton(
                "GitHub Repository",
                icon=ft.Icons.CODE,
                url=pkg.repository_url,
                style=ft.ButtonStyle(color=DARK_ACCENT),
            )
        )
    if not doc_controls:
        doc_controls.append(ft.Text("No documentation links available", color="#9e9e9e"))
    docs_view = ft.Container(
        content=ft.Column(controls=doc_controls, spacing=12),
        padding=20,
    )

    # Topics
    topic_chips = [
        ft.Container(
            content=ft.Text(f"#{t}", size=12, color=TAG_COLOR),
            bgcolor=TAG_BG,
            border_radius=12,
            padding=ft.Padding(left=8, top=3, right=8, bottom=3),
        )
        for t in pkg.topics
    ]

    dep_controls = [ft.Text(d, size=12, color="#bdbdbd") for d in (pkg.dependencies or [])[:20]]

    # Sidebar
    sidebar = ft.Container(
        content=ft.Column(
            controls=[
                _sidebar_section(
                    "Statistics",
                    [
                        _stat_row(ft.Icons.STAR, "Stars", format_number(pkg.stars)),
                        _stat_row(ft.Icons.FORK_RIGHT, "Forks", format_number(pkg.forks)),
                        _stat_row(ft.Icons.DOWNLOAD, "Downloads", format_number(pkg.downloads)),
                    ],
                ),
                ft.Divider(color=DARK_DIVIDER),
                _sidebar_section(
                    "Repository",
                    [
                        ft.TextButton(
                            "GitHub",
                            icon=ft.Icons.CODE,
                            url=pkg.repository_url,
                            style=ft.ButtonStyle(color=DARK_ACCENT),
                        )
                        if pkg.repository_url
                        else ft.Container(),
                        ft.TextButton(
                            "Issues",
                            icon=ft.Icons.BUG_REPORT,
                            url=pkg.issues_url,
                            style=ft.ButtonStyle(color=DARK_ACCENT),
                        )
                        if pkg.issues_url
                        else ft.Container(),
                    ],
                ),
                ft.Divider(color=DARK_DIVIDER),
                _sidebar_section(
                    "Topics",
                    [ft.Row(controls=topic_chips, wrap=True, spacing=4)]
                    if topic_chips
                    else [ft.Text("No topics", size=12, color="#757575")],
                ),
                ft.Divider(color=DARK_DIVIDER),
                _sidebar_section(
                    "License",
                    [ft.Text(pkg.license or "Unknown", size=14, color="#bdbdbd")],
                ),
                ft.Divider(color=DARK_DIVIDER),
                _sidebar_section(
                    "Dependencies",
                    dep_controls
                    if dep_controls
                    else [ft.Text("No dependencies", size=12, color="#757575")],
                ),
            ],
            spacing=8,
        ),
        width=280,
        padding=16,
        bgcolor=DARK_CARD,
        border_radius=8,
    )

    return ft.Column(
        controls=[
            # Package header
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.ARROW_BACK,
                                    icon_color=ft.Colors.WHITE,
                                    on_click=lambda _: on_back() if on_back else None,
                                ),
                                ft.Text(
                                    f"{pkg.name} {pkg.version}",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.COPY,
                                    icon_size=16,
                                    icon_color="#9e9e9e",
                                    tooltip=pkg.pip_install_command,
                                    on_click=handle_copy,
                                ),
                            ],
                            spacing=8,
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    f"Published {format_date(pkg.updated_at)}",
                                    size=13,
                                    color="#9e9e9e",
                                ),
                                ft.Text(
                                    f"by {pkg.publisher}" if pkg.publisher else "",
                                    size=13,
                                    color="#9e9e9e",
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.THUMB_UP
                                            if is_starred
                                            else ft.Icons.THUMB_UP_OUTLINED,
                                            size=16,
                                            color=DARK_ACCENT,
                                        ),
                                        ft.Text(
                                            format_number(pkg.stars), size=13, color=DARK_ACCENT
                                        ),
                                    ],
                                    spacing=4,
                                ),
                            ],
                            spacing=16,
                        ),
                    ],
                    spacing=4,
                ),
                padding=ft.Padding(left=20, top=16, right=20, bottom=16),
            ),
            # Tabs + Sidebar
            ft.Row(
                controls=[
                    # Main content with tabs
                    ft.Container(
                        content=ft.Tabs(
                            length=3,
                            selected_index=active_tab,
                            on_change=lambda e: set_active_tab(int(e.data)),
                            content=ft.Column(
                                controls=[
                                    ft.TabBar(
                                        tabs=[
                                            ft.Tab(label="Readme"),
                                            ft.Tab(label="Changelog"),
                                            ft.Tab(label="Documentation"),
                                        ],
                                        indicator_color=DARK_ACCENT,
                                        label_color=DARK_ACCENT,
                                        unselected_label_color="#9e9e9e",
                                    ),
                                    ft.TabBarView(
                                        controls=[
                                            readme_view,
                                            changelog_view,
                                            docs_view,
                                        ],
                                        expand=True,
                                    ),
                                ],
                                expand=True,
                            ),
                        ),
                        expand=True,
                    ),
                    sidebar,
                ],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=20,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def _sidebar_section(title: str, controls: list[ft.Control]) -> ft.Control:
    return ft.Column(
        controls=[
            ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            *controls,
        ],
        spacing=6,
    )


def _stat_row(icon: ft.Icons, label: str, value: str) -> ft.Control:
    return ft.Row(
        controls=[
            ft.Icon(icon, size=16, color="#9e9e9e"),
            ft.Text(label, size=13, color="#9e9e9e"),
            ft.Container(expand=True),
            ft.Text(value, size=13, color=DARK_ACCENT, weight=ft.FontWeight.BOLD),
        ],
        spacing=8,
    )
