from dataclasses import dataclass, field
from enum import Enum


class PackageType(Enum):
    UI_CONTROL = "UI Controls"
    SERVICE = "Services"
    PYTHON_PACKAGE = "Python Package"


class SortOption:
    """Sort option constants — single source of truth."""

    DEFAULT = "default ranking"
    MOST_STARS = "most stars"
    MOST_DOWNLOADS = "most downloads"
    RECENTLY_UPDATED = "recently updated"
    NEWEST = "newest package"
    TRENDING = "trending"


@dataclass
class Package:
    name: str
    description: str = ""
    version: str = ""
    stars: int = 0
    downloads: int = 0
    license: str = ""
    topics: list[str] = field(default_factory=list)
    repository_url: str = ""
    documentation_url: str = ""
    readme: str = ""
    changelog: str = ""
    publisher: str = ""
    updated_at: str = ""
    created_at: str = ""
    forks: int = 0
    package_type: PackageType = PackageType.PYTHON_PACKAGE
    is_official: bool = False
    is_verified: bool = False
    is_new: bool = False
    homepage_url: str = ""
    issues_url: str = ""
    dependencies: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    pypi_name: str = ""
    github_owner: str = ""
    github_repo: str = ""

    @property
    def pip_install_command(self) -> str:
        name = self.pypi_name or self.name
        return f"pip install {name}"

    @property
    def display_stars(self) -> str:
        from src.utils.formatters import format_number

        return format_number(self.stars)

    @property
    def display_downloads(self) -> str:
        from src.utils.formatters import format_number

        return format_number(self.downloads)
