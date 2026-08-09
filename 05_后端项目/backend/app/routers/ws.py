"""
宠迹 PawTrack — WebSocket 实时推送端点

端点：GET /ws/v1?token={access_token}

协议：
  Client → Server:
    {"action": "subscribe",   "channel": "location", "pet_id": 123}
    {"action": "subscribe",   "channel": "alarm"}
    {"action": "unsubscribe", "channel": "location", "pet_id": 123}
    {"action": "ping"}

  Server → Client:
    {"type": "connected",  "user_id": 1, "ts": ...}
    {"type": "location",   "pet_id": 123, "device_id": 456, "lat": 31.23, "lng": 121.47, ...}
    {"type": "alarm",      "alarm_id": 1, "pet_id": 123, "alarm_type": "leave_fence", ...}
    {"type": "pong",       "ts": ...}
    {"type": "error",      "code": 40001, "message": "..."}
"""
import json
import time
import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.auth import decode_token
from app.websocket_manager import ws_manager

logger = logging.getLogger("pawtrack.ws.router")
router = APIRouter(tags=["WebSocket"])

# ── 心跳配置 ──────────────────────────────────────────────────

HEARTBEAT_TIMEOUT = 90  # 秒，超过此时间无消息则断开


@router.websocket("/ws/v1")
async def websocket_endpoint(
    ws: WebSocket,
    token: str = Query(..., description="用户 access_token")
):
    """
    WebSocket 实时推送端点

    连接方式：ws://host:8000/ws/v1?token=eyJhbGciOi...

    鉴权：通过 query param 传递 JWT access_token
    （WebSocket 无法使用标准 Authorization Header）
    """
    # ── 1. 鉴权 ──────────────────────────────────────────────
    try:
        payload = decode_token(token)
    except Exception:
        await ws.close(code=4001, reason="Token 无效或已过期")
        return

    # 只允许用户 token，不允许设备 token
    if payload.get("token_type") != "access":
        await ws.close(code=4002, reason="Token 类型错误")
        return

    user_id = int(payload["sub"])

    # ── 2. 接受连接 ──────────────────────────────────────────
    conn = await ws_manager.connect(ws, user_id)

    try:
        # ── 3. 消息接收循环 ──────────────────────────────────
        while conn.is_active:
            try:
                # 设置心跳超时
                raw = await asyncio.wait_for(
                    ws.receive_text(),
                    timeout=HEARTBEAT_TIMEOUT
                )
            except asyncio.TimeoutError:
                # 心跳超时，主动断开
                logger.info(f"心跳超时断开 user={user_id}")
                await conn.send_json({
                    "type": "error",
                    "code": 40003,
                    "message": "心跳超时，连接已断开"
                })
                break

            # 解析客户端消息
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await conn.send_json({
                    "type": "error",
                    "code": 40001,
                    "message": "消息格式错误，需要 JSON"
                })
                continue

            action = msg.get("action")

            if action == "subscribe":
                ws_manager.handle_subscribe(conn, msg)
                await conn.send_json({
                    "type": "ack",
                    "action": "subscribe",
                    "channel": msg.get("channel"),
                    "pet_id": msg.get("pet_id"),
                    "ts": int(time.time())
                })

            elif action == "unsubscribe":
                ws_manager.handle_unsubscribe(conn, msg)
                await conn.send_json({
                    "type": "ack",
                    "action": "unsubscribe",
                    "channel": msg.get("channel"),
                    "pet_id": msg.get("pet_id"),
                    "ts": int(time.time())
                })

            elif action == "ping":
                await conn.send_json({
                    "type": "pong",
                    "ts": int(time.time())
                })

            else:
                await conn.send_json({
                    "type": "error",
                    "code": 40002,
                    "message": f"未知 action: {action}"
                })

    except WebSocketDisconnect:
        logger.info(f"客户端主动断开 user={user_id}")

    except Exception as e:
        logger.error(f"WebSocket 异常 user={user_id}: {e}", exc_info=True)

    finally:
        await ws_manager.disconnect(conn)


# ── 调试端点 ──────────────────────────────────────────────────

@router.get("/ws/v1/stats")
async def ws_stats():
    """WebSocket 连接统计（调试用）"""
    return {"code": 0, "data": ws_manager.get_stats()}
