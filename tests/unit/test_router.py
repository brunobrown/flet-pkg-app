"""Tests for app_router — route parsing and URL building."""

from src.presentation.navigation.app_router import (
    build_detail_url,
    build_navigate_url,
    build_packages_url,
    parse_route,
)


class TestParseRoute:
    def test_home_root(self) -> None:
        r = parse_route("/")
        assert r.page == "home"

    def test_home_empty(self) -> None:
        r = parse_route("")
        assert r.page == "home"

    def test_guide(self) -> None:
        r = parse_route("/guide")
        assert r.page == "guide"

    def test_packages_no_params(self) -> None:
        r = parse_route("/packages")
        assert r.page == "packages"
        assert r.query == ""
        assert r.sort == "default ranking"
        assert r.filter_type is None
        assert r.official is False
        assert r.page_num == 1

    def test_packages_with_query(self) -> None:
        r = parse_route("/packages?q=audio")
        assert r.page == "packages"
        assert r.query == "audio"

    def test_packages_with_sort(self) -> None:
        r = parse_route("/packages?sort=trending")
        assert r.sort == "trending"

    def test_packages_with_type(self) -> None:
        r = parse_route("/packages?type=services")
        assert r.filter_type == "Services"

    def test_packages_with_type_ui(self) -> None:
        r = parse_route("/packages?type=ui-controls")
        assert r.filter_type == "UI Controls"

    def test_packages_with_official(self) -> None:
        r = parse_route("/packages?official=true")
        assert r.official is True

    def test_packages_with_page(self) -> None:
        r = parse_route("/packages?page=5")
        assert r.page_num == 5

    def test_packages_all_params(self) -> None:
        r = parse_route("/packages?q=audio&sort=most+downloads&type=services&official=true&page=3")
        assert r.query == "audio"
        assert r.sort == "most downloads"
        assert r.filter_type == "Services"
        assert r.official is True
        assert r.page_num == 3

    def test_detail(self) -> None:
        r = parse_route("/packages/flet-audio")
        assert r.page == "detail"
        assert r.package_name == "flet-audio"

    def test_detail_empty_name(self) -> None:
        r = parse_route("/packages/")
        assert r.page == "packages"

    def test_unknown_route(self) -> None:
        r = parse_route("/unknown")
        assert r.page == "home"


class TestBuildPackagesUrl:
    def test_no_params(self) -> None:
        assert build_packages_url() == "/packages"

    def test_with_query(self) -> None:
        assert build_packages_url(query="audio") == "/packages?q=audio"

    def test_with_sort(self) -> None:
        url = build_packages_url(sort="trending")
        assert "sort=trending" in url

    def test_default_sort_excluded(self) -> None:
        url = build_packages_url(sort="default ranking")
        assert "sort" not in url

    def test_with_type(self) -> None:
        url = build_packages_url(filter_type="Services")
        assert "type=services" in url

    def test_with_official(self) -> None:
        url = build_packages_url(official=True)
        assert "official=true" in url

    def test_page_1_excluded(self) -> None:
        url = build_packages_url(page_num=1)
        assert "page" not in url

    def test_page_gt_1(self) -> None:
        url = build_packages_url(page_num=5)
        assert "page=5" in url

    def test_all_params(self) -> None:
        url = build_packages_url(
            query="audio", sort="trending", filter_type="UI Controls", official=True, page_num=2
        )
        assert "q=audio" in url
        assert "sort=trending" in url
        assert "type=ui-controls" in url
        assert "official=true" in url
        assert "page=2" in url


class TestBuildDetailUrl:
    def test_basic(self) -> None:
        assert build_detail_url("flet-audio") == "/packages/flet-audio"


class TestBuildNavigateUrl:
    def test_home(self) -> None:
        assert build_navigate_url("home") == "/"

    def test_guide(self) -> None:
        assert build_navigate_url("guide") == "/guide"

    def test_detail(self) -> None:
        assert build_navigate_url("detail:flet-audio") == "/packages/flet-audio"

    def test_packages_with_query(self) -> None:
        url = build_navigate_url("packages:audio")
        assert url == "/packages?q=audio"

    def test_packages_empty(self) -> None:
        assert build_navigate_url("packages") == "/packages"

    def test_packages_filtered(self) -> None:
        url = build_navigate_url("packages_filtered:trending:services:true")
        assert "sort=trending" in url
        assert "type=services" in url
        assert "official=true" in url

    def test_unknown(self) -> None:
        assert build_navigate_url("unknown") == "/"
