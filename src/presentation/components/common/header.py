"""Responsive header component.

Home: no logo (it's in hero), just Help + theme toggle.
Other pages: logo left, search center, Help + theme right (like pub.dev).
"""

import flet as ft


@ft.component
def AppHeader(
    on_theme_toggle: object = None,
    on_open_drawer: object = None,
    on_navigate_home: object = None,
    on_search: object = None,
    on_toggle_pypi_filter: object = None,
    on_navigate_guide: object = None,
    on_navigate_contribute: object = None,
    is_dark: bool = True,
    show_logo: bool = True,
    show_pypi_only: bool = True,
    search_query: str = "",
) -> ft.Control:
    query, set_query = ft.use_state(search_query)
    theme_icon = ft.Icons.LIGHT_MODE_OUTLINED if is_dark else ft.Icons.DARK_MODE_OUTLINED

    def handle_search_submit(e: ft.ControlEvent) -> None:
        text = e.data if e.data is not None else query
        if on_search:
            on_search(text)

    def handle_clear(_e: ft.ControlEvent) -> None:
        set_query("")

    # --- Desktop header ---
    if show_logo:
        # Logo + app name
        logo_group = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Image(src="/images/flet.svg", width=28, height=28, fit=ft.BoxFit.CONTAIN),
                    ft.Text(
                        "Flet PKG",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_SURFACE,
                    ),
                ],
                spacing=8,
            ),
            on_click=lambda _: on_navigate_home() if on_navigate_home else None,
            ink=True,
            padding=ft.Padding(left=4, top=4, right=8, bottom=4),
        )

        desktop_items: list[ft.Control] = [logo_group]
        if on_search:
            # Packages list: logo+name | spacer | search (fixed width) | spacer | help + theme
            desktop_items.extend(
                [
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.TextField(
                            value=query,
                            hint_text="Search packages",
                            on_change=lambda e: set_query(e.data or ""),
                            on_submit=handle_search_submit,
                            border_radius=25,
                            content_padding=ft.Padding(left=16, top=8, right=16, bottom=8),
                            border_color=ft.Colors.OUTLINE_VARIANT,
                            focused_border_color=ft.Colors.PRIMARY,
                            cursor_color=ft.Colors.PRIMARY,
                            text_size=14,
                            prefix_icon=ft.Icons.SEARCH,
                            suffix=ft.Container(
                                content=ft.Icon(
                                    ft.Icons.CLOSE,
                                    size=16,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                                on_click=handle_clear,
                                ink=True,
                                tooltip="Clear search",
                            )
                            if query
                            else None,
                            height=42,
                            bgcolor=ft.Colors.SURFACE_CONTAINER,
                            hint_style=ft.TextStyle(color=ft.Colors.ON_SURFACE_VARIANT),
                        ),
                        width=650,
                    ),
                    ft.Container(expand=True),
                ]
            )
        else:
            # Detail: logo+name | spacer | help + theme
            desktop_items.append(ft.Container(expand=True))

        desktop_items.extend(
            [
                _help_menu(
                    on_toggle_pypi_filter, show_pypi_only, on_navigate_guide, on_navigate_contribute
                ),
                _theme_button(theme_icon, on_theme_toggle),
            ]
        )
        desktop_row = ft.Row(
            controls=desktop_items,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
    else:
        # Home: just spacer + help + theme (no logo, no search)
        desktop_row = ft.Row(
            controls=[
                ft.Container(expand=True),
                _help_menu(
                    on_toggle_pypi_filter, show_pypi_only, on_navigate_guide, on_navigate_contribute
                ),
                _theme_button(theme_icon, on_theme_toggle),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    desktop_header = ft.Container(
        content=desktop_row,
        col={ft.ResponsiveRowBreakpoint.XS: 0, ft.ResponsiveRowBreakpoint.MD: 12},
    )

    # --- Mobile header ---
    mobile_controls: list[ft.Control] = [
        ft.IconButton(
            icon=ft.Icons.MENU,
            icon_color=ft.Colors.ON_SURFACE,
            icon_size=24,
            on_click=lambda _: on_open_drawer() if on_open_drawer else None,
        ),
        ft.Container(expand=True),
    ]
    if show_logo:
        mobile_controls.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Image(
                            src="/images/flet.svg", width=28, height=28, fit=ft.BoxFit.CONTAIN
                        ),
                        ft.Text(
                            "Flet PKG",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE,
                        ),
                    ],
                    spacing=8,
                ),
                on_click=lambda _: on_navigate_home() if on_navigate_home else None,
                ink=True,
            )
        )
    mobile_controls.append(ft.Container(expand=True))

    mobile_header_controls: list[ft.Control] = [
        ft.Row(
            controls=[
                *mobile_controls,
                _theme_button(theme_icon, on_theme_toggle),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    ]

    # Search field on mobile (packages page only)
    if on_search:
        mobile_header_controls.append(
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.TextField(
                            value=query,
                            hint_text="Search packages",
                            on_change=lambda e: set_query(e.data or ""),
                            on_submit=handle_search_submit,
                            border_radius=25,
                            content_padding=ft.Padding(left=16, top=8, right=16, bottom=8),
                            border_color=ft.Colors.OUTLINE_VARIANT,
                            focused_border_color=ft.Colors.PRIMARY,
                            cursor_color=ft.Colors.PRIMARY,
                            text_size=14,
                            prefix_icon=ft.Icons.SEARCH,
                            suffix=ft.Container(
                                content=ft.Icon(
                                    ft.Icons.CLOSE,
                                    size=16,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                                on_click=handle_clear,
                                ink=True,
                                tooltip="Clear search",
                            )
                            if query
                            else None,
                            height=42,
                            bgcolor=ft.Colors.SURFACE_CONTAINER,
                            hint_style=ft.TextStyle(color=ft.Colors.ON_SURFACE_VARIANT),
                        ),
                        expand=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )

    mobile_header = ft.Container(
        content=ft.Column(controls=mobile_header_controls, spacing=4),
        col={ft.ResponsiveRowBreakpoint.XS: 12, ft.ResponsiveRowBreakpoint.MD: 0},
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    return ft.Container(
        content=ft.ResponsiveRow(controls=[desktop_header, mobile_header], spacing=0),
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
        padding=ft.Padding(left=12, top=6, right=12, bottom=6),
    )


def _help_menu(
    on_toggle_pypi_filter: object = None,
    show_pypi_only: bool = True,
    on_navigate_guide: object = None,
    on_navigate_contribute: object = None,
) -> ft.Control:
    return ft.PopupMenuButton(
        content=ft.Row(
            controls=[
                ft.Text("Help", color=ft.Colors.ON_SURFACE, size=13),
                ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=ft.Colors.ON_SURFACE, size=16),
            ],
            spacing=0,
        ),
        items=[
            ft.PopupMenuItem(
                content="Developer Guide",
                on_click=lambda _: on_navigate_guide() if on_navigate_guide else None,
            ),
            ft.PopupMenuItem(
                content="Support & Contribute",
                on_click=lambda _: on_navigate_contribute() if on_navigate_contribute else None,
            ),
            ft.PopupMenuItem(),  # divider
            ft.PopupMenuItem(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.CHECK_BOX
                            if not show_pypi_only
                            else ft.Icons.CHECK_BOX_OUTLINE_BLANK,
                            size=18,
                            color=ft.Colors.PRIMARY,
                        ),
                        ft.Text("Show GitHub-only packages", size=13),
                    ],
                    spacing=8,
                ),
                on_click=lambda _: on_toggle_pypi_filter() if on_toggle_pypi_filter else None,
            ),
        ],
    )


def _theme_button(icon: ft.IconDataOrControl, on_toggle: object) -> ft.Control:
    return ft.IconButton(
        icon=icon,
        icon_color=ft.Colors.PRIMARY,
        icon_size=20,
        on_click=lambda _: on_toggle() if on_toggle else None,
        tooltip="Toggle theme",
    )
