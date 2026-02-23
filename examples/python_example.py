#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
通过 jsDelivr CDN 访问中国法定节假日数据的 Python 示例

CDN 地址格式:
https://cdn.jsdelivr.net/gh/drjiathu/holiday-cn@latest/data/{year}.json
"""

from functools import lru_cache
from datetime import date

import requests

# CDN 基础地址 (使用 @latest 自动指向最新 release)
CDN_BASE_URL = "https://cdn.jsdelivr.net/gh/drjiathu/holiday-cn@latest/data"


@lru_cache(maxsize=10)
def get_holidays(year: int) -> dict:
    """
    获取指定年份的节假日数据（带内存缓存）

    Args:
        year: 年份，如 2024

    Returns:
        包含节假日信息的字典
    """
    url = f"{CDN_BASE_URL}/{year}.json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def is_holiday(query_date: str | date) -> dict:
    """
    检查某天是否为法定节假日

    Args:
        query_date: 日期，格式为 "YYYY-MM-DD" 或 date 对象

    Returns:
        包含节假日信息的字典
    """
    if isinstance(query_date, date):
        query_date = query_date.isoformat()

    year = int(query_date[:4])
    data = get_holidays(year)

    for day in data["days"]:
        if day["date"] == query_date:
            return {
                "date": query_date,
                "isHoliday": True,
                "isOffDay": day["isOffDay"],
                "name": day["name"],
            }

    return {"date": query_date, "isHoliday": False}


def is_off_day(query_date: str | date) -> bool:
    """
    判断是否为休息日（法定节假日且放假）

    Args:
        query_date: 日期

    Returns:
        是否为休息日
    """
    result = is_holiday(query_date)
    return result.get("isOffDay", False)


def is_work_day(query_date: str | date) -> bool:
    """
    判断是否为调休工作日（法定节假日但需要上班）

    Args:
        query_date: 日期

    Returns:
        是否为调休工作日
    """
    result = is_holiday(query_date)
    return result["isHoliday"] and not result.get("isOffDay", True)


def get_holidays_in_range(start_date: str, end_date: str) -> list[dict]:
    """
    获取日期范围内的所有法定节假日

    Args:
        start_date: 开始日期 "YYYY-MM-DD"
        end_date: 结束日期 "YYYY-MM-DD"

    Returns:
        节假日列表
    """
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    results = []
    for year in range(start.year, end.year + 1):
        data = get_holidays(year)
        for day in data["days"]:
            day_date = date.fromisoformat(day["date"])
            if start <= day_date <= end:
                results.append(day)

    return results


def get_next_holiday(from_date: str | date = None) -> dict | None:
    """
    获取下一个法定假日（休息日）

    Args:
        from_date: 起始日期，默认为今天

    Returns:
        下一个假日信息
    """
    if from_date is None:
        from_date = date.today()
    elif isinstance(from_date, str):
        from_date = date.fromisoformat(from_date)

    # 检查当年和下一年
    for year in [from_date.year, from_date.year + 1]:
        try:
            data = get_holidays(year)
            for day in data["days"]:
                day_date = date.fromisoformat(day["date"])
                if day_date > from_date and day["isOffDay"]:
                    return day
        except requests.HTTPError:
            continue

    return None


# ============ 使用示例 ============

if __name__ == "__main__":
    print("=" * 50)
    print("中国法定节假日查询示例")
    print("=" * 50)

    # 示例 1: 查询特定日期
    print("\n1. 查询特定日期是否为节假日:")
    result = is_holiday("2024-10-01")
    print(f"   2024-10-01: {result}")

    result = is_holiday("2024-10-08")
    print(f"   2024-10-08: {result}")

    # 示例 2: 判断是否为休息日
    print("\n2. 判断是否为休息日:")
    print(f"   2024-10-01 是休息日: {is_off_day('2024-10-01')}")
    print(f"   2024-09-29 是休息日: {is_off_day('2024-09-29')}")

    # 示例 3: 判断是否为调休工作日
    print("\n3. 判断是否为调休工作日:")
    print(f"   2024-09-29 是调休工作日: {is_work_day('2024-09-29')}")

    # 示例 4: 获取日期范围内的节假日
    print("\n4. 获取 2024 年 10 月的节假日:")
    holidays = get_holidays_in_range("2024-10-01", "2024-10-31")
    for h in holidays:
        status = "休息" if h["isOffDay"] else "上班"
        print(f"   {h['date']} {h['name']} ({status})")

    # 示例 5: 获取下一个假日
    print("\n5. 获取下一个假日:")
    next_holiday = get_next_holiday()
    if next_holiday:
        print(f"   {next_holiday['date']} {next_holiday['name']}")

    # 示例 6: 获取年度数据概览
    print("\n6. 2024 年节假日概览:")
    data = get_holidays(2024)
    print(f"   数据来源: {data['papers'][0][:50]}...")
    off_days = [d for d in data["days"] if d["isOffDay"]]
    work_days = [d for d in data["days"] if not d["isOffDay"]]
    print(f"   放假天数: {len(off_days)} 天")
    print(f"   调休天数: {len(work_days)} 天")
