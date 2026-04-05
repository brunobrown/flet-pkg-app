# Flet PKG
**Package discovery platform for the Flet ecosystem. Search, explore, and share Flet packages and extensions — all data aggregated from GitHub, PyPI, and ClickHouse in one place.**

![Python](https://img.shields.io/badge/python-3.12+-3776AB?logo=python&logoColor=white)
![Flet](https://img.shields.io/badge/flet-0.84.0+-00B4D8?logo=flet)
![License](https://img.shields.io/badge/license-MIT-yellow)

---

> **Like [pub.dev](https://pub.dev) for Flutter, but for Flet.**
>
> Flet PKG indexes all Flet packages from the community and official sources, enriches them with download stats and quality metadata, and serves everything from an in-memory index — zero-latency search, filter, sort, and pagination.

---

## Table of Contents

- [Features](#features)
- [Live Demo](#live-demo)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Development](#development)
- [Developer Guide](#developer-guide)
- [Buy Me a Coffee](#buy-me-a-coffee)
- [Learn More](#learn-more)
- [Flet Community](#flet-community)
- [Support](#support)
- [Contributing](#contributing)

---

## Buy Me a Coffee

If you find this project useful, please consider supporting its development:

<a href="https://www.buymeacoffee.com/brunobrown">
<img src="https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-1.svg" width="200" alt="Buy Me a Coffee">
</a>

---

## Features

- **Search** packages by name, description, topics, and keywords
- **Filter** by type (UI Controls, Services), category, PyPI availability, official only
- **Sort** by stars, downloads, trending, recently updated, or newest
- **Package detail** with README, changelog, dependencies, and download stats
- **Verified badge** — automatic quality verification based on multiple criteria
- **New badge** — highlights packages created in the last 30 days
- **Share button** — copy link and share to social networks
- **Dark/Light mode** — respects system preference, toggleable
- **Responsive layout** — adapts to desktop and mobile screens
- **Local cache** — persistent JSON cache for instant startup (stale-while-revalidate)
- **Background re-indexing** — hourly refresh without user interruption
- **Topic search** — `topic:audio` syntax for exact topic matching

---

## Live Demo

Visit the live platform: **[flet-pkg-app.onrender.com](https://flet-pkg-app.onrender.com)**

---

## Installation

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (fast Python package manager)
- A [GitHub Personal Access Token](https://github.com/settings/tokens)

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
```

---

## Quick Start

**1. Configure your GitHub token in `.secrets.toml`:**

```toml
[default]
GITHUB_TOKEN = "ghp_your_personal_access_token_here"
```

**2. Run the app:**

```bash
# Desktop mode
uv run flet run main.py

# Web mode
uv run flet run main.py --web --port 8001
```

---

## How It Works

Flet PKG builds an **in-memory index** at startup by fetching data from three sources:

```
GitHub API          PyPI API          ClickHouse
(discovery +        (versions +       (download
 metadata)           packages)         stats)
     │                  │                 │
     └──────────┬───────┘─────────────────┘
                │
        PackageIndexService
        (in-memory index)
                │
        ┌───────┴───────┐
        │  query()      │  ← zero HTTP, microseconds
        │  filter/sort  │
        │  paginate     │
        └───────────────┘
```

1. **Discovery** — finds repositories with Flet-related topics on GitHub
2. **Enrichment** — verifies PyPI existence, fetches versions and metadata
3. **Stats** — retrieves download counts from ClickHouse (same source as pepy.tech)
4. **Index** — builds in-memory list, re-indexes every hour in background
5. **Local cache** — persists to disk for instant startup on next launch

All user queries run against the in-memory index — **zero HTTP requests** per interaction.

---

## Configuration

Configuration is managed by [Dynaconf](https://www.dynaconf.com/) with two files:

| File | Purpose | Git tracked |
|---|---|---|
| `settings.toml` | Public settings (API URLs, cache TTLs, UI options) | Yes |
| `.secrets.toml` | Sensitive values (API tokens) | No |

### Key settings

| Setting | Default | Description |
|---|---|---|
| `INDEX_REINDEX_INTERVAL` | 3600 (1h) | Background re-index interval |
| `CACHE_TTL_SECONDS` | 300 (5min) | General cache TTL |
| `CACHE_TTL_DOWNLOADS` | 86400 (24h) | Download stats cache TTL |
| `LOCAL_INDEX_CACHE_TTL` | 21600 (6h) | Local JSON cache TTL |
| `NEW_PACKAGE_DAYS` | 30 | Days to show "New" badge |
| `DEFAULT_PER_PAGE` | 10 | Default pagination size |

Environment variable overrides use the prefix `SET_VAR_DYNACONF_`:

```bash
SET_VAR_DYNACONF_GITHUB_TOKEN=ghp_xxx uv run flet run main.py
```

---

## Project Structure

```
flet-pkg-app/
├── main.py                  # Application entry point
├── config.py                # Dynaconf configuration
├── settings.toml            # Public settings
├── .secrets.toml            # Sensitive settings (git-ignored)
├── src/
│   ├── core/                # Logger, constants, exceptions
│   ├── domain/              # Entities, use cases, repository ABC
│   │   ├── entities/        # Package, PackageType, SortOption
│   │   ├── usecases/        # SearchPackages, GetPackageDetail, etc.
│   │   └── repositories/    # Abstract PackageRepository
│   ├── data/                # External data sources and implementations
│   │   ├── sources/         # GitHub, PyPI, ClickHouse, PackageDiscovery
│   │   ├── repositories/    # PackageRepositoryImpl
│   │   └── models/          # Mappers (API response → domain entity)
│   ├── services/            # ApiService, CacheService, IndexService
│   ├── presentation/        # Flet UI (declarative mode)
│   │   ├── pages/           # PackagesPage, PackageDetailPage, ContributePage
│   │   ├── components/      # Header, SearchBar, PackageCard, Footer
│   │   ├── hooks/           # use_packages (state → UI bridge)
│   │   ├── state_management/ # AppState, PackagesState, AppContext
│   │   ├── navigation/      # NavigationService, AppRouter
│   │   └── themes/          # Light/Dark themes, colors
│   └── utils/               # Formatters, helpers
├── tests/
│   ├── unit/                # 124 unit tests
│   └── integration/         # Integration tests (require Flet runtime)
├── assets/                  # Images and icons
├── docs/                    # Documentation site (Docusaurus)
├── Dockerfile               # Production container
└── render.yaml              # Render deployment blueprint
```

---

## Development

```bash
# Clone and install
git clone https://github.com/brunobrown/flet-pkg-app.git
cd flet-pkg-app
uv sync

# Run the app
uv run flet run main.py

# Format
uv tool run ruff format

# Lint
uv tool run ruff check

# Type check
uv tool run ty check

# Unit tests
python -m pytest tests/unit/ -x -q
```

### Tech Stack

| Tool | Purpose |
|---|---|
| **Python 3.12+** | Runtime |
| **Flet 0.84+** | UI framework (declarative mode) |
| **httpx** | Async HTTP client |
| **Dynaconf** | Configuration management |
| **Ruff** | Formatting and linting |
| **ty** | Type checking |
| **pytest** | Testing |
| **Docker** | Production deployment |
| **Docusaurus** | Documentation site |

---

## Developer Guide

Want your package to appear on Flet PKG? Follow these steps:

1. Name your repository and PyPI package with the `flet-` prefix
2. Add topics `flet` and `fletPackage` on GitHub
3. Include `flet` as a dependency in `pyproject.toml`
4. Add `keywords` in `pyproject.toml`
5. Write a complete `README.md` with examples
6. Maintain a `CHANGELOG.md`

The index refreshes every hour. New packages may take up to 60 minutes to appear.

For the full guide, see the [Developer Guide](https://brunobrown.github.io/flet-pkg-app/docs/developer-guide) in the documentation.

---

## Learn more
* [Documentation](https://brunobrown.github.io/flet-pkg-app)

## Flet Community

Join the community to contribute or get help:

* [Discussions](https://github.com/flet-dev/flet/discussions)
* [Discord](https://discord.gg/dzWXP8SHG8)
* [X (Twitter)](https://twitter.com/fletdev)
* [Bluesky](https://bsky.app/profile/fletdev.bsky.social)
* [Email us](mailto:hello@flet.dev)

## Support

If you like this project, please give it a [GitHub star](https://github.com/brunobrown/flet-pkg-app) ⭐

---

## Contributing

Contributions and feedback are welcome!

1. Fork the repository
2. Create a feature branch
3. Run all quality checks (`ruff format`, `ruff check`, `ty check`, `pytest`)
4. Submit a pull request with detailed explanation

For feedback, [open an issue](https://github.com/brunobrown/flet-pkg-app/issues) with your suggestions.

---

<p align="center"><img src="https://github.com/user-attachments/assets/431aa05f-5fbc-4daa-9689-b9723583e25a" width="50%"></p>
<p align="center"><a href="https://www.bible.com/bible/116/PRO.16.NLT"> Commit your work to the LORD, and your plans will succeed. Proverbs 16:3</a></p>