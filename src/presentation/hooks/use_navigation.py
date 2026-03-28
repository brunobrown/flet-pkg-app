"""Hook that provides navigation utilities to declarative components."""

from src.presentation.navigation.app_router import ParsedRoute, parse_route


def get_current_route(route: str) -> ParsedRoute:
    """Parse the current page route into a structured object."""
    return parse_route(route)
