"""Local storage source for persisting favorites and cached data."""

import json
from pathlib import Path

from src.core.logger import get_logger

logger = get_logger(__name__)

DEFAULT_STORAGE_DIR = Path.home() / ".flet_pkg"


class LocalSource:
    def __init__(self, storage_dir: Path = DEFAULT_STORAGE_DIR):
        self._storage_dir = storage_dir
        self._storage_dir.mkdir(parents=True, exist_ok=True)

    def _file_path(self, key: str) -> Path:
        safe_key = key.replace("/", "_").replace("\\", "_")
        return self._storage_dir / f"{safe_key}.json"

    def get(self, key: str) -> dict | list | None:
        path = self._file_path(key)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to read local storage key %s: %s", key, e)
            return None

    def set(self, key: str, value: dict | list) -> None:
        path = self._file_path(key)
        try:
            path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        except OSError as e:
            logger.warning("Failed to write local storage key %s: %s", key, e)

    def delete(self, key: str) -> None:
        path = self._file_path(key)
        if path.exists():
            path.unlink()

    def exists(self, key: str) -> bool:
        return self._file_path(key).exists()
