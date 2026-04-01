"""Tests for ClickHouse input sanitization — SQL injection prevention."""

import pytest

from src.data.sources.clickhouse_source import _sanitize_name


class TestSanitizeName:
    def test_valid_name(self) -> None:
        assert _sanitize_name("flet-audio") == "flet-audio"

    def test_valid_with_underscore(self) -> None:
        assert _sanitize_name("flet_audio") == "flet_audio"

    def test_valid_with_dot(self) -> None:
        assert _sanitize_name("my.package") == "my.package"

    def test_sql_injection_attempt(self) -> None:
        with pytest.raises(ValueError):
            _sanitize_name("'; DROP TABLE pypi.pypi_downloads_per_day; --")

    def test_semicolon(self) -> None:
        with pytest.raises(ValueError):
            _sanitize_name("flet;evil")

    def test_quote(self) -> None:
        with pytest.raises(ValueError):
            _sanitize_name("flet'evil")

    def test_space(self) -> None:
        with pytest.raises(ValueError):
            _sanitize_name("flet evil")

    def test_empty_string(self) -> None:
        with pytest.raises(ValueError):
            _sanitize_name("")

    def test_parentheses(self) -> None:
        with pytest.raises(ValueError):
            _sanitize_name("flet()")
