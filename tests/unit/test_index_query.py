"""Tests for PackageIndexService.query() — all filter/sort/pagination combinations."""

from src.domain.entities.package import Package, PackageType
from src.services.package_index_service import PackageIndexService


def _make_pkg(
    name: str,
    pypi_name: str = "",
    stars: int = 0,
    downloads: int = 0,
    package_type: PackageType = PackageType.PYTHON_PACKAGE,
    is_official: bool = False,
    description: str = "",
    topics: list[str] | None = None,
    updated_at: str = "",
    created_at: str = "",
) -> Package:
    return Package(
        name=name,
        pypi_name=pypi_name,
        stars=stars,
        downloads=downloads,
        package_type=package_type,
        is_official=is_official,
        description=description,
        topics=topics or [],
        updated_at=updated_at,
        created_at=created_at,
    )


def _build_index() -> PackageIndexService:
    """Create an index with known test data (no external deps)."""
    index = PackageIndexService.__new__(PackageIndexService)
    index._ready = __import__("asyncio").Event()
    index._ready.set()
    index._official_names = {"flet-audio", "flet-map"}
    index._packages = [
        _make_pkg(
            "flet-audio",
            pypi_name="flet-audio",
            stars=100,
            downloads=5000,
            package_type=PackageType.SERVICE,
            is_official=True,
            description="Audio service for Flet",
            topics=["flet", "audio"],
            updated_at="2025-03-01",
            created_at="2024-01-01",
        ),
        _make_pkg(
            "flet-map",
            pypi_name="flet-map",
            stars=80,
            downloads=3000,
            package_type=PackageType.UI_CONTROL,
            is_official=True,
            description="Map control for Flet",
            topics=["flet", "map"],
            updated_at="2025-02-15",
            created_at="2024-02-01",
        ),
        _make_pkg(
            "flet-charts",
            pypi_name="flet-charts",
            stars=60,
            downloads=8000,
            package_type=PackageType.UI_CONTROL,
            is_official=True,
            description="Charts for Flet",
            updated_at="2025-01-10",
            created_at="2024-03-01",
        ),
        _make_pkg(
            "awesome-flet",
            pypi_name="awesome-flet",
            stars=50,
            downloads=1000,
            description="A cool Flet app",
            topics=["flet", "python"],
            updated_at="2025-03-10",
            created_at="2024-06-01",
        ),
        _make_pkg(
            "flet-onesignal",
            pypi_name="flet-onesignal",
            stars=30,
            downloads=500,
            package_type=PackageType.SERVICE,
            description="OneSignal push for Flet",
            updated_at="2025-02-20",
            created_at="2024-05-01",
        ),
        # GitHub-only (no pypi_name)
        _make_pkg(
            "FletSchool",
            pypi_name="",
            stars=10,
            downloads=0,
            description="A school project using Flet",
            updated_at="2025-01-01",
            created_at="2024-09-01",
        ),
        _make_pkg(
            "my-flet-app",
            pypi_name="",
            stars=5,
            downloads=0,
            description="My personal Flet app",
            updated_at="2024-12-01",
            created_at="2024-10-01",
        ),
    ]
    return index


class TestQueryDefaults:
    def test_returns_all_pypi_packages_by_default(self) -> None:
        index = _build_index()
        results, total = index.query()
        assert total == 5  # Excludes 2 GitHub-only
        assert all(p.pypi_name for p in results)

    def test_returns_all_packages_when_pypi_only_false(self) -> None:
        index = _build_index()
        results, total = index.query(pypi_only=False)
        assert total == 7


class TestPagination:
    def test_first_page(self) -> None:
        index = _build_index()
        results, total = index.query(per_page=2, page=1)
        assert len(results) == 2
        assert total == 5

    def test_second_page(self) -> None:
        index = _build_index()
        results, total = index.query(per_page=2, page=2)
        assert len(results) == 2
        assert total == 5

    def test_last_page_partial(self) -> None:
        index = _build_index()
        results, total = index.query(per_page=2, page=3)
        assert len(results) == 1
        assert total == 5

    def test_beyond_last_page(self) -> None:
        index = _build_index()
        results, total = index.query(per_page=2, page=10)
        assert len(results) == 0
        assert total == 5


