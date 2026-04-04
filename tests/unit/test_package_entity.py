from src.domain.entities.package import Package
from src.utils.formatters import format_number


class TestPackage:
    def test_pip_install_command(self) -> None:
        pkg = Package(name="flet-map", pypi_name="flet-map")
        assert pkg.pip_install_command == "pip install flet-map"

    def test_pip_install_uses_pypi_name(self) -> None:
        pkg = Package(name="flet_map", pypi_name="flet-map")
        assert pkg.pip_install_command == "pip install flet-map"

    def test_format_stars_small(self) -> None:
        assert format_number(42) == "42"

    def test_format_stars_thousands(self) -> None:
        assert format_number(1500) == "1.5k"

    def test_format_downloads_millions(self) -> None:
        assert format_number(2_500_000) == "2.50M"
