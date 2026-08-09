"""
宠迹 PawTrack — 监控告警

包含：
  - Prometheus metrics 接入（/metrics）
  - 深度健康检查（DB/Redis/MongoDB 连通性）
  - 告警 webhook（关键错误推送）
  - Sentry 集成（可选，通过 SENTRY_DSN 注入）
"""
from typing import Any
from app.config import settings
from app.logging import logger

# ── Prometheus metrics ─────────────────────────────

_metrics_instrumentator = None


def setup_metrics(app: Any) -> None:
    """接入 Prometheus 指标采集，暴露 /metrics 端点。

    依赖 prometheus_fastapi_instrumentator（可选，缺失时静默跳过）。
    """
    global _metrics_instrumentator
    try:
        from prometheus_fastapi_instrumentator import Instrumentator
    except ImportError:
        logger.warning("prometheus_fastapi_instrumentator 未安装，/metrics 端点不可用")
        return

    _metrics_instrumentator = Instrumentator(
        should_gzip=True,
        should_round_latency_decimals=True,
        excluded_handlers=["/health", "/metrics"],
    )
    _metrics_instrumentator.instrument(app).expose(
        app, endpoint="/metrics", include_in_schema=False
    )
    logger.info("Prometheus metrics 已启用 → /metrics")


# ── 深度健康检查 ─────────────────────────────


async def check_postgres() -> dict:
    """检查 PostgreSQL 连通性"""
    from app.database import engine
    from sqlalchemy import text
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "up"}
    except Exception as e:  # noqa: BLE001
        return {"status": "down", "error": str(e)}


async def check_redis() -> dict:
    """检查 Redis 连通性"""
    try:
        import redis.asyncio as aioredis
        client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        pong = await client.ping()
        await client.aclose()
        return {"status": "up" if pong else "down"}
    except Exception as e:  # noqa: BLE001
        return {"status": "down", "error": str(e)}


async def check_mongodb() -> dict:
    """检查 MongoDB 连通性"""
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
        await client.admin.command("ping")
        client.close()
        return {"status": "up"}
    except Exception as e:  # noqa: BLE001
        return {"status": "down", "error": str(e)}


async def deep_health() -> dict:
    """聚合健康检查，返回各依赖状态"""
    checks = await _gather(check_postgres, check_redis, check_mongodb)
    all_up = all(c.get("status") == "up" for c in checks.values())
    return {
        "status": "healthy" if all_up else "degraded",
        "service": "pawtrack-api",
        "env": settings.ENV,
        "checks": checks,
    }


async def _gather(*checkers) -> dict:
    """并发执行检查器，返回 {name: result}"""
    import asyncio
    results = await asyncio.gather(
        *[c() for c in checkers], return_exceptions=True
    )
    out = {}
    for c, r in zip(checkers, results):
        name = c.__name__.replace("check_", "")
        if isinstance(r, Exception):
            out[name] = {"status": "down", "error": str(r)}
        else:
            out[name] = r
    return out


# ── 告警 webhook ─────────────────────────────

_alert_buffer: list[dict] = []


def send_alert(title: str, message: str, severity: str = "warning") -> None:
    """发送告警。生产环境推送到 ALERT_WEBHOOK_URL，开发环境仅记录日志。

    severity: info | warning | error | critical
    """
    payload = {
        "title": title,
        "message": message,
        "severity": severity,
        "env": settings.ENV,
        "service": "pawtrack-api",
    }
    _alert_buffer.append(payload)
    if len(_alert_buffer) > 100:
        _alert_buffer.pop(0)

    log_fn = {
        "info": logger.info, "warning": logger.warning,
        "error": logger.error, "critical": logger.critical,
    }.get(severity, logger.warning)
    log_fn(f"[告警] {title}: {message}", extra={"alert": payload})

    webhook = getattr(settings, "ALERT_WEBHOOK_URL", None)
    if webhook and settings.is_prod:
        import httpx
        try:
            httpx.post(webhook, json=payload, timeout=5.0)
        except Exception as e:  # noqa: BLE001
            logger.error(f"告警 webhook 推送失败: {e}")


def get_alert_buffer() -> list[dict]:
    """返回最近告警缓冲（供 admin 查看）"""
    return list(_alert_buffer)


# ── Sentry 集成（可选）─────────────────

def setup_sentry() -> None:
    """接入 Sentry，需通过 SENTRY_DSN 环境变量注入。缺失则跳过。"""
    dsn = getattr(settings, "SENTRY_DSN", None)
    if not dsn:
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.asyncio import AsyncioIntegration
        sentry_sdk.init(
            dsn=dsn,
            environment=settings.ENV,
            traces_sample_rate=0.1 if settings.is_prod else 1.0,
            send_default_pii=False,
            integrations=[AsyncioIntegration()],
        )
        logger.info("Sentry 已启用")
    except ImportError:
        logger.warning("sentry-sdk 未安装，Sentry 集成跳过")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Sentry 初始化失败: {e}")
