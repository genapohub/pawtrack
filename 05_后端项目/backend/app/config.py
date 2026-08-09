"""
宠迹 PawTrack — 配置管理（多环境自动切换）

环境识别规则（优先级从高到低）：
  1. 真实环境变量 ENV（如 export ENV=prod）
  2. .env 文件中的 ENV
  3. 默认 "dev"

各环境默认值：
  - dev：本地裸跑友好（localhost），DEBUG=True，开发密钥自动生成
  - prod：关键变量必须通过环境变量/.env 注入，缺失则启动报错

Docker 开发环境（docker-compose.yml）会显式覆盖为容器名（postgres/redis/...），
本地裸跑使用 localhost 默认值，生产通过 .env.prod 注入。
"""
import os
from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Optional


class Settings(BaseSettings):
    # ── 环境标识 ─────────────────────────────
    ENV: str = "dev"  # dev | prod
    DEBUG: bool = True

    # ── 数据库（dev 默认 localhost，便于本地裸跑）──────────────
    DATABASE_URL: str = "postgresql+asyncpg://pawtrack:pawtrack_dev@localhost:5432/pawtrack"

    # ── Redis ─────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_STREAM_MAXLEN: int = 1_000_000

    # ── MongoDB ─────────────────────────────
    MONGODB_URL: str = "mongodb://pawtrack:pawtrack_dev@localhost:27017/pawtrack"

    # ── RabbitMQ ─────────────────────────────
    RABBITMQ_URL: str = "amqp://pawtrack:pawtrack_dev@localhost:5672/"

    # ── MQTT ─────────────────────────────
    MQTT_BROKER_URL: str = "mqtt://localhost:1883"

    # ── JWT ─────────────────────────────
    JWT_PRIVATE_KEY_PATH: str = "/app/keys/jwt_private.pem"
    JWT_PUBLIC_KEY_PATH: str = "/app/keys/jwt_public.pem"
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 7200       # 2小时
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 2_592_000  # 30天

    # ── 第三方 ─────────────────────────────
    AMAP_API_KEY: Optional[str] = None
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_APP_SECRET: Optional[str] = None

    # ── 后台管理系统 ─────────────────────────────
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "pawtrack_admin_2026"
    ADMIN_TOKEN_EXPIRE_SECONDS: int = 28800  # 8小时

    # ── 监控告警 ─────────────────────────────
    SENTRY_DSN: Optional[str] = None
    ALERT_WEBHOOK_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    # ── 便捷属性 ─────────────────────────────
    @property
    def is_dev(self) -> bool:
        return self.ENV == "dev"

    @property
    def is_prod(self) -> bool:
        return self.ENV == "prod"

    # ── 生产环境关键配置校验 ─────────────────────────────
    @model_validator(mode="after")
    def _validate_prod(self):
        if self.is_prod:
            # 生产环境强制覆盖 DEBUG
            if self.DEBUG:
                print("⚠️  生产环境 (ENV=prod) 已自动关闭 DEBUG")
                self.DEBUG = False
            # 生产环境禁止使用 dev 默认密码
            weak_secrets = {
                "ADMIN_PASSWORD": "pawtrack_admin_2026",
            }
            for key, weak in weak_secrets.items():
                if getattr(self, key) == weak:
                    raise ValueError(
                        f"生产环境 (ENV=prod) 禁止使用默认 {key}={weak}，"
                        f"请通过环境变量或 .env 注入强密码"
                    )
            # 生产环境必须提供 JWT 密钥文件（auth.py 加载时会校验）
            if "localhost" in self.DATABASE_URL:
                raise ValueError(
                    "生产环境 (ENV=prod) DATABASE_URL 不能指向 localhost，"
                    "请通过环境变量注入生产数据库地址"
                )
        return self


settings = Settings()
