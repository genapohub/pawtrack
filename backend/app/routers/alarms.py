"""
宠迹 PawTrack — 报警管理路由（Sprint 2）

功能：
1. 报警列表查询（按宠物/按状态筛选）
2. 报警详情
3. 处理报警（确认/标记误报）
4. 围栏报警自动检测（PostGIS ST_DWithin）
5. 低电量报警触发
6. WebSocket Pub/Sub 推送报警通知
"""
import json
import time
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, update
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

from app.database import get_db
from app.models import Alarm, Pet, Device, AlarmType, AlarmSeverity, AlarmStatus
from app.auth import get_current_user
from app.main import redis_client

router = APIRouter(prefix="/api/v1/alarms", tags=["报警"])

# ── 请求模型 ──────────────────────────────────────────────

class AlarmHandleRequest(BaseModel):
    status: AlarmStatus = Field(..., description="handled 或 false_positive")
    note: Optional[str] = Field(None, max_length=200)

class FenceCheckRequest(BaseModel):
    """围栏检测触发（内部调用）"""
    device_id: int
    lat: float
    lng: float

# ── 工具函数 ──────────────────────────────────────────────

def _alarm_to_dict(alarm: Alarm) -> dict:
    return {
        "id": alarm.id,
        "pet_id": alarm.pet_id,
        "device_id": alarm.device_id,
        "type": alarm.type.value,
        "severity": alarm.severity.value,
        "lat": float(alarm.lat) if alarm.lat else None,
        "lng": float(alarm.lng) if alarm.lng else None,
        "address": alarm.address,
        "status": alarm.status.value,
        "handled_at": alarm.handled_at.isoformat() if alarm.handled_at else None,
        "created_at": alarm.created_at.isoformat() if alarm.created_at else ""
    }

async def _create_alarm(
    db: AsyncSession,
    pet_id: int,
    user_id: int,
    device_id: int,
    alarm_type: AlarmType,
    severity: AlarmSeverity,
    lat: float = None,
    lng: float = None,
    publish_ws: bool = True
) -> Alarm:
    """创建报警记录并推送 WebSocket 通知"""
    alarm = Alarm(
        pet_id=pet_id,
        user_id=user_id,
        device_id=device_id,
        type=alarm_type,
        severity=severity,
        lat=lat,
        lng=lng,
        status=AlarmStatus.active
    )
    db.add(alarm)
    await db.commit()
    await db.refresh(alarm)

    # 推送 WebSocket 通知
    if publish_ws and redis_client:
        ws_msg = json.dumps({
            "type": "alarm",
            "alarm_id": alarm.id,
            "pet_id": pet_id,
            "alarm_type": alarm_type.value,
            "severity": severity.value,
            "lat": lat,
            "lng": lng,
            "ts": int(time.time())
        }, ensure_ascii=False)
        await redis_client.publish(f"ws:user:{user_id}", ws_msg)

    return alarm

# ── 接口实现 ──────────────────────────────────────────────

