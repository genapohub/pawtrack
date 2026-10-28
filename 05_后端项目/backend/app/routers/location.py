"""
宠迹 PawTrack — 定位数据路由
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.database import get_db
from app.models import Pet, Device, User, MemberLevel
from app.auth import get_current_user
from app import main as app_main

router = APIRouter(prefix="/api/v1/location", tags=["定位"])

# ── 请求模型 ──────────────────────────────────────────────

class LocationUploadRequest(BaseModel):
    device_id: int
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    bearing: Optional[float] = Field(None, ge=0, le=360)
    source: str = "gps"
    is_indoor: bool = False
    battery: int = Field(100, ge=0, le=100)
    ts: int  # 设备端时间戳

class RealtimeLocationResponse(BaseModel):
    device_id: int
    pet_id: int
    lat: float
    lng: float
    accuracy: Optional[float]
    source: str
    battery: int
    ts: int

_mongo_client: Optional[AsyncIOMotorClient] = None


def _locations_collection():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    return _mongo_client.get_default_database()["locations"]


# ── 接口实现 ──────────────────────────────────────────────

@router.post("/upload", response_model=dict)
async def upload_location(
    body: LocationUploadRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """设备定位数据上报；生产要求设备 JWT，开发允许归属用户模拟上报"""
    result = await db.execute(select(Device).where(Device.id == body.device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(404, detail={"code": 20003, "message": "设备不存在"})

    is_device_token = user.get("member_level") == "device" and int(user["sub"]) == body.device_id
    is_owner_simulation = settings.is_dev and device.user_id == int(user["sub"])
    if not is_device_token and not is_owner_simulation:
        raise HTTPException(403, detail={"code": 20008, "message": "无权上报该设备定位"})

    # 1. 写入 Redis Stream（缓冲层，所有字段 string）
    stream_data_full = {
        "device_id": str(body.device_id),
        "pet_id": str(device.pet_id or 0),
        "user_id": str(device.user_id or 0),
        "lat": str(body.lat),
        "lng": str(body.lng),
        "accuracy": str(body.accuracy) if body.accuracy else "",
        "altitude": str(body.altitude) if body.altitude else "",
        "speed": str(body.speed) if body.speed else "",
        "source": body.source,
        "is_indoor": "1" if body.is_indoor else "0",
        "battery": str(body.battery),
        "ts": str(body.ts)
    }

    await app_main.redis_client.xadd(
        "location:stream",
        stream_data_full,
        maxlen=1000000,
        approximate=True
    )

    # 2. 更新 Redis GEO（实时查询用）
    await app_main.redis_client.geoadd("location:geo:nearby", (body.lng, body.lat, str(body.device_id)))

    await _locations_collection().insert_one({
        "device_id": body.device_id,
        "pet_id": device.pet_id,
        "user_id": device.user_id,
        "lat": body.lat,
        "lng": body.lng,
        "accuracy": body.accuracy,
        "altitude": body.altitude,
        "speed": body.speed,
        "source": body.source,
        "is_indoor": body.is_indoor,
        "battery": body.battery,
        "ts": body.ts,
        "created_at": datetime.now(timezone.utc),
    })

    # 3. 更新设备在线状态
    device.last_online_at = datetime.now(timezone.utc)
    device.battery_level = body.battery
    if device.status == "offline":
        device.status = "online"
    await db.commit()

    # 4. 发布 Redis Pub/Sub（推送到 WebSocket 客户端）
    if device.user_id:
        ws_message = json.dumps({
            "type": "location",
            "pet_id": device.pet_id,
            "device_id": body.device_id,
            "lat": body.lat,
            "lng": body.lng,
            "accuracy": body.accuracy,
            "source": body.source,
            "battery": body.battery,
            "ts": body.ts
        }, ensure_ascii=False)
        await app_main.redis_client.publish(f"ws:user:{device.user_id}", ws_message)

    return {"code": 0, "message": "success"}

@router.get("/realtime/{pet_id}", response_model=dict)
async def get_realtime_location(
    pet_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取宠物实时位置"""
    # 验证宠物属于当前用户
    result = await db.execute(select(Pet).where(Pet.id == pet_id, Pet.user_id == int(user["sub"])))
    pet = result.scalar_one_or_none()
    if not pet:
        raise HTTPException(404, detail={"code": 20002, "message": "宠物不存在"})

    # 从设备关联表获取设备
    device_result = await db.execute(select(Device).where(Device.pet_id == pet_id))
    device = device_result.scalar_one_or_none()
    if not device:
        raise HTTPException(404, detail={"code": 20003, "message": "该宠物未绑定设备"})

    # 从 Redis GEO 获取最新位置
    geo_result = await app_main.redis_client.geopos("location:geo:nearby", str(device.id))
    if geo_result and geo_result[0]:
        lng, lat = geo_result[0]
        return {"code": 0, "data": {
            "device_id": device.id,
            "pet_id": pet_id,
            "lat": lat,
            "lng": lng,
            "source": "gps",
            "battery": device.battery_level,
            "ts": int(datetime.now(timezone.utc).timestamp())
        }}

    return {"code": 0, "data": {
        "device_id": device.id,
        "pet_id": pet_id,
        "lat": None,
        "lng": None,
        "source": "none",
        "battery": device.battery_level,
        "ts": 0
    }}

@router.get("/history/{pet_id}", response_model=dict)
async def get_location_history(
    pet_id: int,
    start: Optional[int] = None,
    end: Optional[int] = None,
    interval: int = 60,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取历史轨迹（免费7天，会员永久）"""
    result = await db.execute(select(Pet).where(Pet.id == pet_id, Pet.user_id == int(user["sub"])))
    pet = result.scalar_one_or_none()
    if not pet:
        raise HTTPException(404, detail={"code": 20002, "message": "宠物不存在"})

    device_result = await db.execute(select(Device).where(Device.pet_id == pet_id))
    device = device_result.scalar_one_or_none()
    if not device:
        raise HTTPException(404, detail={"code": 20003, "message": "该宠物未绑定设备"})

    owner_result = await db.execute(select(User).where(User.id == int(user["sub"])))
    owner = owner_result.scalar_one_or_none()
    if owner and owner.member_level == MemberLevel.free:
        retention_start = int((datetime.now(timezone.utc) - timedelta(days=7)).timestamp())
        start = max(start or 0, retention_start)

    query = {"device_id": device.id}
    if start is not None:
        query["ts"] = {"$gte": start}
    if end is not None:
        query.setdefault("ts", {})["$lte"] = end

    collection = _locations_collection()
    total = await collection.count_documents(query)
    cursor = collection.find(
        query,
        {"_id": 0, "ts": 1, "lat": 1, "lng": 1, "accuracy": 1, "source": 1, "battery": 1},
    ).sort("ts", 1).limit(500)
    items = await cursor.to_list(length=500)
    return {"code": 0, "data": items, "pagination": {"total": total}}
