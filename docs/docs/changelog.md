---
sidebar_position: 6
title: Changelog
description: Version history of Flet PKG
---

# Changelog

## v0.1.0 — Initial Release

### Features

- **Package discovery**: automatic indexing from GitHub, PyPI, and ClickHouse
- **In-memory index**: zero-latency search, filter, sort, and pagination
- **Package detail page**: README, changelog, dependencies, download stats, and metadata
- **Search**: full-text search by name, description, topics, and keywords
- **Topic search**: `topic:audio` syntax for exact topic matching
- **Sort options**: default ranking, most stars, most downloads, trending, recently updated, newest
- **Filters**: package type (UI Controls, Services), categories, PyPI-only, official-only
- **Verified badge**: automatic quality verification based on multiple criteria
- **New badge**: highlights packages created within the last 30 days
- **Share button**: copy link, share to social networks
- **Developer guide**: in-app guide for package authors
- **Contribute page**: support links and social channels
- **Dark/Light mode**: respects system preference, toggleable
- **Responsive layout**: adapts to desktop and mobile screens
- **Local cache**: persistent JSON cache for instant startup (stale-while-revalidate)
- **Background re-indexing**: hourly refresh without user interruption

### Infrastructure

- **Deployment**: Docker + Render (free tier)
- **Configuration**: Dynaconf with settings.toml + .secrets.toml
- **Caching**: LRU in-memory cache with configurable TTL per resource type
- **Logging**: structured logging with per-module loggers

### Tech stack

- **Python 3.12+** with **Flet 0.84+** (declarative mode)
- **httpx** for async HTTP
- **Dynaconf** for configuration
- **Ruff** for formatting and linting
- **ty** for type checking
- **pytest** for testing