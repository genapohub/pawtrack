# 宠迹 PawTrack — 开发命令速查
# 用法：make <target>，例如 make dev / make prod / make test

.PHONY: help infra dev dev-down prod prod-down test test-backend test-admin lint build keys

PYTHON ?= python3
VENV   ?= backend/.venv

help:  ## 显示所有命令
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ── 基础设施 ─────────────────────────────
infra:  ## 启动本地基础设施（DB/Redis/Mongo/MQTT，本地裸跑后端用）
	docker compose -f docker-compose.infra.yml up -d

infra-down:  ## 停止本地基础设施
	docker compose -f docker-compose.infra.yml down

# ── 全栈开发（Docker）─────────────────
dev:  ## 启动全栈开发环境（Docker，前后端+基础设施）
	docker compose up -d --build

dev-down:  ## 停止全栈开发环境
	docker compose down

dev-logs:  ## 查看后端日志
	docker compose logs -f backend

# ── 本地裸跑后端（配合 infra）──────────────
run-backend:  ## 本地裸跑后端（需先 make infra）
	cd backend && $(VENV)/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-admin:  ## 本地裸跑 admin
	cd ../04_前端项目/admin && npm run dev

# ── 生产 ─────────────────────────────
prod:  ## 启动生产编排（需先配置 .env，见 .env.example）
	docker compose -f docker-compose.prod.yml up -d

prod-down:  ## 停止生产编排
	docker compose -f docker-compose.prod.yml down

# ── 测试 ─────────────────────────────
test: test-backend test-admin  ## 运行全部测试

test-backend:  ## 后端 pytest（仅单测，跳过集成）
	cd backend && $(VENV)/bin/pytest tests/ -v

test-admin:  ## admin vitest
	cd ../04_前端项目/admin && npm run test

# ── 性能压测 ─────────────────────────────
load-test:  ## 启动 Locust Web 压测（浏览器配置并发）
	cd backend && $(VENV)/bin/locust -f tests/load/locustfile.py --host=http://localhost:8000

load-test-headless:  ## 无头压测（默认 100 用户，10/s 爬坡，60s）
	cd backend && $(VENV)/bin/locust -f tests/load/locustfile.py \
		--host=http://localhost:8000 --headless \
		-u 100 -r 10 --run-time 60s \
		--html=loadtest-report.html
	@echo "📊 报告已生成：backend/loadtest-report.html"

# ── Lint ─────────────────────────────
lint:  ## 后端 ruff lint
	cd backend && $(VENV)/bin/ruff check app/ tests/

lint-fix:  ## 后端 ruff 自动修复
	cd backend && $(VENV)/bin/ruff check --fix --unsafe-fixes app/ tests/

# ── 构建 ─────────────────────────────
build: build-admin  ## 构建前端产物

build-admin:  ## 构建 admin
	cd ../04_前端项目/admin && npm run build

# ── JWT 密钥 ─────────────────────────────
keys:  ## 生成 JWT RSA 密钥对到 ../keys/
	@mkdir -p ../keys
	@if [ -f ../keys/jwt_private.pem ]; then echo "⚠️  密钥已存在，跳过（如需重新生成请先删除 ../keys/jwt_private.pem）"; exit 0; fi
	openssl genrsa -out ../keys/jwt_private.pem 2048
	openssl rsa -in ../keys/jwt_private.pem -pubout -out ../keys/jwt_public.pem
	@chmod 600 ../keys/jwt_private.pem
	@echo "✅ 已生成 ../keys/jwt_private.pem + ../keys/jwt_public.pem"

# ── 安装 ─────────────────────────────
install:  ## 安装全部依赖（后端 venv + 前端 npm）
	cd backend && $(PYTHON) -m venv $(VENV) && $(VENV)/bin/pip install -r requirements.txt -r requirements-dev.txt
	cd ../04_前端项目/admin && npm install
