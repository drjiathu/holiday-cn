"""Integration tests for API service."""

import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from holiday_cn.api import app, _cache


@pytest.fixture
def client():
    """Create test client."""
    _cache.clear()  # 清除缓存
    return TestClient(app)


@pytest.fixture
def mock_data_dir(tmp_path):
    """Create mock data directory with test data."""
    # 创建测试数据
    test_data = {
        "$schema": "https://example.com/schema.json",
        "$id": "https://example.com/2024.json",
        "year": 2024,
        "papers": ["https://www.gov.cn/test"],
        "days": [
            {"date": "2024-01-01", "name": "元旦", "isOffDay": True},
            {"date": "2024-01-02", "name": "元旦", "isOffDay": True},
            {"date": "2024-01-03", "name": "元旦", "isOffDay": False},
            {"date": "2024-10-01", "name": "国庆节", "isOffDay": True},
            {"date": "2024-10-02", "name": "国庆节", "isOffDay": True},
            {"date": "2024-10-03", "name": "国庆节", "isOffDay": True},
        ],
    }

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    with open(data_dir / "2024.json", "w", encoding="utf-8") as f:
        json.dump(test_data, f, ensure_ascii=False)

    return data_dir


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_returns_html(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "中国法定节假日 API" in response.text

    def test_api_info_returns_json(self, client):
        response = client.get("/api")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data


class TestDateEndpoint:
    """Tests for /date/{date} endpoint."""

    def test_query_holiday(self, client, mock_data_dir):
        with patch("holiday_cn.api.dataspace_path") as mock_path:
            mock_path.return_value = mock_data_dir / "2024.json"
            response = client.get("/date/2024-01-01")

        assert response.status_code == 200
        data = response.json()
        assert data["date"] == "2024-01-01"
        assert data["isHoliday"] is True
        assert data["isOffDay"] is True
        assert data["name"] == "元旦"

    def test_query_workday(self, client, mock_data_dir):
        with patch("holiday_cn.api.dataspace_path") as mock_path:
            mock_path.return_value = mock_data_dir / "2024.json"
            response = client.get("/date/2024-01-03")

        assert response.status_code == 200
        data = response.json()
        assert data["isHoliday"] is True
        assert data["isOffDay"] is False  # 补班

    def test_query_normal_day(self, client, mock_data_dir):
        with patch("holiday_cn.api.dataspace_path") as mock_path:
            mock_path.return_value = mock_data_dir / "2024.json"
            response = client.get("/date/2024-03-15")

        assert response.status_code == 200
        data = response.json()
        assert data["isHoliday"] is False
        assert data["isOffDay"] is None
        assert data["name"] is None

    def test_invalid_date_format(self, client):
        response = client.get("/date/2024-1-1")
        assert response.status_code == 400
        assert "日期格式错误" in response.json()["detail"]

    def test_invalid_date_value(self, client):
        response = client.get("/date/not-a-date")
        assert response.status_code == 400


class TestYearEndpoint:
    """Tests for /year/{year} endpoint."""

    def test_get_year_data(self, client, mock_data_dir):
        with patch("holiday_cn.api.dataspace_path") as mock_path:
            mock_path.return_value = mock_data_dir / "2024.json"
            response = client.get("/year/2024")

        assert response.status_code == 200
        data = response.json()
        assert data["year"] == 2024
        assert len(data["papers"]) > 0
        assert len(data["days"]) == 6

    def test_year_not_found(self, client, mock_data_dir):
        with patch("holiday_cn.api.dataspace_path") as mock_path:
            mock_path.return_value = mock_data_dir / "1999.json"  # 不存在
            response = client.get("/year/1999")

        assert response.status_code == 404
        assert "未找到" in response.json()["detail"]


class TestRangeEndpoint:
    """Tests for /range endpoint."""

    def test_query_range(self, client, mock_data_dir):
        with patch("holiday_cn.api.dataspace_path") as mock_path:
            mock_path.return_value = mock_data_dir / "2024.json"
            response = client.get("/range?start=2024-01-01&end=2024-01-03")

        assert response.status_code == 200
        data = response.json()
        assert data["start"] == "2024-01-01"
        assert data["end"] == "2024-01-03"
        assert len(data["days"]) == 3

    def test_range_invalid_dates(self, client):
        response = client.get("/range?start=invalid&end=2024-01-03")
        assert response.status_code == 400

    def test_range_start_after_end(self, client):
        response = client.get("/range?start=2024-12-31&end=2024-01-01")
        assert response.status_code == 400
        assert "开始日期不能晚于结束日期" in response.json()["detail"]


class TestTodayEndpoint:
    """Tests for /today endpoint."""

    def test_today_returns_response(self, client, mock_data_dir):
        with patch("holiday_cn.api.dataspace_path") as mock_path:
            mock_path.return_value = mock_data_dir / "2024.json"
            response = client.get("/today")

        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "isHoliday" in data
