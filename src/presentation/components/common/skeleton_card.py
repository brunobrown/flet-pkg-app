"""Skeleton loading cards — placeholder that mirrors PackageCard structure.

Uses opacity pulsing via on_animation_end chaining (no re-render loops).
"""

import flet as ft


def _bar(width: float, height: float = 14) -> ft.Control:
    """Skeleton placeholder bar."""
    return ft.Container(
        width=width,
        height=height,
        border_radius=4,
        bgcolor=ft.Colors.OUTLINE_VARIANT,
    )


@ft.component
def SkeletonCard() -> ft.Control:
    """Skeleton that mirrors PackageCard layout with pulse animation."""
    opacity, set_opacity = ft.use_state(0.25)

    # Kick off the first animation after mount
    def _start_pulse():
        set_opacity(0.7)

    ft.use_effect(_start_pulse, [])

    def _on_animation_end(_e):
        set_opacity(0.25 if opacity >= 0.5 else 0.7)

    return ft.Container(
        content=ft.Column(
            controls=[
                # Header row: name placeholder + stat placeholders
                ft.Row(
                    controls=[
                        _bar(180, 20),
                        ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[_bar(40, 16), _bar(40, 10)],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=4,
                                ),
                                ft.Column(
                                    controls=[_bar(40, 16), _bar(60, 10)],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=4,
                                ),
                            ],
                            spacing=16,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                # Description lines
                _bar(500, 14),
                _bar(350, 14),
                # Footer: version, date, publisher
                ft.Row(
                    controls=[_bar(60, 12), _bar(80, 12), _bar(100, 12)],
                    spacing=12,
                ),
            ],
            spacing=12,
        ),
        height=180,
        padding=16,
        border_radius=8,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
        opacity=opacity,
        animate_opacity=ft.Animation(800, ft.AnimationCurve.EASE_IN_OUT),
        on_animation_end=_on_animation_end,
    )


@ft.component
def SkeletonCardList(count: int = 10) -> ft.Control:
    """Grid of skeleton cards for loading state."""
    return ft.ResponsiveRow(
        controls=[
            ft.Container(
                content=SkeletonCard(),
                col={
                    ft.ResponsiveRowBreakpoint.XS: 12,
                    ft.ResponsiveRowBreakpoint.SM: 6,
                    ft.ResponsiveRowBreakpoint.LG: 4,
                },
            )
            for _ in range(count)
        ],
        spacing=10,
        run_spacing=10,
    )
