---
sidebar_position: 3
title: Developer Guide
description: How to publish packages and optimize visibility on Flet PKG
---

# Developer Guide

This guide explains how to publish Flet packages and extensions so they are automatically discovered and properly displayed on Flet PKG.

## How packages are discovered

Flet PKG discovers packages through two channels:

1. **GitHub search**: repositories with Flet-related topics
2. **Official packages**: from the [flet-dev/flet](https://github.com/flet-dev/flet) monorepo (`sdk/python/packages/`)

To ensure your package is found, follow the guidelines below.

## Repository setup

### Naming convention

Name your repository with the `flet-` prefix:

```
flet-audio
flet-onesignal
flet-map
flet-lottie
```

### GitHub topics

Add these topics to your repository (Settings > Topics):

- `flet` — required for discovery
- `fletPackage` — marks it as a Flet package
- One of:
  - `fletUIControl` — for UI controls (widgets, charts, maps, etc.)
  - `fletService` — for services (storage, permissions, push notifications, etc.)
  - `fletExtension` — generic extension

Additional relevant topics help with search and categorization (e.g., `audio`, `maps`, `animation`).

### Description

Include keywords like "flet", "flet extension", "flet service", or "flet ui control" in your repository description. This helps with text search on the platform.

## PyPI publishing

### Package name

Use the `flet-` prefix for your PyPI package name:

```toml
# pyproject.toml
[project]
name = "flet-audio"
```

### Keywords

Include relevant keywords for better discoverability:

```toml
[project]
keywords = ["flet", "flet-extension", "audio", "music", "player"]
```

### Dependencies

Include `flet` as a dependency:

```toml
[project]
dependencies = [
    "flet>=0.84.0",
]
```

## Quality badges

### Verified badge

Packages automatically receive a "Verified" badge when they meet these criteria:

- Published on PyPI (has a version)
- 100+ downloads in the last month
- Updated within the last 6 months
- Has a license defined
- Has a meaningful description (30+ characters)
- Has at least one topic or keyword

### New badge

Packages created within the last 30 days receive a "New" badge automatically.

## README and Changelog

### README

A complete `README.md` is displayed on the package detail page. Include:

- Brief description of what the package does
- Installation instructions (`pip install flet-yourpackage`)
- Usage examples with code snippets
- Screenshots or GIFs showing the package in action
- Link to documentation (if available)

### Changelog

Maintain a `CHANGELOG.md` in your repository root. It is displayed in the "Changelog" tab of the detail page.

## Example `pyproject.toml`

```toml
[project]
name = "flet-audio"
version = "0.1.0"
description = "Audio playback and recording extension for Flet"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
keywords = ["flet", "flet-extension", "audio", "music", "player"]
dependencies = [
    "flet>=0.84.0",
]

[project.urls]
Homepage = "https://github.com/youruser/flet-audio"
Repository = "https://github.com/youruser/flet-audio"
```

## Checklist

- [ ] Repository name starts with `flet-`
- [ ] Topics include `flet` and `fletPackage`
- [ ] Topic indicates type: `fletUIControl` or `fletService`
- [ ] Description mentions "flet"
- [ ] Published on PyPI with `flet-` prefix
- [ ] `keywords` defined in `pyproject.toml`
- [ ] `flet` listed as dependency
- [ ] `README.md` with examples and screenshots
- [ ] `CHANGELOG.md` maintained
- [ ] License defined