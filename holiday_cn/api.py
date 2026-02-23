#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Simple API service for querying Chinese holidays."""

import json
from datetime import date
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .filetools import dataspace_path


class UTF8JSONResponse(JSONResponse):
    """自定义 JSON 响应，支持中文显示"""

    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


app = FastAPI(
    title="中国法定节假日 API",
    description="查询中国法定节假日数据",
    version="1.0.0",
    default_response_class=UTF8JSONResponse,
)

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DayInfo(BaseModel):
    """单日信息"""

    date: str
    name: str
    isOffDay: bool


class HolidayResponse(BaseModel):
    """节假日查询响应"""

    date: str
    isHoliday: bool
    isOffDay: bool | None = None
    name: str | None = None


class YearData(BaseModel):
    """年度数据"""

    year: int
    papers: list[str]
    days: list[DayInfo]


class RangeResponse(BaseModel):
    """日期范围查询响应"""

    start: str
    end: str
    days: list[DayInfo]


# 缓存已加载的数据
_cache: dict[int, dict] = {}


def load_year_data(year: int) -> dict | None:
    """加载指定年份的数据"""
    if year in _cache:
        return _cache[year]

    filepath = dataspace_path(f"{year}.json")
    if not filepath.exists():
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        _cache[year] = data
        return data


def find_day(year: int, month: int, day: int) -> dict | None:
    """查找指定日期的节假日信息"""
    data = load_year_data(year)
    if not data:
        return None

    target_date = f"{year:04d}-{month:02d}-{day:02d}"
    for d in data.get("days", []):
        if d["date"] == target_date:
            return d
    return None


@app.get("/", summary="API 信息")
def root():
    """返回 API 基本信息"""
    return {
        "name": "中国法定节假日 API",
        "version": "1.0.0",
        "endpoints": {
            "/date/{date}": "查询指定日期",
            "/year/{year}": "获取年度数据",
            "/today": "查询今天",
            "/range": "查询日期范围",
        },
    }


@app.get("/date/{query_date}", response_model=HolidayResponse, summary="查询指定日期")
def query_date(query_date: str):
    """
    查询指定日期是否为法定节假日

    - **query_date**: 日期，格式为 YYYY-MM-DD
    """
    try:
        d = date.fromisoformat(query_date)
    except ValueError as exc:
        raise HTTPException(
            status_code=400, detail="日期格式错误，应为 YYYY-MM-DD"
        ) from exc

    day_info = find_day(d.year, d.month, d.day)

    if day_info:
        return HolidayResponse(
            date=query_date,
            isHoliday=True,
            isOffDay=day_info["isOffDay"],
            name=day_info["name"],
        )
    else:
        return HolidayResponse(
            date=query_date,
            isHoliday=False,
        )


@app.get("/today", response_model=HolidayResponse, summary="查询今天")
def query_today():
    """查询今天是否为法定节假日"""
    today = date.today()
    return query_date(today.isoformat())


@app.get("/year/{year}", response_model=YearData, summary="获取年度数据")
def get_year_data(year: int):
    """
    获取指定年份的完整节假日数据

    - **year**: 年份，如 2024
    """
    data = load_year_data(year)
    if not data:
        raise HTTPException(status_code=404, detail=f"未找到 {year} 年的数据")

    return YearData(
        year=data["year"],
        papers=data["papers"],
        days=data["days"],
    )


@app.get("/range", response_model=RangeResponse, summary="查询日期范围")
def query_range(
    start: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end: str = Query(..., description="结束日期 YYYY-MM-DD"),
):
    """查询日期范围内的所有节假日"""
    try:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
    except ValueError as exc:
        raise HTTPException(
            status_code=400, detail="日期格式错误，应为 YYYY-MM-DD"
        ) from exc

    if start_date > end_date:
        raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")

    results = []
    for year in range(start_date.year, end_date.year + 1):
        data = load_year_data(year)
        if not data:
            continue
        for d in data.get("days", []):
            day_date = date.fromisoformat(d["date"])
            if start_date <= day_date <= end_date:
                results.append(d)

    return {"start": start, "end": end, "days": results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
