"""Google AdMob integration — banner ads for mobile platforms."""

import logging

import flet as ft
from flet.utils import is_mobile

from config import settings

logger = logging.getLogger(__name__)

# Ad unit IDs per platform (from settings.toml)
_BANNER_UNIT_ID = {
    "android": settings.get("ADS_BANNER", {}).get("android", ""),
    "ios": settings.get("ADS_BANNER", {}).get("ios", ""),
}


def _get_platform_key(page: ft.Page) -> str:
    """Return 'android' or 'ios' based on the current page platform."""
    if page.platform == ft.PagePlatform.IOS:
        return "ios"
    return "android"


def is_ads_supported() -> bool:
    """Check if ads are supported on the current platform."""
    return is_mobile()


def create_banner_ad(page: ft.Page, on_error=None) -> ft.Control | None:
    """Create a BannerAd for the current platform. Returns None on non-mobile."""
    if not is_ads_supported():
        return None

    from flet_ads import BannerAd

    platform = _get_platform_key(page)
    unit_id = _BANNER_UNIT_ID.get(platform, "")
    if not unit_id:
        logger.warning("No banner ad unit ID for platform: %s", platform)
        return None

    return BannerAd(
        unit_id=unit_id,
        width=320,
        height=50,
        on_error=on_error or (lambda e: logger.warning("Banner ad error: %s", e.data)),
    )
