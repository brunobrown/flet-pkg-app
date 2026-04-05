---
sidebar_position: 4
title: API Reference
description: Data sources and endpoints used by Flet PKG
---

# API Reference

Flet PKG aggregates data from three external sources. This page documents how each source is used.

## GitHub API

**Base URL**: `https://api.github.com`

Used for package discovery, repository metadata, and README/changelog content.

### Endpoints used

| Endpoint | Purpose |
|---|---|
| `GET /search/repositories?q=topic:flet` | Discover community packages |
| `GET /repos/{owner}/{repo}` | Repository metadata (stars, description, license) |
| `GET /repos/{owner}/{repo}/readme` | Package README content |
| `GET /repos/{owner}/{repo}/contents/CHANGELOG.md` | Changelog content |
| `GET /repos/{owner}/{repo}/contents/{path}` | Official packages from flet-dev/flet monorepo |
| `GET /repos/{owner}/{repo}/topics` | Repository topics |

### Rate limits

- **Authenticated**: 5,000 requests/hour (requires `GITHUB_TOKEN`)
- **Unauthenticated**: 60 requests/hour (insufficient for production)

A GitHub Personal Access Token is required. Configure it in `.secrets.toml`.

### Concurrency

GitHub requests are limited to `GITHUB_MAX_CONCURRENT` (default: 10) parallel requests.

## PyPI API

**Base URL**: `https://pypi.org`

Used to verify package existence, fetch versions, and retrieve package metadata.

### Endpoints used

| Endpoint | Purpose |
|---|---|
| `GET /pypi/{package_name}/json` | Package info, version, dependencies, license |

### Rate limits

PyPI has no official rate limit, but Flet PKG respects reasonable concurrency to avoid abuse.

## ClickHouse (PyPI download stats)

**Base URL**: `https://sql-clickhouse.clickhouse.com`

Used to fetch download statistics. This is the same BigQuery dataset used by [pepy.tech](https://pepy.tech), exposed via ClickHouse's public SQL interface.

### Query

```sql
SELECT project, count() as downloads
FROM pypi.pypi_downloads
WHERE project IN (...)
  AND date >= today() - 30
GROUP BY project
```

### Advantages over pypistats.org

- **Batch queries**: fetch downloads for all packages in a single request
- **No rate limiting**: public demo account with read-only access
- **Fast**: ClickHouse is optimized for analytical queries

### Configuration

| Setting | Default | Description |
|---|---|---|
| `CLICKHOUSE_URL` | `https://sql-clickhouse.clickhouse.com` | ClickHouse endpoint |
| `CLICKHOUSE_USER` | `demo` | Public read-only user |
| `CLICKHOUSE_PASSWORD` | _(empty)_ | No password for public access |

## Caching

All external API responses are cached in-memory to minimize redundant requests.

| Setting | Default | Description |
|---|---|---|
| `CACHE_TTL_SECONDS` | 300 (5 min) | General cache TTL |
| `CACHE_TTL_DOWNLOADS` | 86400 (24h) | Download stats cache TTL |
| `CACHE_TTL_DISCOVERY` | 86400 (24h) | Package discovery cache TTL |
| `CACHE_MAX_ENTRIES` | 10000 | Max LRU cache entries |

## Index

The in-memory index is built at startup and refreshed periodically.

| Setting | Default | Description |
|---|---|---|
| `INDEX_REINDEX_INTERVAL` | 3600 (1h) | Background re-index interval |
| `INDEX_MAX_GITHUB_PAGES` | 5 | Max GitHub search result pages |
| `INDEX_GITHUB_PER_PAGE` | 100 | Results per GitHub search page |
| `INDEX_DOWNLOAD_DAYS` | 30 | Download stats time window |

## Local cache (persistent)

For mobile/offline scenarios, the index is persisted to disk as JSON.

| Setting | Default | Description |
|---|---|---|
| `LOCAL_INDEX_CACHE_TTL` | 21600 (6h) | Max age before re-index is required |
| `LOCAL_INDEX_CACHE_DIR` | `.cache` | Directory for the JSON cache file |