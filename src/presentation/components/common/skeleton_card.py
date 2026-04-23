"""Skeleton loading cards — placeholder that mirrors PackageCardGrid structure.

Uses opacity pulsing via on_animation_end chaining (no re-render loops).
"""

import flet as ft


def _bar(width: float | None, height: float = 14, expand: bool = False) -> ft.Control:
    """Skeleton placeholder bar."""
    return ft.Container(
        width=width,
        height=height,
        border_radius=4,
        bgcolor=ft.Colors.OUTLINE_VARIANT,
        expand=expand,
    )


@ft.component
def SkeletonCard() -> ft.Control:
    """Skeleton that mirrors PackageCardGrid layout with pulse animation."""
    opacity, set_opacity = ft.use_state(0.25)

    _page = ft.context.page
    compact = _page.width is not None and _page.width < 600

    def _start_pulse():
        set_opacity(0.7)

    ft.use_effect(_start_pulse, [])

    def _on_animation_end(_e):
        set_opacity(0.25 if opacity >= 0.5 else 0.7)

    card_controls: list[ft.Control] = [
        # Name row
        _bar(None, 16, expand=True),
        # Description lines (2 lines in full mode, 1 in compact)
        _bar(None, 12, expand=True),
        *([] if compact else [_bar(None, 12, expand=True)]),
        # Stats row (stars, downloads)
        ft.Row(
            controls=[_bar(40, 12), _bar(50, 12)],
            spacing=12,
        ),
    ]

    # Version/publisher row: hidden in compact mode (matches PackageCardGrid)
    if not compact:
        card_controls.append(
            ft.Row(
                controls=[_bar(30, 10), _bar(50, 10), _bar(60, 10)],
                spacing=8,
            ),
        )

    return ft.Container(
        content=ft.Column(controls=card_controls, spacing=6),
        padding=12 if compact else 16,
        border_radius=8,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
        width=200,
        height=150 if compact else 200,
        opacity=opacity,
        animate_opacity=ft.Animation(800, ft.AnimationCurve.EASE_IN_OUT),
        on_animation_end=_on_animation_end,
    )


@ft.component
def SkeletonCardList(count: int = 10) -> ft.Control:
    """Grid of skeleton cards for loading state — matches PackageCardGrid breakpoints."""
    return ft.ResponsiveRow(
        controls=[
            ft.Container(
                content=SkeletonCard(),
                col={
                    ft.ResponsiveRowBreakpoint.XS: 6,
                    ft.ResponsiveRowBreakpoint.SM: 6,
                    ft.ResponsiveRowBreakpoint.LG: 4,
                },
            )
            for _ in range(count)
        ],
        spacing=10,
        run_spacing=10,
    )
