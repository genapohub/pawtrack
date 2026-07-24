"""
宠迹 PawTrack — WebSocket 连接管理器

架构设计：
  设备上报位置 → location router 写 Redis Stream/GEO + 发布 Redis Pub/Sub
                                                    ↓
  ConnectionManager 后台任务订阅 Redis Pub/Sub → 推送到 WebSocket 客户端

通道设计：
  ws:user:{user_id}           — 该用户的所有实时消息（位置+报警）

客户端协议（Client → Server）：
  {"action": "subscribe",   "channel": "location", "pet_id": 123}
  {"action": "subscribe",   "channel": "alarm"}
  {"action": "unsubscribe", "channel": "location", "pet_id": 123}
  {"action": "ping"}

服务端协议（Server → Client）：
  {"type": "connected",  "user_id": 1}
  {"type": "location",   "pet_id": 123, "device_id": 456, "lat": 31.23, ...}
  {"type": "alarm",      "alarm_id": 1, "pet_id": 123, "alarm_type": "leave_fence", ...}
  {"type": "pong",       "ts": 1721443200}
  {"type": "error",      "code": 40001, "message": "..."}
"""
import asyncio
import json
import time
import logging
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket

logger = logging.getLogger("pawtrack.ws")


class ConnectionInfo:
    """单个 WebSocket 连接的上下文"""
    def __init__(self, ws: WebSocket, user_id: int):
        self.ws = ws
        self.user_id = user_id
        # 订阅的宠物位置更新 pet_id 集合
        self.subscribed_pets: Set[int] = set()
        # 是否订阅报警推送
        self.subscribed_alarm: bool = False
        self.is_active: bool = True

    async def send_json(self, data: dict):
        """安全发送 JSON 消息"""
        if not self.is_active:
            return
        try:
            await self.ws.send_text(json.dumps(data, ensure_ascii=False))
        except Exception as e:
            logger.warning(f"发送消息失败 user={self.user_id}: {e}")
            self.is_active = False


