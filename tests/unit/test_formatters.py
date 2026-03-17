from src.utils.formatters import format_number, truncate


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
