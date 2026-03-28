"""Developer Guide page — instructions for package authors."""

import flet as ft

from src.presentation.components.common.footer import AppFooter
from src.presentation.themes.colors import FLET_PINK

_GUIDE_CONTENT = """\
# Developer Guide

Welcome! This guide explains how to make your Flet package easily discoverable \
on **Flet PKG**.

---

## Quick Start with flet-pkg CLI

The fastest way to create a Flet extension is using \
**[flet-pkg](https://brunobrown.github.io/flet-pkg)** — a CLI tool that \
automatically generates the entire extension project from a Flutter package.

```bash
pip install flet-pkg
```

**What it does:**

1. Downloads the Flutter package source from pub.dev
2. Parses the Dart API (classes, methods, enums, streams)
3. Generates Python controls, Dart bridge code, and type mappings
4. Creates a ready-to-develop project with pyproject.toml, tests, and docs

**Examples:**

```bash
# Interactive mode — the CLI guides you step by step
flet-pkg create

# Create a Service extension from a Flutter package
flet-pkg create -t service -f shared_preferences

# Create a UI Control extension
flet-pkg create -t ui_control -f shimmer

# With AI-powered code refinement (free via Ollama)
flet-pkg create -f onesignal_flutter --ai-refine
```

The generated project comes with the correct naming conventions, GitHub topics, \
pyproject.toml metadata, and all the structure needed for automatic discovery \
on Flet PKG.

Documentation: [brunobrown.github.io/flet-pkg](https://brunobrown.github.io/flet-pkg) \
| Source: [github.com/brunobrown/flet-pkg](https://github.com/brunobrown/flet-pkg)

---

## Manual Setup

If you prefer to set up your package manually, follow the steps below.

## Naming Your Package

Use the prefix **`flet-`** in both your GitHub repository and PyPI package name. \
This is the strongest signal for automatic discovery.

- `flet-audio` ✓
- `flet-onesignal` ✓
- `my-awesome-lib` ✗ (won't be auto-discovered)

---

## GitHub Repository Setup

### Topics

Add these topics to your GitHub repository:

- **`flet`** — required for discovery
- **`fletPackage`** — marks it as a reusable package
- **`fletService`** — if your package is a Service extension
- **`fletUIControl`** — if your package is a UI Control extension
- **`fletExtension`** — general Flet extension

### Description

Include keywords like **"flet"**, **"flet extension"**, **"flet service"** or \
**"flet ui control"** in the repository description.

### README.md

A complete README is essential. Include:

- What the package does
- Installation instructions (`pip install` / `uv add`)
- Usage examples with code snippets
- Screenshots (if visual)
- Supported platforms (Android, iOS, Web, macOS, Windows, Linux)

### CHANGELOG.md

Keep a `CHANGELOG.md` in the root of your repository. It will be displayed in \
the **Changelog** tab on the package detail page.

---

## PyPI Publishing

### Package Name

Publish on PyPI with the `flet-` prefix:

```
flet-audio
flet-geolocator
flet-onesignal
```

### pyproject.toml

Include `flet` as a dependency and add keywords:

```toml
[project]
name = "flet-my-extension"
description = "A brief description mentioning Flet"
keywords = ["flet", "flet-extension", "python"]
dependencies = [
    "flet>=0.83.0",
]
```

The `keywords` field helps with search ranking, and having `flet` in \
`dependencies` confirms your package is a real Flet extension.

---

## Package Classification

Flet PKG automatically classifies packages into three types:

| Type | Keywords in name/description |
|------|------------------------------|
| **Service** | service, storage, permission, geolocation, push notification, ads |
| **UI Control** | control, widget, chart, map, video, camera, webview, animation |
| **Python Package** | Everything else |

To ensure correct classification, include relevant keywords in your package \
description or repository topics.

---

## Checklist

- [ ] Repository name starts with `flet-`
- [ ] Topics include `flet` and `fletPackage`
- [ ] Description mentions "flet"
- [ ] `README.md` with install instructions and examples
- [ ] `CHANGELOG.md` up to date
- [ ] Published on PyPI with `flet-` prefix
- [ ] `flet` in `dependencies` of `pyproject.toml`
- [ ] `keywords` field populated in `pyproject.toml`

---

## Need Help?

If your package is not appearing on Flet PKG, check that:

1. It is published on PyPI **or** has the `flet` topic on GitHub
2. The name starts with `flet-` or the description/dependencies reference `flet`
3. It is not in the excluded list (core packages like `flet`, `flet-cli`, etc.)

The index refreshes every hour. New packages may take up to 60 minutes to appear.
"""


@ft.component
def DeveloperGuidePage() -> ft.Control:
    return ft.Column(
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.MENU_BOOK, size=28, color=FLET_PINK),
                                ft.Text(
                                    "Developer Guide",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.ON_SURFACE,
                                ),
                            ],
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Text(
                            "How to publish your package on Flet PKG",
                            size=14,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                    spacing=4,
                ),
                padding=ft.Padding(left=40, top=20, right=40, bottom=12),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            ),
            ft.Container(
                content=ft.ListView(
                    controls=[
                        ft.Container(
                            content=ft.Markdown(
                                value=_GUIDE_CONTENT,
                                selectable=True,
                                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                auto_follow_links=True,
                                auto_follow_links_target=ft.UrlTarget.BLANK,
                                shrink_wrap=True,
                                fit_content=True,
                            ),
                            padding=ft.Padding(left=40, top=20, right=40, bottom=20),
                        ),
                    ],
                ),
                expand=True,
            ),
            AppFooter(),
        ],
        spacing=0,
        expand=True,
    )
