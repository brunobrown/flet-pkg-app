"""Centralized route definitions, parsing, and URL building."""

import re
import urllib.parse
from dataclasses import dataclass, field

from src.domain.entities.package import SortOption

_VALID_PACKAGE_NAME = re.compile(r"^[a-zA-Z0-9._-]+$")


def _safe_int(value: str, default: int = 0) -> int:
    """Parse string to int, returning default on failure."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


# --- Route constants ---
ROUTE_HOME = "/"
ROUTE_GUIDE = "/guide"
ROUTE_CONTRIBUTE = "/contribute"
ROUTE_PACKAGES = "/packages"

# --- Type mapping (URL param ↔ domain value) ---
TYPE_URL_TO_DOMAIN = {
    "services": "Services",
    "ui-controls": "UI Controls",
    "python": "Python Package",
}
TYPE_DOMAIN_TO_URL = {v: k for k, v in TYPE_URL_TO_DOMAIN.items()}


@dataclass(frozen=True)
class ParsedRoute:
    """Structured representation of a parsed URL route."""

    page: str = "home"
    package_name: str = ""
    query: str = ""
    sort: str = SortOption.DEFAULT
    filter_type: str | None = None
    official: bool = False
    categories: list[str] = field(default_factory=list)
    page_num: int = 1


def parse_route(route: str) -> ParsedRoute:
    """Parse a raw URL route into a structured ParsedRoute."""
    parsed = urllib.parse.urlparse(route)
    path = parsed.path.strip("/")
    params = dict(urllib.parse.parse_qsl(parsed.query))

    if path == "" or path == "/":
        return ParsedRoute(page="home")

    if path == "guide":
        return ParsedRoute(page="guide")

    if path == "contribute":
        return ParsedRoute(page="contribute")

    if path == "packages":
        cat_str = params.get("cat", "")
        categories = [c for c in cat_str.split(",") if c] if cat_str else []
        return ParsedRoute(
            page="packages",
            query=params.get("q", ""),
            sort=params.get("sort", SortOption.DEFAULT).lower(),
            filter_type=TYPE_URL_TO_DOMAIN.get(params.get("type", "")),
            official=params.get("official", "") == "true",
            categories=categories,
            page_num=_safe_int(params.get("page", "1"), default=1),
        )

    if path.startswith("packages/"):
        name = path.split("/", 1)[1]
        if name and _VALID_PACKAGE_NAME.match(name):
            return ParsedRoute(page="detail", package_name=name)
        return ParsedRoute(page="packages")

    return ParsedRoute(page="home")


def build_packages_url(
    query: str = "",
    sort: str = SortOption.DEFAULT,
    filter_type: str | None = None,
    official: bool = False,
    categories: list[str] | None = None,
    page_num: int = 1,
) -> str:
    """Build /packages URL from explicit params."""
    qparams: dict[str, str] = {}
    if query:
        qparams["q"] = query
    if sort and sort != SortOption.DEFAULT:
        qparams["sort"] = sort
    if filter_type:
        type_key = TYPE_DOMAIN_TO_URL.get(filter_type, "")
        if type_key:
            qparams["type"] = type_key
    if categories:
        qparams["cat"] = ",".join(categories)
    if official:
        qparams["official"] = "true"
    if page_num > 1:
        qparams["page"] = str(page_num)
    qs = f"?{urllib.parse.urlencode(qparams)}" if qparams else ""
    return f"/packages{qs}"


def build_detail_url(package_name: str) -> str:
    """Build /packages/<name> URL."""
    return f"/packages/{package_name}"


def build_navigate_url(target: str) -> str:
    """Convert internal navigate target string to a browser URL.

    target formats:
        "home"                                  -> /
        "guide"                                 -> /guide
        "packages:query"                        -> /packages?q=query
        "packages"                              -> /packages
        "packages_filtered:sort:type:official"  -> /packages?sort=X&type=Y&official=true
        "detail:name"                           -> /packages/name
    """
    if target == "home":
        return ROUTE_HOME
    if target == "guide":
        return ROUTE_GUIDE
    if target == "contribute":
        return ROUTE_CONTRIBUTE
    if target.startswith("detail:"):
        name = target.split(":", 1)[1]
        return build_detail_url(name)
    if target.startswith("packages_filtered:"):
        parts = target.split(":", 3)
        sort = parts[1] if len(parts) > 1 else SortOption.DEFAULT
        type_key = parts[2] if len(parts) > 2 else ""
        official_str = parts[3] if len(parts) > 3 else ""
        qparams: dict[str, str] = {}
        if sort and sort != SortOption.DEFAULT:
            qparams["sort"] = sort
        if type_key:
            qparams["type"] = type_key
        if official_str == "true":
            qparams["official"] = "true"
        qs = f"?{urllib.parse.urlencode(qparams)}" if qparams else ""
        return f"/packages{qs}"
    if target.startswith("packages"):
        query = target.split(":", 1)[1] if ":" in target else ""
        if query:
            return f"/packages?q={urllib.parse.quote(query)}"
        return ROUTE_PACKAGES
    return ROUTE_HOME
