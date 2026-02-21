# 使用官方 Python 3.11 运行时作为基础镜像
FROM python:3.11-slim

# 确保 Python 输出是 UTF-8
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=UTF-8

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron curl && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY pyproject.toml poetry.lock ./

# 安装 Poetry 并安装依赖
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --only main --no-ansi

# 复制项目文件
COPY holiday_cn ./holiday_cn

# 复制启动脚本
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 创建数据目录
RUN mkdir -p /app/data

# 环境变量：cron 表达式（默认每天中午 12 点）
ENV CRON_SCHEDULE="0 12 * * *"

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# 启动入口
ENTRYPOINT ["docker-entrypoint.sh"]
