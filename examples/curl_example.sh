#!/bin/bash
# 通过 jsDelivr CDN 访问中国法定节假日数据的 Shell 示例
#
# CDN 地址格式:
# https://cdn.jsdelivr.net/gh/drjiathu/holiday-cn@main/data/{year}.json

# 使用 @latest 自动指向最新 release
CDN_BASE_URL="https://cdn.jsdelivr.net/gh/drjiathu/holiday-cn@latest/data"

echo "=================================================="
echo "中国法定节假日查询示例 (Shell/Curl)"
echo "=================================================="

# 示例 1: 获取 2024 年节假日数据
echo -e "\n1. 获取 2024 年节假日数据:"
curl -s "${CDN_BASE_URL}/2024.json" | head -c 500
echo -e "\n..."

# 示例 2: 使用 jq 解析 JSON (需要安装 jq)
if command -v jq &> /dev/null; then
    echo -e "\n2. 获取 2024 年所有节假日名称 (使用 jq):"
    curl -s "${CDN_BASE_URL}/2024.json" | jq -r '.days[] | "\(.date) \(.name) (\(if .isOffDay then "休息" else "上班" end))"'

    echo -e "\n3. 查询特定日期 (2024-10-01):"
    curl -s "${CDN_BASE_URL}/2024.json" | jq '.days[] | select(.date == "2024-10-01")'

    echo -e "\n4. 统计放假天数和调休天数:"
    curl -s "${CDN_BASE_URL}/2024.json" | jq '{
        year: .year,
        off_days: [.days[] | select(.isOffDay == true)] | length,
        work_days: [.days[] | select(.isOffDay == false)] | length
    }'

    echo -e "\n5. 获取所有休息日:"
    curl -s "${CDN_BASE_URL}/2024.json" | jq -r '.days[] | select(.isOffDay == true) | "\(.date) \(.name)"'
else
    echo -e "\n提示: 安装 jq 可以更方便地解析 JSON 数据"
    echo "  macOS: brew install jq"
    echo "  Ubuntu: apt-get install jq"
fi

# 示例: 下载 ICS 日历文件
echo -e "\n6. 下载 ICS 日历文件:"
echo "curl -O ${CDN_BASE_URL}/2024.ics"
echo "curl -O ${CDN_BASE_URL}/holiday-cn.ics"

# 示例: 一行命令检查某天是否为节假日
echo -e "\n7. 一行命令检查某天是否为节假日:"
echo 'DATE="2024-10-01"; curl -s "${CDN_BASE_URL}/2024.json" | jq --arg d "$DATE" ".days[] | select(.date == \$d)"'
