"""Tests for package discovery — classify_by_summary, is_flet_dependency, is_flet_related."""

from src.data.sources.package_discovery import classify_by_summary, is_flet_dependency
from src.domain.entities.package import PackageType


class TestClassifyBySummary:
    def test_service_by_keyword(self) -> None:
        assert (
            classify_by_summary("A storage service for Flet", "flet-storage") == PackageType.SERVICE
        )

    def test_service_by_name(self) -> None:
        assert classify_by_summary("", "flet-geolocator") == PackageType.SERVICE

    def test_ui_control_by_keyword(self) -> None:
        assert (
            classify_by_summary("A chart widget for Flet", "flet-charts") == PackageType.UI_CONTROL
        )

    def test_ui_control_by_name(self) -> None:
        assert classify_by_summary("", "flet-webview") == PackageType.UI_CONTROL

    def test_python_package_default(self) -> None:
        assert classify_by_summary("A utility library", "flet-utils") == PackageType.PYTHON_PACKAGE

    def test_case_insensitive(self) -> None:
        assert classify_by_summary("CAMERA integration", "my-cam") == PackageType.UI_CONTROL


class TestIsFletDependency:
    def test_flet_in_requires(self) -> None:
        assert is_flet_dependency(["flet>=0.20", "httpx"]) is True

    def test_flet_with_extras(self) -> None:
        assert is_flet_dependency(["flet[all]>=0.20"]) is True

    def test_flet_exact(self) -> None:
        assert is_flet_dependency(["flet"]) is True

    def test_flet_with_version(self) -> None:
        assert is_flet_dependency(["flet>=0.80.0"]) is True

    def test_flet_with_env_marker(self) -> None:
        assert is_flet_dependency(['flet; python_version >= "3.8"']) is True

    def test_no_flet(self) -> None:
        assert is_flet_dependency(["requests", "httpx"]) is False

    def test_none_input(self) -> None:
        assert is_flet_dependency(None) is False

    def test_empty_list(self) -> None:
        assert is_flet_dependency([]) is False

    def test_flet_prefixed_not_flet(self) -> None:
        # "flet-audio" depends on flet, but the dep name is "flet-audio", not "flet"
        assert is_flet_dependency(["flet-audio>=0.1"]) is False
