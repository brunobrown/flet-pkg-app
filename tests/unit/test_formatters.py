from src.utils.formatters import format_date, format_number, truncate


class TestFormatNumber:
    def test_small_number(self) -> None:
        assert format_number(42) == "42"

    def test_thousands(self) -> None:
        assert format_number(1500) == "1.5k"

    def test_millions(self) -> None:
        assert format_number(2_500_000) == "2.50M"

    def test_zero(self) -> None:
        assert format_number(0) == "0"


class TestTruncate:
    def test_short_text(self) -> None:
        assert truncate("hello", 10) == "hello"

    def test_long_text(self) -> None:
        result = truncate("a" * 200, 100)
        assert len(result) == 100
        assert result.endswith("...")


class TestFormatDate:
    def test_iso_with_z_suffix(self) -> None:
        result = format_date("2024-01-15T10:00:00Z")
        assert "ago" in result or result == "just now"

    def test_iso_with_timezone(self) -> None:
        result = format_date("2024-01-15T10:00:00+00:00")
        assert "ago" in result or result == "just now"

    def test_naive_datetime(self) -> None:
        result = format_date("2024-01-15T10:00:00")
        assert "ago" in result or result == "just now"

    def test_empty_string(self) -> None:
        assert format_date("") == ""

    def test_invalid_date(self) -> None:
        result = format_date("not-a-date")
        assert result == "not-a-date"

    def test_recent_date_shows_days(self) -> None:
        from datetime import datetime, timedelta, timezone

        recent = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        result = format_date(recent)
        assert "3 days ago" in result

    def test_old_date_shows_years(self) -> None:
        result = format_date("2020-01-01T00:00:00Z")
        assert "year" in result

    def test_months_ago(self) -> None:
        from datetime import datetime, timedelta, timezone

        months_ago = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
        result = format_date(months_ago)
        assert "month" in result

    def test_partial_date_fallback(self) -> None:
        result = format_date("2024-01-15")
        # fromisoformat handles "YYYY-MM-DD" in Python 3.12+
        assert "ago" in result or result == "2024-01-15"
