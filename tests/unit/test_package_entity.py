from src.domain.entities.package import Package


class TestPackage:
    def test_pip_install_command(self) -> None:
        pkg = Package(name="flet-map", pypi_name="flet-map")
        assert pkg.pip_install_command == "pip install flet-map"

    def test_pip_install_uses_pypi_name(self) -> None:
        pkg = Package(name="flet_map", pypi_name="flet-map")
        assert pkg.pip_install_command == "pip install flet-map"

    def test_display_stars_small(self) -> None:
        pkg = Package(name="test", stars=42)
        assert pkg.display_stars == "42"

    def test_display_stars_thousands(self) -> None:
        pkg = Package(name="test", stars=1500)
        assert pkg.display_stars == "1.5k"

    def test_display_downloads_millions(self) -> None:
        pkg = Package(name="test", downloads=2_500_000)
        assert pkg.display_downloads == "2.50M"
