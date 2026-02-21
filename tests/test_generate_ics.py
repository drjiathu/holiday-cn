"""Test module for `generate_ics`."""

import tempfile
from datetime import date
from pathlib import Path

import pytest

from holiday_cn.generate_ics import (
    _cast_date,
    _iter_date_ranges,
    generate_ics,
)


class TestCastDate:
    """Tests for _cast_date function."""

    def test_cast_date_from_date(self):
        d = date(2024, 1, 1)
        assert _cast_date(d) == d

    def test_cast_date_from_string(self):
        assert _cast_date("2024-01-01") == date(2024, 1, 1)

    def test_cast_date_invalid_type(self):
        with pytest.raises(NotImplementedError):
            _cast_date(12345)


class TestIterDateRanges:
    """Tests for _iter_date_ranges function."""

    def test_empty_days(self):
        assert list(_iter_date_ranges([])) == []

    def test_single_day(self):
        days = [{"date": "2024-01-01", "name": "元旦", "isOffDay": True}]
        result = list(_iter_date_ranges(days))
        assert len(result) == 1
        assert result[0] == (days[0], days[0])

    def test_consecutive_days_same_type(self):
        """Consecutive days with same isOffDay should merge."""
        days = [
            {"date": "2024-01-01", "name": "元旦", "isOffDay": True},
            {"date": "2024-01-02", "name": "元旦", "isOffDay": True},
            {"date": "2024-01-03", "name": "元旦", "isOffDay": True},
        ]
        result = list(_iter_date_ranges(days))
        assert len(result) == 1
        assert result[0] == (days[0], days[2])

    def test_consecutive_days_different_type(self):
        """Consecutive days with different isOffDay should not merge."""
        days = [
            {"date": "2024-01-01", "name": "元旦", "isOffDay": True},
            {"date": "2024-01-02", "name": "元旦", "isOffDay": False},
        ]
        result = list(_iter_date_ranges(days))
        assert len(result) == 2
        assert result[0] == (days[0], days[0])
        assert result[1] == (days[1], days[1])

    def test_non_consecutive_days(self):
        """Non-consecutive days should not merge."""
        days = [
            {"date": "2024-01-01", "name": "元旦", "isOffDay": True},
            {"date": "2024-01-03", "name": "元旦", "isOffDay": True},
        ]
        result = list(_iter_date_ranges(days))
        assert len(result) == 2

    def test_mixed_scenario(self):
        """Test a realistic mixed scenario."""
        days = [
            {"date": "2024-01-01", "name": "元旦", "isOffDay": True},
            {"date": "2024-01-02", "name": "元旦", "isOffDay": True},
            {"date": "2024-01-03", "name": "元旦", "isOffDay": False},
            {"date": "2024-02-10", "name": "春节", "isOffDay": True},
            {"date": "2024-02-11", "name": "春节", "isOffDay": True},
        ]
        result = list(_iter_date_ranges(days))
        assert len(result) == 3
        # 元旦假期 (1.1-1.2)
        assert result[0] == (days[0], days[1])
        # 元旦补班 (1.3)
        assert result[1] == (days[2], days[2])
        # 春节假期 (2.10-2.11)
        assert result[2] == (days[3], days[4])


class TestGenerateIcs:
    """Tests for generate_ics function."""

    def test_generate_ics_creates_file(self):
        """Test that generate_ics creates a valid ICS file."""
        days = [
            {"date": "2024-01-01", "name": "元旦", "isOffDay": True},
        ]
        with tempfile.NamedTemporaryFile(suffix=".ics", delete=False) as f:
            filepath = Path(f.name)

        try:
            generate_ics(days, filepath)
            assert filepath.exists()
            content = filepath.read_bytes()
            assert b"BEGIN:VCALENDAR" in content
            assert b"END:VCALENDAR" in content
        finally:
            filepath.unlink()

    def test_generate_ics_contains_event(self):
        """Test that ICS contains the correct event."""
        days = [
            {"date": "2024-01-01", "name": "元旦", "isOffDay": True},
        ]
        with tempfile.NamedTemporaryFile(suffix=".ics", delete=False) as f:
            filepath = Path(f.name)

        try:
            generate_ics(days, filepath)
            content = filepath.read_text(encoding="utf-8")
            assert "BEGIN:VEVENT" in content
            assert "END:VEVENT" in content
        finally:
            filepath.unlink()

    def test_generate_ics_workday_naming(self):
        """Test that workdays are named correctly."""
        days = [
            {"date": "2024-01-03", "name": "元旦", "isOffDay": False},
        ]
        with tempfile.NamedTemporaryFile(suffix=".ics", delete=False) as f:
            filepath = Path(f.name)

        try:
            generate_ics(days, filepath)
            content = filepath.read_bytes()
            # 补班日应该包含 "上班" 字样
            assert "上班".encode("utf-8") in content
        finally:
            filepath.unlink()

    def test_generate_ics_calendar_metadata(self):
        """Test that ICS contains correct calendar metadata."""
        days = [
            {"date": "2024-01-01", "name": "元旦", "isOffDay": True},
        ]
        with tempfile.NamedTemporaryFile(suffix=".ics", delete=False) as f:
            filepath = Path(f.name)

        try:
            generate_ics(days, filepath)
            content = filepath.read_bytes()
            assert b"VERSION:2.0" in content
            assert b"METHOD:PUBLISH" in content
            assert "中国法定节假日".encode("utf-8") in content
        finally:
            filepath.unlink()

    def test_generate_ics_timezone(self):
        """Test that ICS contains timezone information."""
        days = [
            {"date": "2024-01-01", "name": "元旦", "isOffDay": True},
        ]
        with tempfile.NamedTemporaryFile(suffix=".ics", delete=False) as f:
            filepath = Path(f.name)

        try:
            generate_ics(days, filepath)
            content = filepath.read_text(encoding="utf-8")
            assert "VTIMEZONE" in content
            assert "Asia/Shanghai" in content
        finally:
            filepath.unlink()
