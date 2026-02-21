# 第一阶段：构建环境
# 使用官方Python 3.11运行时作为父镜像
FROM python:3.11-slim AS build

# 确保Python输出是UTF-8
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=UTF-8

# 设置工作目录
WORKDIR /app

# 复制 pyproject.toml 和 poetry.lock
COPY pyproject.toml poetry.lock ./

# 安装poetry。你可以通过其他方式预先安装poetry，比如在Dockerfile中使用RUN pip install poetry
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple poetry

# 使用poetry安装依赖到虚拟环境
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-ansi

# 复制项目文件
COPY . .

# 如果有需要，可以在这里运行测试或其他构建脚本
# RUN pytest

# 第二阶段：生产环境
FROM python:3.11-slim AS production

# 确保Python输出是UTF-8
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=UTF-8

# 设置工作目录
WORKDIR /app

# 从构建阶段复制已安装的依赖和项目文件
COPY --from=build /app /app

# 由于Poetry会将依赖安装在虚拟环境中，我们可以通过以下方式激活虚拟环境
ENV PATH="/app/.venv/bin:$PATH"

# 可选：如果只需要运行时依赖，可以删除安装在虚拟环境中的开发依赖
# RUN poetry install --no-root --only-main

# 声明运行时需要暴露的端口
EXPOSE 5000

# 定义环境变量
# ENV NAME World

# 运行应用程序
# CMD ["python", "holiday_cn/update.py"]
