#!/bin/bash
set -e

# 动态获取当前年份
CURRENT_YEAR=$(date +%Y)

# 如果当前年份数据不存在，执行更新
if [ ! -f "/app/data/${CURRENT_YEAR}.json" ]; then
    echo "数据不存在或需要更新，正在获取..."
    python -m holiday_cn.entry
    echo "数据更新完成"
fi

# 设置定时任务
echo "${CRON_SCHEDULE:-0 12 * * *} cd /app && python -m holiday_cn.entry >> /var/log/cron.log 2>&1" | crontab -
echo "定时任务已配置: ${CRON_SCHEDULE:-0 12 * * *}"

# 创建日志文件
touch /var/log/cron.log

# 启动 cron 守护进程
cron

echo "服务启动中..."
# 启动 API 服务（前台主进程）
exec uvicorn holiday_cn.api:app --host 0.0.0.0 --port 8000
