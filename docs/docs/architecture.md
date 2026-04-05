---
sidebar_position: 2
title: Architecture
description: Clean Architecture overview, layers, and data flow
---

# Architecture

Flet PKG follows **Clean Architecture** principles with clearly separated layers. The codebase is organized to keep business logic independent of UI framework and external data sources.

## Layer diagram

```
┌─────────────────────────────────────────────┐
│              Presentation                   │
│   pages / components / hooks / themes       │
│         (Flet declarative mode)             │
├─────────────────────────────────────────────┤
│              Domain                         │
│   entities / use cases / repository (ABC)   │
├─────────────────────────────────────────────┤
│              Data                           │
│   sources (GitHub, PyPI, ClickHouse)        │
│   repositories (impl) / models (mappers)    │
├─────────────────────────────────────────────┤
│              Services                       │
│   ApiService / CacheService                 │
│   PackageIndexService / LocalIndexCache     │
└─────────────────────────────────────────────┘
```

## Layers

### Domain (`src/domain/`)

Pure Python — no framework imports.

- **Entities**: `Package`, `PackageType`, `SortOption` — the core data models
- **Use Cases**: `SearchPackages`, `GetPackageDetail`, `GetHomeData`, `StarPackage`
- **Repositories**: abstract base class `PackageRepository` defining the contract

### Data (`src/data/`)

Implements the domain contracts and handles external communication.

- **Sources**: HTTP clients for GitHub API, PyPI API, ClickHouse, and the package discovery engine
- **Repositories**: `PackageRepositoryImpl` — orchestrates sources to fulfill domain use cases
- **Models/Mappers**: transform raw API responses into domain entities

### Presentation (`src/presentation/`)

Flet 0.84+ declarative mode with `@ft.component`, `@ft.observable`, `ft.use_state`, and `ft.use_context`.

- **Pages**: `PackagesPage`, `PackageDetailPage`, `ContributePage`
- **Components**: reusable UI elements (cards, header, search bar, footer)
- **Hooks**: `use_packages` — connects components to the application state
- **State Management**: `AppState` + `PackagesState` via `ft.Observable`, shared through `AppCtx` (context provider)
- **Navigation**: `NavigationService` with time-based dedup and route validation
- **Themes**: light/dark theme definitions and color constants

### Services (`src/services/`)

Cross-cutting infrastructure.

- **`ApiService`**: factory that wires all dependencies (composition root for data layer)
- **`PackageIndexService`**: in-memory index with query engine, background re-indexing, and local cache integration
- **`CacheService`**: LRU in-memory cache with TTL
- **`LocalIndexCache`**: persistent JSON cache on disk (stale-while-revalidate pattern)

## Data flow

### Startup

```
main.py
  └─ ApiService()              # wires all dependencies
      └─ PackageIndexService.start()
          ├─ LocalIndexCache.load()   # instant from disk (if fresh)
          │   └─ _ready.set()         # UI can render immediately
          └─ build_index()            # background re-index
              ├─ GitHub API           # discover packages
              ├─ PyPI API             # verify + enrich versions
              ├─ ClickHouse           # download stats
              └─ LocalIndexCache.save()  # persist for next startup
```

### User query

```
User types in search bar
  └─ use_packages hook
      └─ PackageIndexService.query()   # pure in-memory, zero HTTP
          ├─ filter (text, type, category, pypi_only)
          ├─ sort (stars, downloads, trending, etc.)
          └─ paginate → return (packages[], total)
```

### Package detail

```
User clicks package card
  └─ NavigationService.navigate("/package/name")
      └─ _load_detail()
          └─ PackageRepositoryImpl.get_package()
              ├─ index lookup (cached metadata)
              ├─ GitHub API (README, topics)
              ├─ PyPI API (dependencies, full metadata)
              └─ ClickHouse (download stats)
```

## Configuration

Configuration is managed by [Dynaconf](https://www.dynaconf.com/) with two files:

| File | Purpose | Git tracked |
|---|---|---|
| `settings.toml` | Public settings (API URLs, cache TTLs, UI options) | Yes |
| `.secrets.toml` | Sensitive values (API tokens) | No (git-ignored) |

Environment variables with prefix `SET_VAR_DYNACONF_` override any setting.

## Key patterns

- **Singleton `ApiService`**: shared across all sessions (created once in `main.py`)
- **Stale-while-revalidate**: local JSON cache serves instant data on startup, re-indexes in background
- **Scheduler crash guard**: `_patch_session()` protects against Flet's `__updates_scheduler` crash on stale contexts
- **Time-based navigation dedup**: prevents duplicate navigations within a 2-second window