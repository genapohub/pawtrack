"""
宠迹 PawTrack — FastAPI 后端入口（MVP Sprint 1）
"""
import asyncio
import json
import time
import uuid
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

# ── 导入配置和模块 ──────────────────────────────────────────
from app.config import settings
from app.logging import logger
from app.database import engine, SessionLocal
from app.models import Base
from app.auth import get_current_user_optional
from app.websocket_manager import ws_manager
from app.monitoring import setup_metrics, setup_sentry, deep_health, send_alert
from app.ratelimit import RateLimitMiddleware

# ── 生命周期管理 ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    env_label = "开发环境 (DEV)" if settings.is_dev else "生产环境 (PROD)"
    logger.info(f"🚀 宠迹后端服务启动中... [{env_label}]")
    logger.info(f"   ENV={settings.ENV} | DEBUG={settings.DEBUG}")
    logger.info(f"   DATABASE_URL={settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    setup_sentry()
    await init_db()
    await init_redis()
    app.state.redis_client = redis_client
    await init_websocket()
    logger.info("✅ 依赖服务连接就绪")

    # V2.0: 碰头超时扫描后台任务（每 60 秒扫描 confirmed 超过 30 分钟的 meet → failed）
    timeout_task = asyncio.create_task(_meet_timeout_worker(), name="meet-timeout")

    yield

    # 关闭时执行
    timeout_task.cancel()
    try:
        await timeout_task
    except asyncio.CancelledError:
        pass
    await ws_manager.stop()
    await engine.dispose()
    logger.info("🛑 宠迹后端服务关闭")


# ── FastAPI 实例 ────────────────────────────────────────────────

app = FastAPI(
    title="宠迹 PawTrack API",
    description="宠物智能定位与社交平台后端服务",
    version="0.4.0 (Sprint 3)",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 限流中间件 ──────────────────────────────────────────
app.add_middleware(RateLimitMiddleware)

# ── Prometheus metrics ──────────────────────────────────────────
setup_metrics(app)


# ── 请求中间件（请求 ID + 耗时日志 + 异常告警）──────────────────────
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]
    start = time.perf_counter()

    # 注入 request_id 到响应头
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-ms"] = f"{duration_ms:.1f}"

    # 慢请求告警（>2s）
    if duration_ms > 2000:
        send_alert(
            "慢请求",
            f"{request.method} {request.url.path} 耗时 {duration_ms:.0f}ms (request_id={request_id})",
            severity="warning",
        )

    logger.info(
        f"{request.method} {request.url.path} → {response.status_code} ({duration_ms:.0f}ms)",
        extra={"request_id": request_id, "method": request.method,
               "path": request.url.path, "status": response.status_code,
               "duration_ms": round(duration_ms, 1)},
    )
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """捕获未处理异常，告警并返回 500"""
    import traceback
    send_alert(
        "未处理异常",
        f"{request.method} {request.url.path}: {exc}",
        severity="error",
    )
    logger.error(f"未处理异常: {exc}", exc_info=True,
                 extra={"path": request.url.path})
    if settings.is_dev:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "traceback": traceback.format_exc()},
        )
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


# ── 初始化函数 ──────────────────────────────────────────────

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ 数据库表结构已确认")

async def init_redis():
    import redis.asyncio as aioredis
    global redis_client
    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    await redis_client.ping()
    logger.info("✅ Redis 连接已确认")

async def init_websocket():
    """启动 WebSocket Redis Pub/Sub 监听"""
    if redis_client:
        await ws_manager.start(redis_client)
        logger.info("✅ WebSocket Pub/Sub 监听已启动")

# ── Redis 全局引用 ──────────────────────────────────────────
redis_client = None


# ── 数据库依赖 ──────────────────────────────────────────────

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ── 健康检查 ──────────────────────────────────────────────────

@app.get("/health", tags=["系统"])
async def health_check():
    """深度健康检查，返回各依赖连通性"""
    return await deep_health()


# ── 根路径 ────────────────────────────────────────────────────

@app.get("/", tags=["系统"])
async def root():
    return {
        "message": "🐾 宠迹 PawTrack API 已启动",
        "version": "0.4.0",
        "env": settings.ENV,
        "debug": settings.DEBUG,
        "docs": "/docs",
        "sprint": "Sprint 3 — 后台管理系统",
        "modules": ["auth", "users", "pets", "devices", "location", "ws", "alarms", "social", "orders", "points", "admin"]
    }


# ── 注册路由 ──────────────────────────────────────────────────

from app.routers import auth as auth_router
from app.routers import users as users_router
from app.routers import pets as pets_router
from app.routers import devices as devices_router
from app.routers import location as location_router
from app.routers import ws as ws_router
from app.routers import alarms as alarms_router
from app.routers import social as social_router
from app.routers import orders as orders_router
from app.routers import points as points_router
from app.routers import invites as invites_router
from app.routers import admin as admin_router

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(pets_router.router)
app.include_router(devices_router.router)
app.include_router(location_router.router)
app.include_router(ws_router.router)
app.include_router(alarms_router.router)
app.include_router(social_router.router)
app.include_router(orders_router.router)
app.include_router(points_router.router)
app.include_router(invites_router.router)
app.include_router(admin_router.router)


# ── V2.0 碰头超时扫描 ─────────────────────────────────────────

async def _meet_timeout_worker():
    """后台任务：每 60 秒扫描 confirmed 超过 30 分钟的 meet → failed"""
    # 延迟导入，避免循环
    from datetime import datetime, timedelta, timezone
    from app.models import Meet, MeetStatus
    from app.database import SessionLocal
    from sqlalchemy import select, update

    await asyncio.sleep(10)  # 启动缓冲，等所有组件就绪

    while True:
        try:
            async with SessionLocal() as db:
                cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
                result = await db.execute(
                    update(Meet)
                    .where(
                        Meet.status == MeetStatus.confirmed,
                        Meet.confirmed_at < cutoff
                    )
                    .values(status=MeetStatus.failed)
                )
                await db.commit()
                affected = result.rowcount
                if affected:
                    logger.info(f"⏱ 碰头超时扫描：标记 {affected} 条超时记录")
        except Exception as e:
            logger.warning(f"碰头超时扫描异常（下次重试）: {e}")
        await asyncio.sleep(60)


# ── 启动入口 ──────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
