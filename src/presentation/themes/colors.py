"""Color constants.

For theme-aware colors, use ft.Colors.* (PRIMARY, SURFACE, ON_SURFACE, etc.)
which automatically switch between dark/light via ColorScheme in app_theme.py.

Only use these constants for:
- Flet logo colors (always the same)
- Hero gradient (intentionally always dark)
- Legacy code that hasn't been migrated yet
"""

# Flet logo palette (fixed, not theme-dependent)
FLET_PINK = "#E1386B"
FLET_BLUE = "#59A3DC"
FLET_BLUE_LIGHT = "#6CB2E2"

# Hero section gradient (intentionally always dark, like pub.dev)
HERO_GRADIENT = ("#1e3a5f", "#2c5282", "#1e3a5f")
HERO_SEARCH_BG = "#232831"

# Legacy aliases — used during migration, prefer ft.Colors.* instead
DARK_BG = "#081425"
DARK_SURFACE = "#14253A"
DARK_CARD = "#232831"
DARK_HEADER = "#081425"
DARK_ACCENT = FLET_BLUE_LIGHT
DARK_DIVIDER = "#354457"
LIGHT_BG = "#f5f5f5"
