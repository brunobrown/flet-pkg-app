from dataclasses import dataclass, field
from enum import Enum


class PackageType(Enum):
    UI_CONTROL = "UI Controls"
    SERVICE = "Services"
    PYTHON_PACKAGE = "Python Package"
    OFFICIAL = "Official"


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
    homepage_url: str = ""
    issues_url: str = ""
    dependencies: list[str] = field(default_factory=list)
    has_screenshot: bool = False
    pypi_name: str = ""
    github_owner: str = ""
    github_repo: str = ""

    @property
    def pip_install_command(self) -> str:
        name = self.pypi_name or self.name
        return f"pip install {name}"

    @property
    def display_stars(self) -> str:
        if self.stars >= 1_000_000:
            return f"{self.stars / 1_000_000:.1f}M"
        if self.stars >= 1_000:
            return f"{self.stars / 1_000:.1f}k"
        return str(self.stars)

    @property
    def display_downloads(self) -> str:
        if self.downloads >= 1_000_000:
            return f"{self.downloads / 1_000_000:.2f}M"
        if self.downloads >= 1_000:
            return f"{self.downloads / 1_000:.1f}k"
        return str(self.downloads)
