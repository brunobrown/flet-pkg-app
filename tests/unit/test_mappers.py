"""Tests for data model mappers — GitHub and PyPI to Package conversion."""

from src.data.models.mappers import github_repo_to_package, pypi_info_to_package
from src.domain.entities.package import PackageType


class TestGithubRepoToPackage:
    def test_basic_mapping(self) -> None:
        repo = {
            "name": "flet-audio",
            "full_name": "flet-dev/flet-audio",
            "owner": {"login": "flet-dev"},
            "description": "Audio service",
            "stargazers_count": 150,
            "forks_count": 20,
            "html_url": "https://github.com/flet-dev/flet-audio",
            "homepage": "https://docs.flet.dev",
            "updated_at": "2025-03-01T00:00:00Z",
            "created_at": "2024-01-01T00:00:00Z",
            "license": {"spdx_id": "MIT"},
            "topics": ["flet", "audio"],
        }
        pkg = github_repo_to_package(repo)
        assert pkg.name == "flet-audio"
        assert pkg.stars == 150
        assert pkg.forks == 20
        assert pkg.license == "MIT"
        assert pkg.topics == ["flet", "audio"]
        assert pkg.github_owner == "flet-dev"
        assert pkg.github_repo == "flet-audio"
        assert pkg.is_official is True

    def test_pypi_name_empty_by_default(self) -> None:
        repo = {"name": "my-repo", "owner": {"login": "user"}, "full_name": "user/my-repo"}
        pkg = github_repo_to_package(repo)
        assert pkg.pypi_name == ""

    def test_pypi_name_explicit(self) -> None:
        repo = {"name": "my-repo", "owner": {"login": "user"}, "full_name": "user/my-repo"}
        pkg = github_repo_to_package(repo, pypi_name="my-package")
        assert pkg.pypi_name == "my-package"

    def test_service_topic(self) -> None:
        repo = {
            "name": "my-service",
            "owner": {"login": "user"},
            "full_name": "user/my-service",
            "topics": ["service", "flet"],
        }
        pkg = github_repo_to_package(repo)
        assert pkg.package_type == PackageType.SERVICE

    def test_ui_control_topic(self) -> None:
        repo = {
            "name": "my-widget",
            "owner": {"login": "user"},
            "full_name": "user/my-widget",
            "topics": ["ui-control"],
        }
        pkg = github_repo_to_package(repo)
        assert pkg.package_type == PackageType.UI_CONTROL

    def test_missing_fields(self) -> None:
        repo = {"name": "minimal", "owner": {"login": ""}, "full_name": ""}
        pkg = github_repo_to_package(repo)
        assert pkg.name == "minimal"
        assert pkg.stars == 0
        assert pkg.description == ""
        assert pkg.license == ""

    def test_null_license(self) -> None:
        repo = {"name": "test", "owner": {"login": "u"}, "full_name": "u/test", "license": None}
        pkg = github_repo_to_package(repo)
        assert pkg.license == ""

    def test_official_detection(self) -> None:
        repo = {
            "name": "flet-map",
            "owner": {"login": "flet-dev"},
            "full_name": "flet-dev/flet-map",
        }
        assert github_repo_to_package(repo).is_official is True

        repo2 = {"name": "flet-map", "owner": {"login": "someone"}, "full_name": "someone/flet-map"}
        assert github_repo_to_package(repo2).is_official is False


class TestPypiInfoToPackage:
    def test_basic_mapping(self) -> None:
        data = {
            "info": {
                "name": "flet-audio",
                "summary": "Audio service for Flet",
                "version": "0.1.0",
                "author": "flet-dev",
                "license": "MIT",
                "project_urls": {
                    "Repository": "https://github.com/flet-dev/flet-audio",
                    "Documentation": "https://docs.flet.dev",
                },
                "requires_dist": ["flet>=0.80"],
            },
            "urls": [{"upload_time_iso_8601": "2025-03-01T12:00:00Z"}],
        }
        pkg = pypi_info_to_package(data)
        assert pkg.name == "flet-audio"
        assert pkg.version == "0.1.0"
        assert pkg.pypi_name == "flet-audio"
        assert pkg.github_owner == "flet-dev"
        assert pkg.github_repo == "flet-audio"
        assert pkg.license == "MIT"
        assert pkg.dependencies == ["flet>=0.80"]

    def test_github_url_parsing(self) -> None:
        data = {
            "info": {
                "name": "test",
                "project_urls": {"Source": "https://github.com/user/repo"},
            },
        }
        pkg = pypi_info_to_package(data)
        assert pkg.github_owner == "user"
        assert pkg.github_repo == "repo"

    def test_no_github_url(self) -> None:
        data = {"info": {"name": "test", "project_urls": {"Homepage": "https://example.com"}}}
        pkg = pypi_info_to_package(data)
        assert pkg.github_owner == ""
        assert pkg.github_repo == ""

    def test_license_from_classifiers(self) -> None:
        data = {
            "info": {
                "name": "test",
                "license": "",
                "classifiers": ["License :: OSI Approved :: Apache Software License"],
            },
        }
        pkg = pypi_info_to_package(data)
        assert pkg.license == "Apache Software License"

    def test_empty_data(self) -> None:
        data = {"info": {}}
        pkg = pypi_info_to_package(data)
        assert pkg.name == ""
        assert pkg.version == ""
        assert pkg.pypi_name == ""

    def test_null_project_urls(self) -> None:
        data = {"info": {"name": "test", "project_urls": None}}
        pkg = pypi_info_to_package(data)
        assert pkg.repository_url == ""
