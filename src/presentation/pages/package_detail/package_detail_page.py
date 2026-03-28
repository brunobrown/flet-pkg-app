"""Package detail page — fixed tabs, scrollable content, slide-in sidebar."""

import flet as ft

from src.presentation.components.common.footer import AppFooter
from src.presentation.components.common.loading import ErrorMessage, LoadingIndicator
from src.presentation.state_management.app_context import AppCtx
from src.presentation.state_management.global_state import PackagesState, UserState
from src.presentation.themes.colors import FLET_PINK
from src.services.api_service import ApiService
from src.utils.formatters import format_date, format_number


@ft.component
def PackageDetailPage(
    state: PackagesState,
    user: UserState,
    api: ApiService,
    package_name: str,
    on_copy: object,
) -> ft.Control:
    ctx = ft.use_context(AppCtx)
    active_tab, set_active_tab = ft.use_state(0)
    sidebar_open, set_sidebar_open = ft.use_state(False)
    is_dark = ctx.state.is_dark

    # Markdown styling adapted to theme mode
    code_theme = ft.MarkdownCodeTheme.ATOM_ONE_DARK if is_dark else ft.MarkdownCodeTheme.GITHUB
    md_style = ft.MarkdownStyleSheet(
        blockquote_decoration=ft.BoxDecoration(
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST if is_dark else "#E3F2FD",
            border=ft.Border(left=ft.BorderSide(4, ft.Colors.PRIMARY)),
            border_radius=4,
        ),
        blockquote_text_style=ft.TextStyle(color=ft.Colors.ON_SURFACE),
    )

    if state.error:
        return ErrorMessage(state.error)

    pkg = state.detail_package
    if not pkg:
        return LoadingIndicator("Loading package details...")

    def handle_copy(_e: ft.ControlEvent) -> None:
        if on_copy:
            on_copy(pkg.pip_install_command)

    def handle_share(_e: ft.ControlEvent) -> None:
        if on_copy:
            name = pkg.pypi_name or pkg.name
            card = (
                f":: {name} {pkg.version}\n"
                f"{pkg.description}\n"
                f"Stars: {format_number(pkg.stars)}"
                f" | Downloads: {format_number(pkg.downloads)}\n"
            )
            if pkg.publisher:
                card += f"Publisher: {pkg.publisher}"
            if pkg.license:
                card += f" | {pkg.license}"
            card += f"\n/packages/{name}"
            on_copy(card)

    def _handle_markdown_link(e: ft.ControlEvent) -> None:
        url = e.data or ""
        if url.startswith("#"):
            return
        if url.startswith(("http://", "https://")):
            e.page.run_task(ft.UrlLauncher().launch_url, url)

    # --- Tab content ---
    if active_tab == 1:
        changelog_text = _clean_readme(pkg.changelog) if pkg.changelog else "No changelog available"
        tab_content = ft.Markdown(
            value=changelog_text,
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            code_theme=code_theme,
            md_style_sheet=md_style,
            on_tap_link=_handle_markdown_link,
            shrink_wrap=True,
            fit_content=True,
        )
    elif active_tab == 2:
        doc_controls: list[ft.Control] = []
        if pkg.documentation_url:
            doc_controls.append(
                ft.TextButton(
                    "Documentation",
                    icon=ft.Icons.BOOK,
                    url=pkg.documentation_url,
                    style=ft.ButtonStyle(color=ft.Colors.PRIMARY),
                )
            )
        if pkg.repository_url:
            doc_controls.append(
                ft.TextButton(
                    "GitHub Repository",
                    icon=ft.Icons.CODE,
                    url=pkg.repository_url,
                    style=ft.ButtonStyle(color=ft.Colors.PRIMARY),
                )
            )
        if not doc_controls:
            doc_controls.append(
                ft.Text("No documentation links available", color=ft.Colors.ON_SURFACE_VARIANT)
            )
        tab_content = ft.Column(controls=doc_controls, spacing=12)
    else:
        readme_text = _clean_readme(pkg.readme) if pkg.readme else "No README available"
        tab_content = ft.Markdown(
            value=readme_text,
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            code_theme=code_theme,
            md_style_sheet=md_style,
            on_tap_link=_handle_markdown_link,
            shrink_wrap=True,
            fit_content=True,
        )

    # --- Sidebar content ---
    sidebar_content = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(
                        "Package Info",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_SURFACE,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=18,
                        icon_color=ft.Colors.ON_SURFACE_VARIANT,
                        on_click=lambda _: set_sidebar_open(False),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Divider(color=ft.Colors.OUTLINE_VARIANT),
            _sidebar_section(
                "Statistics",
                [
                    _stat_row(ft.Icons.STAR, "Stars", format_number(pkg.stars)),
                    _stat_row(ft.Icons.FORK_RIGHT, "Forks", format_number(pkg.forks)),
                    _stat_row(ft.Icons.DOWNLOAD, "Downloads", format_number(pkg.downloads)),
                ],
            ),
            ft.Divider(color=ft.Colors.OUTLINE_VARIANT),
            _sidebar_section(
                "Repository",
                [
                    ft.TextButton(
                        "GitHub",
                        icon=ft.Icons.CODE,
                        url=pkg.repository_url,
                        style=ft.ButtonStyle(color=ft.Colors.PRIMARY),
                    )
                    if pkg.repository_url
                    else ft.Container(),
                    ft.TextButton(
                        "Issues",
                        icon=ft.Icons.BUG_REPORT,
                        url=pkg.issues_url,
                        style=ft.ButtonStyle(color=ft.Colors.PRIMARY),
                    )
                    if pkg.issues_url
                    else ft.Container(),
                ],
            ),
            ft.Divider(color=ft.Colors.OUTLINE_VARIANT),
            _sidebar_section(
                "Topics",
                [
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(f"#{t}", size=12, color=ft.Colors.PRIMARY),
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                                border_radius=12,
                                padding=ft.Padding(left=8, top=3, right=8, bottom=3),
                            )
                            for t in pkg.topics
                        ],
                        wrap=True,
                        spacing=4,
                    )
                ]
                if pkg.topics
                else [ft.Text("No topics", size=12, color=ft.Colors.ON_SURFACE_VARIANT)],
            ),
            ft.Divider(color=ft.Colors.OUTLINE_VARIANT),
            _sidebar_section(
                "License",
                [
                    ft.Text(pkg.license or "Unknown", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                ],
            ),
            ft.Divider(color=ft.Colors.OUTLINE_VARIANT),
            _sidebar_section(
                "Dependencies",
                [
                    ft.Text(d, size=12, color=ft.Colors.ON_SURFACE_VARIANT)
                    for d in (pkg.dependencies or [])[:20]
                ]
                or [ft.Text("No dependencies", size=12, color=ft.Colors.ON_SURFACE_VARIANT)],
            ),
        ],
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
    )

    # --- Slide-in sidebar panel ---
    sidebar_panel = ft.Container(
        content=sidebar_content,
        width=300,
        bgcolor=ft.Colors.SURFACE_CONTAINER,
        padding=16,
        border_radius=ft.BorderRadius(top_left=12, bottom_left=12, top_right=0, bottom_right=0),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
            offset=ft.Offset(-2, 0),
        ),
        right=0,
        top=0,
        bottom=0,
        offset=ft.Offset(0, 0) if sidebar_open else ft.Offset(1, 0),
        animate_offset=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
    )

    # --- Toggle tab (vertical strip on right edge) ---
    toggle_tab = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(
                    ft.Icons.CHEVRON_LEFT if sidebar_open else ft.Icons.CHEVRON_RIGHT,
                    size=18,
                    color=ft.Colors.ON_PRIMARY,
                ),
                ft.RotatedBox(
                    content=ft.Text(
                        "Info",
                        size=14,
                        color=ft.Colors.ON_PRIMARY,
                        weight=ft.FontWeight.W_500,
                    ),
                    quarter_turns=1,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        ),
        width=28,
        height=80,
        bgcolor=FLET_PINK,
        border_radius=ft.BorderRadius(top_left=8, bottom_left=8, top_right=0, bottom_right=0),
        alignment=ft.Alignment.CENTER,
        on_click=lambda _: set_sidebar_open(not sidebar_open),
        ink=True,
    )

    # Wrap toggle in a column to center it vertically
    toggle_wrapper = ft.Container(
        content=ft.Column(
            controls=[toggle_tab],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        right=300 if sidebar_open else 0,
        top=0,
        bottom=0,
        animate_position=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
    )

    # --- Tab buttons ---
    def make_tab(label: str, index: int) -> ft.Control:
        is_active = index == active_tab
        return ft.Container(
            content=ft.Text(
                label,
                size=14,
                color=ft.Colors.PRIMARY if is_active else ft.Colors.ON_SURFACE_VARIANT,
                weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.NORMAL,
            ),
            padding=ft.Padding(left=16, top=10, right=16, bottom=10),
            border=ft.Border(
                bottom=ft.BorderSide(2, ft.Colors.PRIMARY) if is_active else ft.BorderSide(0),
            ),
            on_click=lambda _, idx=index: set_active_tab(idx),
            ink=True,
        )

    return ft.Column(
        controls=[
            # FIXED: Header
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.ResponsiveRow(
                            controls=[
                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            ft.Text(
                                                f"{pkg.name} {pkg.version}",
                                                size=24,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.ON_SURFACE,
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.COPY,
                                                icon_size=16,
                                                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                                tooltip=pkg.pip_install_command,
                                                on_click=handle_copy,
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.SHARE,
                                                icon_size=16,
                                                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                                tooltip="Share package",
                                                on_click=handle_share,
                                            ),
                                        ],
                                        spacing=0,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    col={
                                        ft.ResponsiveRowBreakpoint.XS: 12,
                                        ft.ResponsiveRowBreakpoint.MD: 8,
                                    },
                                ),
                                ft.Container(
                                    content=ft.Row(
                                        controls=[_like_button(pkg)],
                                        alignment=ft.MainAxisAlignment.END,
                                    ),
                                    col={
                                        ft.ResponsiveRowBreakpoint.XS: 12,
                                        ft.ResponsiveRowBreakpoint.MD: 4,
                                    },
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    f"Published {format_date(pkg.updated_at)}",
                                    size=13,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                                ft.Text(
                                    f"by {pkg.publisher}" if pkg.publisher else "",
                                    size=13,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                            ],
                            spacing=16,
                        ),
                    ],
                    spacing=4,
                ),
                padding=ft.Padding(left=20, top=16, right=20, bottom=8),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            ),
            # FIXED: Tab buttons
            ft.Container(
                content=ft.Row(
                    controls=[
                        make_tab("Readme", 0),
                        make_tab("Changelog", 1),
                        make_tab("Documentation", 2),
                    ],
                    spacing=0,
                ),
                padding=ft.Padding(left=20, top=0, right=20, bottom=0),
            ),
            ft.Divider(color=ft.Colors.OUTLINE_VARIANT, height=1),
            # SCROLLABLE: Content with overlay sidebar
            ft.Container(
                content=ft.Stack(
                    controls=[
                        # Main content (scrollable)
                        ft.ListView(
                            controls=[
                                ft.Container(
                                    content=tab_content,
                                    padding=ft.Padding(left=40, top=20, right=40, bottom=20),
                                ),
                            ],
                        ),
                        # Slide-in sidebar panel
                        sidebar_panel,
                        # Toggle tab on right edge
                        toggle_wrapper,
                    ],
                ),
                expand=True,
            ),
            # Footer always at bottom
            AppFooter(),
        ],
        spacing=0,
        expand=True,
    )


