---
sidebar_position: 5
title: Contributing
description: How to contribute to the Flet PKG project
---

# Contributing

Flet PKG is open source and contributions are welcome! Here's how to get started.

## Development setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Git
- A [GitHub Personal Access Token](https://github.com/settings/tokens)

### Clone and install

```bash
git clone https://github.com/brunobrown/flet-pkg-app.git
cd flet-pkg-app

# Install all dependencies (including dev)
uv sync

# Create secrets file and add your GitHub token
cat <<EOF > .secrets.toml
[default]
GITHUB_TOKEN = "ghp_your_personal_access_token_here"
EOF
```

### Run the app

```bash
uv run flet run main.py
```

### Run in web mode

```bash
uv run flet run main.py --web --port 8001
```

## Code quality

Before submitting any changes, always run:

```bash
# Format
uv tool run ruff format

# Lint
uv tool run ruff check

# Type check
uv tool run ty check

# Unit tests
python -m pytest tests/unit/ -x -q
```

All checks must pass before a pull request can be merged.

### Code style

- **Line length**: 100 characters
- **Quote style**: double quotes
- **Python target**: 3.12+
- **Formatter/Linter**: [Ruff](https://docs.astral.sh/ruff/)
- **Type checker**: [ty](https://docs.astral.sh/ty/)

## Project structure

```
flet-pkg-app/
├── main.py                  # Application entry point
├── config.py                # Dynaconf configuration
├── settings.toml            # Public settings
├── .secrets.toml            # Sensitive settings (git-ignored)
├── src/
│   ├── core/                # Logger, constants, exceptions
│   ├── domain/              # Entities, use cases, repository ABC
│   ├── data/                # Sources, repository impl, mappers
│   ├── services/            # ApiService, CacheService, IndexService
│   ├── presentation/        # Pages, components, hooks, themes
│   └── utils/               # Formatters, helpers
├── tests/
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests (require Flet runtime)
├── assets/                  # Images, icons
└── docs/                    # This documentation site (Docusaurus)
```

See [Architecture](./architecture.md) for detailed layer descriptions.

## Pull requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Make your changes
4. Run all quality checks (format, lint, type check, tests)
5. Commit with a descriptive message
6. Open a pull request against `main`

### Commit message format

Use conventional commits:

```
feat: add package comparison feature
fix: resolve search bar clear button alignment
perf: optimize index query for large result sets
docs: update developer guide with new topics
```

## Areas for contribution

- **New features**: check `tmp/features_fase2.md` for planned features
- **Bug fixes**: report issues or fix existing ones
- **Documentation**: improve or translate docs
- **Tests**: increase test coverage
- **UI/UX**: improve the interface and user experience

## Support the project

If you find Flet PKG useful, consider:

- Giving a star on [GitHub](https://github.com/brunobrown/flet-pkg-app)
- Sharing with the Flet community on [Discord](https://discord.gg/dzWXP8SHG8)
- Contributing code, docs, or ideas