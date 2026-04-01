"""URL building utilities."""


def github_profile_url(name: str) -> str:
    """Map publisher name to GitHub profile URL."""
    if name == "flet.dev":
        return "https://github.com/flet-dev"
    return f"https://github.com/{name}"