def _clean_readme(text: str) -> str:
    """Clean README for safe Markdown rendering."""
    import re

    text = re.sub(r">\s*\[!(NOTE|WARNING|TIP|IMPORTANT|CAUTION)]", "> **\\1:**", text)
    text = re.sub(r"\[!\[[^\]]*\]\([^)]*\)\]\([^)]*\)", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _sidebar_section(title: str, controls: list[ft.Control]) -> ft.Control:
    return ft.Column(
        controls=[
            ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
            *controls,
        ],
        spacing=6,
    )


def _like_button(pkg) -> ft.Control:
    """LIKE button with gradient, heart icon, arrow, and count badge."""
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.FAVORITE_OUTLINE, size=16, color=ft.Colors.WHITE),
                ft.Text("LIKE", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Row(
                    controls=[
                        ft.Container(
                            width=6,
                            height=6,
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                            rotate=ft.Rotate(0.785),
                            margin=ft.Margin(left=1, top=0, right=-4, bottom=4),
                        ),
                        ft.Container(
                            content=ft.Text(
                                format_number(pkg.stars),
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.ON_SURFACE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                            border_radius=ft.BorderRadius(
                                top_left=0, bottom_left=0, top_right=16, bottom_right=16
                            ),
                            alignment=ft.Alignment.CENTER,
                            padding=ft.Padding(left=6, top=2, right=10, bottom=2),
                        ),
                    ],
                    spacing=0,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=4,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        border_radius=20,
        padding=ft.Padding(left=8, top=2, right=2, bottom=2),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.CENTER_LEFT,
            end=ft.Alignment.CENTER_RIGHT,
            colors=["#ee3167", "#5673b0", "#5abae7"],
        ),
    )


def _stat_row(icon: ft.Icons, label: str, value: str) -> ft.Control:
    return ft.Row(
        controls=[
            ft.Icon(icon, size=16, color=ft.Colors.ON_SURFACE_VARIANT),
            ft.Text(label, size=13, color=ft.Colors.ON_SURFACE_VARIANT),
            ft.Container(expand=True),
            ft.Text(value, size=13, color=ft.Colors.PRIMARY, weight=ft.FontWeight.BOLD),
        ],
        spacing=8,
    )
