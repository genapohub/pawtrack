"""
宠迹 PawTrack — 限流中间件

基于 Redis 固定窗口计数器实现，无需额外依赖。
规则（对照 API 设计文档第 7 节）：
  - POST /auth/login        5 req/min   （按 IP）
  - POST /auth/register     5 req/min   （按 IP）
  - POST /location/upload  30 req/min   （按用户/设备）
  - 全局 GET /api/v1/*     300 req/min  （按用户/IP）

未配置 Redis 或 Redis 不可用时自动降级（放行），不影响可用性。
"""
import time
from typing import Optional, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.logging import logger

# 限流规则：(path_prefix, method, limit, window_seconds)
RATE_RULES = [
    ("/api/v1/auth/login", "POST", 5, 60),
    ("/api/v1/auth/register", "POST", 5, 60),
    ("/api/v1/location/upload", "POST", 30, 60),
]

GLOBAL_LIMIT = 300        # 全局每分钟请求数
GLOBAL_WINDOW = 60


def _client_key(request: Request) -> str:
    """识别客户端：优先用 JWT 中的 user，其次 X-Forwarded-For，最后 client host"""
    # 尝试从已解析的 user（若有）取
    user = getattr(request.state, "user", None)
    if user and isinstance(user, dict) and user.get("sub"):
        return f"user:{user['sub']}"
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return f"ip:{fwd.split(',')[0].strip()}"
    return f"ip:{request.client.host if request.client else 'unknown'}"


async def _check(redis, key: str, limit: int, window: int) -> tuple[bool, int]:
    """检查计数，返回 (allowed, remaining)。Redis 不可用时放行。"""
    if redis is None:
        return True, limit
    try:
        current = await redis.incr(key)
        if current == 1:
            await redis.expire(key, window)
        ttl = await redis.ttl(key)
        if ttl < 0:  # 防止 key 无过期
            await redis.expire(key, window)
        return current <= limit, max(limit - current, 0)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"限流 Redis 检查失败，降级放行: {e}")
        return True, limit


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件：路径规则 + 全局规则"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 健康检查/指标/文档不限流
        path = request.url.path
        if path in ("/health", "/metrics", "/", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        # 从 app 获取 redis_client（main.py 注入到 app.state）
        redis = getattr(request.app.state, "redis_client", None)

        # 1. 路径级规则
        for prefix, method, limit, window in RATE_RULES:
            if path.startswith(prefix) and request.method == method:
                key = f"rl:{prefix}:{method}:{_client_key(request)}"
                allowed, remaining = await _check(redis, key, limit, window)
                if not allowed:
                    return _rate_limited_response(limit, window, remaining)
                break

        # 2. 全局规则（仅对 /api/v1/* 生效）
        if path.startswith("/api/v1/"):
            key = f"rl:global:{_client_key(request)}"
            allowed, remaining = await _check(redis, key, GLOBAL_LIMIT, GLOBAL_WINDOW)
            if not allowed:
                return _rate_limited_response(GLOBAL_LIMIT, GLOBAL_WINDOW, remaining)

        return await call_next(request)


def _rate_limited_response(limit: int, window: int, remaining: int) -> Response:
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=429,
        content={
            "code": 42900,
            "message": f"请求过于频繁，限流 {limit} 次/{window}秒",
            "retry_after": window,
        },
        headers={
            "Retry-After": str(window),
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
        },
    )
