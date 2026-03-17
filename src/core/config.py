import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    github_token: str = ""
    cache_ttl: int = 300
    packages_per_page: int = 10
    app_title: str = "Flet PKG"
    app_subtitle: str = "Find the best packages for your Flet apps"

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            github_token=os.environ.get("GITHUB_TOKEN", ""),
        )
