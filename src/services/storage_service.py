"""Storage service for persisting user favorites and preferences."""

from src.core.logger import get_logger
from src.data.sources.local_source import LocalSource

logger = get_logger(__name__)

FAVORITES_KEY = "favorites"
PREFERENCES_KEY = "preferences"


class StorageService:
    def __init__(self, local_source: LocalSource | None = None):
        self._source = local_source or LocalSource()

    # Favorites
    def get_favorites(self) -> list[str]:
        data = self._source.get(FAVORITES_KEY)
        if isinstance(data, list):
            return data
        return []

    def add_favorite(self, package_name: str) -> None:
        favorites = self.get_favorites()
        if package_name not in favorites:
            favorites.append(package_name)
            self._source.set(FAVORITES_KEY, favorites)

    def remove_favorite(self, package_name: str) -> None:
        favorites = self.get_favorites()
        if package_name in favorites:
            favorites.remove(package_name)
            self._source.set(FAVORITES_KEY, favorites)

    def is_favorite(self, package_name: str) -> bool:
        return package_name in self.get_favorites()

    # Preferences
    def get_preferences(self) -> dict:
        data = self._source.get(PREFERENCES_KEY)
        if isinstance(data, dict):
            return data
        return {}

    def set_preference(self, key: str, value: object) -> None:
        prefs = self.get_preferences()
        prefs[key] = value
        self._source.set(PREFERENCES_KEY, prefs)

    def get_preference(self, key: str, default: object = None) -> object:
        return self.get_preferences().get(key, default)
