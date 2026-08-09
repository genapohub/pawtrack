"""
宠迹 PawTrack — 结构化日志

按环境自动分级：
  - dev：DEBUG，彩色控制台输出，便于本地调试
  - prod：INFO，JSON 格式，便于日志采集（ELK/Loki）

用法：
    from app.logging import logger
    logger.info("消息", extra={"user_id": 123})
"""
import logging
import sys
import json
from datetime import datetime, timezone
from app.config import settings

LOG_FORMAT_DEV = "\033[36m%(asctime)s\033[0m \033[1m%(levelname)-7s\033[0m \033[2m%(name)s\033[0m %(message)s"
LOG_DATE_FMT = "%H:%M:%S"


class JsonFormatter(logging.Formatter):
    """生产环境 JSON 日志格式"""

    def format(self, record: logging.LogRecord) -> str:
        log = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # 合并 extra 字段
        for k, v in record.__dict__.items():
            if k in {"args", "msg", "levelname", "levelno", "pathname", "filename",
                     "module", "exc_info", "exc_text", "stack_info", "lineno",
                     "funcName", "created", "msecs", "relativeCreated", "thread",
                     "threadName", "processName", "process", "name", "message"}:
                continue
            log[k] = v
        if record.exc_info:
            log["exc"] = self.formatException(record.exc_info)
        return json.dumps(log, ensure_ascii=False, default=str)


def setup_logging() -> None:
    """初始化根日志配置（按环境分级）"""
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if settings.is_dev else logging.INFO)
    # 清除已存在 handler（避免重复）
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    if settings.is_dev:
        handler.setFormatter(logging.Formatter(LOG_FORMAT_DEV, datefmt=LOG_DATE_FMT))
    else:
        handler.setFormatter(JsonFormatter())
    root.addHandler(handler)

    # 降低第三方库噪音
    for noisy in ("uvicorn.access", "sqlalchemy.engine", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING if settings.is_prod else logging.INFO)


# 模块级 logger，供各模块直接导入使用
logger = logging.getLogger("pawtrack")

# 导入即初始化
setup_logging()
