from typing import Any

from src.domain.entities.package import Package, PackageType


def github_repo_to_package(
    repo: dict[str, Any],
    package_type: PackageType = PackageType.PYTHON_PACKAGE,
    downloads: int = 0,
    pypi_name: str = "",
) -> Package:
    owner = repo.get("owner", {}).get("login", "")
    name = repo.get("name", "")
    full_name = repo.get("full_name", "")
    topics = repo.get("topics", [])

    is_official = owner == "flet-dev"

    if "service" in topics or "services" in topics:
        pkg_type = PackageType.SERVICE
    elif "ui" in topics or "ui-control" in topics or "control" in topics:
        pkg_type = PackageType.UI_CONTROL
    else:
        pkg_type = package_type

    return Package(
        name=name,
        description=repo.get("description", "") or "",
        version="",
        stars=repo.get("stargazers_count", 0),
        downloads=downloads,
        license=(repo.get("license") or {}).get("spdx_id", ""),
        topics=topics,
        repository_url=repo.get("html_url", ""),
        documentation_url=repo.get("homepage", "") or "",
        publisher=owner,
        updated_at=repo.get("updated_at", ""),
        created_at=repo.get("created_at", ""),
        forks=repo.get("forks_count", 0),
        package_type=pkg_type,
        is_official=is_official,
        homepage_url=repo.get("homepage", "") or "",
        issues_url=f"https://github.com/{full_name}/issues",
        pypi_name=pypi_name or name,
        github_owner=owner,
        github_repo=name,
        has_screenshot=bool(repo.get("homepage")),
    )


def pypi_info_to_package(data: dict[str, Any], downloads: int = 0) -> Package:
    info = data.get("info", {})
    urls = data.get("urls", [])

    project_urls = info.get("project_urls") or {}
    repo_url = (
        project_urls.get("Repository", "")
        or project_urls.get("Source", "")
        or project_urls.get("GitHub", "")
        or project_urls.get("Homepage", "")
    )

    github_owner = ""
    github_repo = ""
    if "github.com" in repo_url:
        parts = repo_url.rstrip("/").split("/")
        if len(parts) >= 5:
            github_owner = parts[3]
            github_repo = parts[4]

    classifiers = info.get("classifiers", [])
    license_name = info.get("license", "") or ""
    if not license_name:
        for c in classifiers:
            if "License" in c:
                license_name = c.split("::")[-1].strip()
                break

    upload_time = ""
    if urls:
        upload_time = urls[0].get("upload_time_iso_8601", "")

    return Package(
        name=info.get("name", ""),
        description=info.get("summary", "") or "",
        version=info.get("version", ""),
        downloads=downloads,
        license=license_name,
        repository_url=repo_url,
        documentation_url=project_urls.get("Documentation", ""),
        publisher=info.get("author", "") or info.get("maintainer", "") or "",
        updated_at=upload_time,
        homepage_url=info.get("home_page", "") or project_urls.get("Homepage", ""),
        pypi_name=info.get("name", ""),
        github_owner=github_owner,
        github_repo=github_repo,
        dependencies=[r.split(";")[0].split(" ")[0] for r in (info.get("requires_dist") or [])],
    )
