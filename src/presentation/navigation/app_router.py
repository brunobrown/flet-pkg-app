"""Centralized route definitions and route parsing for the application."""

from dataclasses import dataclass

# Route constants
ROUTE_HOME = "/"
ROUTE_PACKAGES = "/packages"
ROUTE_PACKAGE_DETAIL = "/packages/{name}"


@dataclass(frozen=True)
class ParsedRoute:
    path: str
    package_name: str = ""
    search_query: str = ""

    @property
    def is_home(self) -> bool:
        return self.path == ROUTE_HOME or self.path == ""

    @property
    def is_packages(self) -> bool:
        return self.path == ROUTE_PACKAGES

    @property
    def is_package_detail(self) -> bool:
        return bool(self.package_name)


def parse_route(route: str) -> ParsedRoute:
    """Parse a raw URL route into a structured ParsedRoute."""
    if not route or route == "/":
        return ParsedRoute(path=ROUTE_HOME)

    if route.startswith("/packages/"):
        pkg_name = route.split("/packages/")[1].split("?")[0]
        return ParsedRoute(
            path=ROUTE_PACKAGE_DETAIL,
            package_name=pkg_name,
        )

    if route.startswith("/packages"):
        query = ""
        if "?q=" in route:
            query = route.split("?q=")[1]
        return ParsedRoute(
            path=ROUTE_PACKAGES,
            search_query=query,
        )

    return ParsedRoute(path=ROUTE_HOME)


def build_packages_route(query: str = "") -> str:
    """Build the packages list route, optionally with a search query."""
    if query:
        return f"{ROUTE_PACKAGES}?q={query}"
    return ROUTE_PACKAGES


def build_detail_route(package_name: str) -> str:
    """Build the package detail route for a given package name."""
    return f"/packages/{package_name}"
