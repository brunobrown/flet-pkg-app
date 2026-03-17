"""Input validators for the application."""

import re


def is_valid_package_name(name: str) -> bool:
    """Check if a string is a valid Python package name."""
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9._-]*$", name))


def is_valid_github_repo(repo: str) -> bool:
    """Check if a string is a valid GitHub owner/repo format."""
    return bool(re.match(r"^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$", repo))


def sanitize_search_query(query: str) -> str:
    """Sanitize a search query to prevent injection in API calls."""
    # Remove characters that could interfere with GitHub search syntax
    sanitized = re.sub(r"[^\w\s\-_.@#]", "", query)
    return sanitized.strip()[:200]
