# 使用官方 slim 镜像 (Debian-based)
FROM python:3.12.3-slim-bullseye

# 设置全局环境变量
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

# 替换 APT 源为清华源
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list

# 安装系统依赖并清理
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录并复制依赖文件
WORKDIR /app
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install -r requirements.txt

# 复制应用代码（注意 Windows 文件权限）
COPY . .

# 暴露端口（与 app.py 中配置的端口一致）
EXPOSE 8001

# 直接通过 Python 运行（需 app.py 包含启动代码）
CMD ["python", "app.py"]