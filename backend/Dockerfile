# 宠迹 PawTrack 后端生产镜像
FROM python:3.12-slim AS builder

WORKDIR /app

# 系统依赖（构建期）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ── 运行阶段 ─────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# 运行期系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制已安装的 Python 包
COPY --from=builder /root/.local /root/.local

# 复制应用代码
COPY app/ ./app/

ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