class TestFilterType:
    def test_filter_services(self) -> None:
        index = _build_index()
        results, total = index.query(package_type="Services")
        assert total == 2
        assert all(p.package_type == PackageType.SERVICE for p in results)

    def test_filter_ui_controls(self) -> None:
        index = _build_index()
        results, total = index.query(package_type="UI Controls")
        assert total == 2
        assert all(p.package_type == PackageType.UI_CONTROL for p in results)

    def test_filter_python_package(self) -> None:
        index = _build_index()
        results, total = index.query(package_type="Python Package")
        # awesome-flet (pypi) only — GitHub-only excluded by pypi_only default
        assert total == 1
        assert results[0].name == "awesome-flet"


class TestFilterOfficial:
    def test_official_only(self) -> None:
        index = _build_index()
        results, total = index.query(official_only=True)
        assert total == 3
        assert all(p.is_official for p in results)


class TestTextSearch:
    def test_search_by_name(self) -> None:
        index = _build_index()
        results, total = index.query(text="audio")
        assert total == 1
        assert results[0].name == "flet-audio"

    def test_search_by_description(self) -> None:
        index = _build_index()
        results, total = index.query(text="OneSignal")
        assert total == 1
        assert results[0].name == "flet-onesignal"

    def test_search_by_topic(self) -> None:
        index = _build_index()
        results, total = index.query(text="python")
        assert total == 1
        assert results[0].name == "awesome-flet"

    def test_search_case_insensitive(self) -> None:
        index = _build_index()
        results, total = index.query(text="AUDIO")
        assert total == 1

    def test_search_no_results(self) -> None:
        index = _build_index()
        results, total = index.query(text="nonexistent")
        assert total == 0
        assert results == []

    def test_search_github_only_with_pypi_false(self) -> None:
        index = _build_index()
        results, total = index.query(text="school", pypi_only=False)
        assert total == 1
        assert results[0].name == "FletSchool"


class TestSort:
    def test_most_downloads(self) -> None:
        index = _build_index()
        results, _ = index.query(sort="most downloads", per_page=100)
        downloads = [p.downloads for p in results]
        assert downloads == sorted(downloads, reverse=True)

    def test_most_stars(self) -> None:
        index = _build_index()
        results, _ = index.query(sort="most stars", per_page=100)
        stars = [p.stars for p in results]
        assert stars == sorted(stars, reverse=True)

    def test_trending(self) -> None:
        index = _build_index()
        results, _ = index.query(sort="trending", per_page=100)
        scores = [p.stars + p.downloads for p in results]
        assert scores == sorted(scores, reverse=True)

    def test_recently_updated(self) -> None:
        index = _build_index()
        results, _ = index.query(sort="recently updated", per_page=100)
        dates = [p.updated_at for p in results]
        assert dates == sorted(dates, reverse=True)

    def test_newest_package(self) -> None:
        index = _build_index()
        results, _ = index.query(sort="newest package", per_page=100)
        dates = [p.created_at for p in results]
        assert dates == sorted(dates, reverse=True)

    def test_default_ranking_preserves_order(self) -> None:
        index = _build_index()
        results, _ = index.query(sort="default ranking", per_page=100)
        # Default order is by stars (set during build)
        stars = [p.stars for p in results]
        assert stars == sorted(stars, reverse=True)


class TestCombinedFilters:
    def test_official_services(self) -> None:
        index = _build_index()
        results, total = index.query(official_only=True, package_type="Services")
        assert total == 1
        assert results[0].name == "flet-audio"

    def test_search_with_type(self) -> None:
        index = _build_index()
        results, total = index.query(text="flet", package_type="UI Controls")
        assert total == 2

    def test_search_with_pagination(self) -> None:
        index = _build_index()
        results, total = index.query(text="audio", per_page=1, page=1)
        assert len(results) == 1
        assert total == 1
        assert results[0].name == "flet-audio"