class ConnectionManager:
    """
    全局 WebSocket 连接管理器

    职责：
    1. 维护 user_id → 连接集合 的映射
    2. 启动 Redis Pub/Sub 后台监听任务
    3. 收到 Pub/Sub 消息后，按用户订阅过滤并推送
    """

    def __init__(self):
        # user_id → Set[ConnectionInfo]
        self._connections: Dict[int, Set[ConnectionInfo]] = {}
        # Redis Pub/Sub 后台任务
        self._pubsub_task: Optional[asyncio.Task] = None
        self._redis = None
        self._pubsub = None
        self._is_running = False

    # ── 连接生命周期 ──────────────────────────────────────────

    async def connect(self, ws: WebSocket, user_id: int) -> ConnectionInfo:
        """接受 WebSocket 连接并注册"""
        await ws.accept()
        conn = ConnectionInfo(ws, user_id)

        if user_id not in self._connections:
            self._connections[user_id] = set()
        self._connections[user_id].add(conn)

        logger.info(f"WebSocket 连接建立 user={user_id}, 当前用户连接数={len(self._connections[user_id])}")

        await conn.send_json({
            "type": "connected",
            "user_id": user_id,
            "ts": int(time.time())
        })
        return conn

    async def disconnect(self, conn: ConnectionInfo):
        """断开连接并清理"""
        conn.is_active = False
        user_conns = self._connections.get(conn.user_id)
        if user_conns:
            user_conns.discard(conn)
            if not user_conns:
                del self._connections[conn.user_id]

        logger.info(f"WebSocket 连接断开 user={conn.user_id}")

    # ── 订阅管理 ──────────────────────────────────────────────

    def handle_subscribe(self, conn: ConnectionInfo, msg: dict):
        """处理客户端订阅请求"""
        channel = msg.get("channel")

        if channel == "location":
            pet_id = msg.get("pet_id")
            if pet_id:
                conn.subscribed_pets.add(int(pet_id))
                logger.info(f"user={conn.user_id} 订阅位置 pet_id={pet_id}")
        elif channel == "alarm":
            conn.subscribed_alarm = True
            logger.info(f"user={conn.user_id} 订阅报警")

    def handle_unsubscribe(self, conn: ConnectionInfo, msg: dict):
        """处理客户端取消订阅"""
        channel = msg.get("channel")

        if channel == "location":
            pet_id = msg.get("pet_id")
            if pet_id:
                conn.subscribed_pets.discard(int(pet_id))
                logger.info(f"user={conn.user_id} 取消订阅位置 pet_id={pet_id}")
        elif channel == "alarm":
            conn.subscribed_alarm = False

    # ── 消息推送 ──────────────────────────────────────────────

    async def push_to_user(self, user_id: int, message: dict):
        """
        向指定用户的所有活跃连接推送消息（按订阅过滤）

        调用方：Redis Pub/Sub 监听任务
        """
        user_conns = self._connections.get(user_id)
        if not user_conns:
            return

        msg_type = message.get("type")
        pet_id = message.get("pet_id")

        # 复制一份避免遍历时修改
        dead_conns = []

        for conn in list(user_conns):
            if not conn.is_active:
                dead_conns.append(conn)
                continue

            # 按订阅类型过滤
            if msg_type == "location" and pet_id:
                if pet_id not in conn.subscribed_pets:
                    continue
            elif msg_type == "alarm":
                if not conn.subscribed_alarm:
                    continue

            await conn.send_json(message)

        # 清理死连接
        for conn in dead_conns:
            await self.disconnect(conn)

    # ── Redis Pub/Sub 后台监听 ────────────────────────────────

    async def start(self, redis_client):
        """启动 Redis Pub/Sub 后台监听"""
        if self._is_running:
            return

        self._redis = redis_client
        self._is_running = True

        # 使用 pattern 订阅所有 ws:user:* 频道
        self._pubsub = redis_client.pubsub()
        await self._pubsub.psubscribe("ws:user:*")

        self._pubsub_task = asyncio.create_task(self._listen_pubsub())
        logger.info("WebSocket Pub/Sub 监听已启动")

    async def stop(self):
        """停止后台监听"""
        self._is_running = False
        if self._pubsub_task:
            self._pubsub_task.cancel()
            try:
                await self._pubsub_task
            except asyncio.CancelledError:
                pass
        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.close()
        logger.info("WebSocket Pub/Sub 监听已停止")

    async def _listen_pubsub(self):
        """Redis Pub/Sub 消息监听循环"""
        logger.info("Pub/Sub 监听循环启动")

        while self._is_running:
            try:
                async for message in self._pubsub.listen():
                    if message["type"] != "pmessage":
                        continue

                    # 从 channel 名解析 user_id: ws:user:123
                    channel = message.get("channel", "")
                    try:
                        user_id = int(channel.split(":")[-1])
                    except (ValueError, IndexError):
                        continue

                    # 解析消息体
                    try:
                        data = json.loads(message["data"])
                    except (json.JSONDecodeError, TypeError):
                        continue

                    # 推送给该用户
                    await self.push_to_user(user_id, data)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Pub/Sub 监听异常: {e}", exc_info=True)
                # 重连等待
                await asyncio.sleep(2)
                if self._is_running and self._redis:
                    try:
                        self._pubsub = self._redis.pubsub()
                        await self._pubsub.psubscribe("ws:user:*")
                        logger.info("Pub/Sub 重连成功")
                    except Exception as retry_err:
                        logger.error(f"Pub/Sub 重连失败: {retry_err}")

    # ── 状态查询 ──────────────────────────────────────────────

    def get_stats(self) -> dict:
        """获取连接统计"""
        total = sum(len(conns) for conns in self._connections.values())
        return {
            "total_connections": total,
            "unique_users": len(self._connections),
            "is_running": self._is_running
        }


# ── 全局单例 ──────────────────────────────────────────────────

ws_manager = ConnectionManager()
