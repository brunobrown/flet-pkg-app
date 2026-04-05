---
sidebar_position: 1
title: Getting Started
description: What is Flet PKG and how to use the platform
---

# Getting Started

**Flet PKG** is a package discovery platform for the [Flet](https://flet.dev) ecosystem — similar to [pub.dev](https://pub.dev) for Flutter.

It aggregates data from GitHub, PyPI, and ClickHouse to provide a unified view of all Flet packages and extensions available in the community.

## What you can do

- **Search** packages by name, description, or topic
- **Filter** by type (UI Controls, Services), category, or PyPI availability
- **Sort** by stars, downloads, trending, recently updated, or newest
- **Explore** package details: README, changelog, dependencies, download stats
- **Discover** verified and new packages through visual badges

## Access the platform

### Web

Visit [flet-pkg-app.onrender.com](https://flet-pkg-app.onrender.com) — no installation required.

### Android (coming soon)

A mobile version with offline support via local cache is in development.

## How it works

Flet PKG builds an **in-memory index** at startup by fetching data from multiple sources:

1. **GitHub** — discovers repositories with Flet-related topics (`flet`, `fletPackage`, etc.)
2. **PyPI** — verifies package existence, fetches versions and metadata
3. **ClickHouse** — retrieves download statistics (same BigQuery source as pepy.tech)

All user queries (search, filter, sort, pagination) are resolved against this in-memory index — **zero HTTP requests** per user interaction. The index is refreshed every hour in background.

## Running locally

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (fast Python package manager)
- A [GitHub Personal Access Token](https://github.com/settings/tokens) (for API access)

### Setup

```bash
# Clone the repository
git clone https://github.com/brunobrown/flet-pkg-app.git
cd flet-pkg-app

# Install dependencies
uv sync

# Create secrets file and add your GitHub token
cat <<EOF > .secrets.toml
[default]
GITHUB_TOKEN = "ghp_your_personal_access_token_here"
EOF

# Run the app
uv run flet run main.py
```

### Configuration

Public settings are in `settings.toml`. Sensitive values (API tokens) go in `.secrets.toml` which is git-ignored.

Environment variable overrides use the prefix `SET_VAR_DYNACONF_`, for example:

```bash
SET_VAR_DYNACONF_GITHUB_TOKEN=ghp_xxx uv run flet run main.py
```

See [Architecture](./architecture.md) for details on configuration management.