@router.get("", response_model=dict)
async def list_alarms(
    pet_id: Optional[int] = None,
    status: Optional[AlarmStatus] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """报警列表（分页）"""
    conditions = [Alarm.user_id == int(user["sub"])]
    if pet_id:
        conditions.append(Alarm.pet_id == pet_id)
    if status:
        conditions.append(Alarm.status == status)

    # 总数
    count_result = await db.execute(
        select(func.count()).where(*conditions).select_from(Alarm)
    )
    total = count_result.scalar()

    # 分页查询
    result = await db.execute(
        select(Alarm)
        .where(*conditions)
        .order_by(Alarm.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    alarms = result.scalars().all()

    return {
        "code": 0,
        "data": [_alarm_to_dict(a) for a in alarms],
        "pagination": {"page": page, "size": size, "total": total}
    }

@router.get("/{alarm_id}", response_model=dict)
async def get_alarm(alarm_id: int, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """报警详情"""
    result = await db.execute(
        select(Alarm).where(Alarm.id == alarm_id, Alarm.user_id == int(user["sub"]))
    )
    alarm = result.scalar_one_or_none()
    if not alarm:
        raise HTTPException(404, detail={"code": 30001, "message": "报警记录不存在"})
    return {"code": 0, "data": _alarm_to_dict(alarm)}

@router.put("/{alarm_id}/handle", response_model=dict)
async def handle_alarm(
    alarm_id: int,
    body: AlarmHandleRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """处理报警（确认/标记误报）"""
    result = await db.execute(
        select(Alarm).where(Alarm.id == alarm_id, Alarm.user_id == int(user["sub"]))
    )
    alarm = result.scalar_one_or_none()
    if not alarm:
        raise HTTPException(404, detail={"code": 30001, "message": "报警记录不存在"})

    if alarm.status != AlarmStatus.active:
        raise HTTPException(400, detail={"code": 30002, "message": "该报警已处理"})

    alarm.status = body.status
    alarm.handled_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(alarm)

    return {"code": 0, "data": _alarm_to_dict(alarm)}

@router.get("/unread/count", response_model=dict)
async def get_unread_count(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """未处理报警数量（App 红点用）"""
    result = await db.execute(
        select(func.count())
        .where(Alarm.user_id == int(user["sub"]), Alarm.status == AlarmStatus.active)
        .select_from(Alarm)
    )
    count = result.scalar()
    return {"code": 0, "data": {"count": count}}

# ── 围栏检测（内部接口，由定位消费者调用）──────────────────

@router.post("/fence-check", response_model=dict)
async def check_fence(
    body: FenceCheckRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    围栏检测：检查设备是否离开安全围栏
    使用 PostGIS ST_DWithin 空间查询
    """
    # 查询设备关联的宠物
    result = await db.execute(select(Device).where(Device.id == body.device_id))
    device = result.scalar_one_or_none()
    if not device or not device.pet_id:
        return {"code": 0, "message": "设备未绑定宠物，跳过"}

    # 查询宠物围栏设置
    pet_result = await db.execute(
        select(Pet).where(Pet.id == device.pet_id, Pet.fence_enabled.is_(True))
    )
    pet = pet_result.scalar_one_or_none()
    if not pet or not pet.fence_center:
        return {"code": 0, "message": "围栏未开启，跳过"}

    # PostGIS 空间查询：设备位置是否在围栏内
    sql = text("""
        SELECT ST_DWithin(
            fence_center,
            ST_MakePoint(:lng, :lat)::geography,
            :radius
        ) AS is_within
        FROM pets
        WHERE id = :pet_id
    """)
    geo_result = await db.execute(sql, {
        "lng": body.lng,
        "lat": body.lat,
        "radius": pet.fence_radius,
        "pet_id": pet.id
    })
    row = geo_result.fetchone()

    if row and not row.is_within:
        # 离开围栏，创建报警
        alarm_type = AlarmType.leave_fence_cat if pet.type.value == "cat" else AlarmType.leave_fence
        await _create_alarm(
            db=db,
            pet_id=pet.id,
            user_id=pet.user_id,
            device_id=device.id,
            alarm_type=alarm_type,
            severity=AlarmSeverity.high,
            lat=body.lat,
            lng=body.lng
        )
        return {"code": 0, "data": {"triggered": True, "type": alarm_type.value}}

    return {"code": 0, "data": {"triggered": False}}

# ── 低电量报警（内部接口，由设备状态更新触发）──────────────

@router.post("/battery-check/{device_id}", response_model=dict)
async def check_battery(
    device_id: int,
    battery: int = Query(..., ge=0, le=100),
    db: AsyncSession = Depends(get_db)
):
    """低电量报警检测"""
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    if not device or not device.pet_id:
        return {"code": 0, "message": "跳过"}

    # 检查是否已有未处理的低电量报警（避免重复）
    existing = await db.execute(
        select(Alarm).where(
            Alarm.device_id == device_id,
            Alarm.type.in_([AlarmType.low_battery, AlarmType.low_battery_critical]),
            Alarm.status == AlarmStatus.active
        )
    )
    if existing.scalar_one_or_none():
        return {"code": 0, "message": "已有未处理低电量报警，跳过"}

    # 低于 20% 紧急，低于 40% 提醒
    if battery <= 20:
        await _create_alarm(
            db=db,
            pet_id=device.pet_id,
            user_id=device.user_id,
            device_id=device_id,
            alarm_type=AlarmType.low_battery_critical,
            severity=AlarmSeverity.high
        )
    elif battery <= 40:
        await _create_alarm(
            db=db,
            pet_id=device.pet_id,
            user_id=device.user_id,
            device_id=device_id,
            alarm_type=AlarmType.low_battery,
            severity=AlarmSeverity.medium
        )

    return {"code": 0, "message": "checked"}


# ── 报警设置 ──────────────────────────────────────────────

class AlarmSettingsRequest(BaseModel):
    """报警设置（按用户级，存 Redis）"""
    leave_fence_notify: bool = True       # 离开围栏推送
    enter_fence_notify: bool = False      # 进入围栏推送
    low_battery_threshold: int = Field(20, ge=5, le=50)  # 低电量阈值
    quiet_hours_start: Optional[str] = None  # 免打扰开始 HH:MM
    quiet_hours_end: Optional[str] = None    # 免打扰结束 HH:MM

ALARM_SETTINGS_KEY = "alarm:settings:user:{user_id}"


@router.get("/settings", response_model=dict)
async def get_alarm_settings(user: dict = Depends(get_current_user)):
    """获取报警设置"""
    from app.main import redis_client
    key = ALARM_SETTINGS_KEY.format(user_id=user["sub"])
    if redis_client:
        raw = await redis_client.get(key)
        if raw:
            return {"code": 0, "data": json.loads(raw)}
    # 默认设置
    return {"code": 0, "data": AlarmSettingsRequest().model_dump()}


@router.put("/settings", response_model=dict)
async def update_alarm_settings(body: AlarmSettingsRequest, user: dict = Depends(get_current_user)):
    """更新报警设置"""
    from app.main import redis_client
    key = ALARM_SETTINGS_KEY.format(user_id=user["sub"])
    data = body.model_dump()
    if redis_client:
        await redis_client.set(key, json.dumps(data, ensure_ascii=False))
    return {"code": 0, "message": "报警设置已更新", "data": data}
