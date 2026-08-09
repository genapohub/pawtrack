"""
宠迹 PawTrack — 社交碰头路由（Sprint 2）

功能：
1. 发起碰头（发现附近宠物 → 发起碰头请求）
2. 确认碰头
3. 完成碰头（双方到场 → 积分奖励）
4. 取消碰头
5. 碰头记录列表
6. 附近宠物查询（Redis GEO）
"""
import json
import time
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

from app.database import get_db
from app.models import Meet, Pet, Device, User, MeetStatus, PetType, PointType, PointsLog
from app.auth import get_current_user
from app import main as app_main

router = APIRouter(prefix="/api/v1/social", tags=["社交"])

# ── 请求模型 ──────────────────────────────────────────────

class MeetCreateRequest(BaseModel):
    receiver_pet_id: int
    start_lat: float = Field(..., ge=-90, le=90)
    start_lng: float = Field(..., ge=-180, le=180)

class MeetConfirmRequest(BaseModel):
    end_lat: Optional[float] = None
    end_lng: Optional[float] = None

class MeetCompleteRequest(BaseModel):
    """完成碰头（双方确认到场）"""
    pass

# ── 工具函数 ──────────────────────────────────────────────

def _meet_to_dict(meet: Meet) -> dict:
    return {
        "id": meet.id,
        "initiator_pet_id": meet.initiator_pet_id,
        "receiver_pet_id": meet.receiver_pet_id,
        "status": meet.status.value,
        "start_lat": float(meet.start_lat) if meet.start_lat else None,
        "start_lng": float(meet.start_lng) if meet.start_lng else None,
        "end_lat": float(meet.end_lat) if meet.end_lat else None,
        "end_lng": float(meet.end_lng) if meet.end_lng else None,
        "points_awarded": meet.points_awarded,
        "started_at": meet.started_at.isoformat() if meet.started_at else None,
        "confirmed_at": meet.confirmed_at.isoformat() if meet.confirmed_at else None,
        "completed_at": meet.completed_at.isoformat() if meet.completed_at else None,
        "created_at": meet.created_at.isoformat() if meet.created_at else ""
    }

async def _award_points(db: AsyncSession, user_id: int, change: int, point_type: PointType, related_id: str = ""):
    """发放积分并记录"""
    # 查询当前余额
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        return

    new_balance = user.points + change
    user.points = new_balance

    log = PointsLog(
        user_id=user_id,
        change=change,
        type=point_type,
        related_id=related_id,
        balance=new_balance
    )
    db.add(log)

# ── 接口实现 ──────────────────────────────────────────────

@router.get("/nearby", response_model=dict)
async def find_nearby_pets(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius: int = Query(1000, ge=100, le=5000, description="搜索半径（米）"),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """查找附近宠物（Redis GEO 查询）"""
    if not redis_client:
        return {"code": 0, "data": []}

    # Redis GEORADIUS 查询附近设备
    nearby = await app_main.redis_client.georadius(
        "location:geo:nearby",
        lng, lat, radius,
        unit="m",
        withcoord=True,
        withdist=True,
        sort="ASC",
        count=20
    )

    if not nearby:
        return {"code": 0, "data": []}

    results = []
    for item in nearby:
        device_id_str, (lng_val, lat_val), dist = item
        device_id = int(device_id_str)

        # 查询设备→宠物信息
        dev_result = await db.execute(
            select(Device, Pet).join(Pet, Device.pet_id == Pet.id).where(Device.id == device_id)
        )
        row = dev_result.first()
        if not row:
            continue

        device, pet = row
        # 排除自己的宠物
        if pet.user_id == int(user["sub"]):
            continue

        results.append({
            "device_id": device.id,
            "pet_id": pet.id,
            "pet_name": pet.name,
            "pet_type": pet.type.value,
            "pet_avatar": pet.avatar,
            "distance": round(dist, 1),
            "lat": lat_val,
            "lng": lng_val
        })

    return {"code": 0, "data": results}

@router.post("/meets", response_model=dict)
async def create_meet(
    body: MeetCreateRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """发起碰头"""
    # 验证发起方宠物属于当前用户
    initiator_result = await db.execute(
        select(Pet).where(Pet.id == body.receiver_pet_id)
    )
    receiver_pet = initiator_result.scalar_one_or_none()
    if not receiver_pet:
        raise HTTPException(404, detail={"code": 40001, "message": "目标宠物不存在"})

    # 查询当前用户的第一只宠物作为发起方
    my_pet_result = await db.execute(
        select(Pet).where(Pet.user_id == int(user["sub"]), Pet.status == "active").limit(1)
    )
    my_pet = my_pet_result.scalar_one_or_none()
    if not my_pet:
        raise HTTPException(400, detail={"code": 40002, "message": "请先添加宠物"})

    if my_pet.id == body.receiver_pet_id:
        raise HTTPException(400, detail={"code": 40003, "message": "不能和自己碰头"})

    # 检查是否已有进行中的碰头
    existing = await db.execute(
        select(Meet).where(
            Meet.initiator_pet_id == my_pet.id,
            Meet.receiver_pet_id == body.receiver_pet_id,
            Meet.status.in_([MeetStatus.pending, MeetStatus.confirmed])
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, detail={"code": 40004, "message": "已有进行中的碰头请求"})

    meet = Meet(
        initiator_pet_id=my_pet.id,
        receiver_pet_id=body.receiver_pet_id,
        status=MeetStatus.pending,
        start_lat=body.start_lat,
        start_lng=body.start_lng,
        started_at=datetime.now(timezone.utc)
    )
    db.add(meet)
    await db.commit()
    await db.refresh(meet)

    # 推送通知给对方宠物主人
    if redis_client:
        ws_msg = json.dumps({
            "type": "alarm",
            "alarm_type": "meet_request",
            "pet_id": body.receiver_pet_id,
            "meet_id": meet.id,
            "ts": int(time.time())
        }, ensure_ascii=False)
        await app_main.redis_client.publish(f"ws:user:{receiver_pet.user_id}", ws_msg)

    return {"code": 0, "data": _meet_to_dict(meet)}

@router.put("/meets/{meet_id}/confirm", response_model=dict)
async def confirm_meet(
    meet_id: int,
    body: MeetConfirmRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """确认碰头（接收方确认）"""
    result = await db.execute(select(Meet).where(Meet.id == meet_id))
    meet = result.scalar_one_or_none()
    if not meet:
        raise HTTPException(404, detail={"code": 40005, "message": "碰头记录不存在"})

    if meet.status != MeetStatus.pending:
        raise HTTPException(400, detail={"code": 40006, "message": "该碰头已处理"})

    # 验证当前用户是接收方宠物的主人
    receiver_result = await db.execute(select(Pet).where(Pet.id == meet.receiver_pet_id))
    receiver_pet = receiver_result.scalar_one_or_none()
    if not receiver_pet or receiver_pet.user_id != int(user["sub"]):
        raise HTTPException(403, detail={"code": 40007, "message": "无权操作"})

    meet.status = MeetStatus.confirmed
    meet.confirmed_at = datetime.now(timezone.utc)
    if body.end_lat and body.end_lng:
        meet.end_lat = body.end_lat
        meet.end_lng = body.end_lng
    await db.commit()
    await db.refresh(meet)

    return {"code": 0, "data": _meet_to_dict(meet)}

@router.put("/meets/{meet_id}/complete", response_model=dict)
async def complete_meet(
    meet_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """完成碰头（发放积分奖励）"""
    result = await db.execute(select(Meet).where(Meet.id == meet_id))
    meet = result.scalar_one_or_none()
    if not meet:
        raise HTTPException(404, detail={"code": 40005, "message": "碰头记录不存在"})

    if meet.status != MeetStatus.confirmed:
        raise HTTPException(400, detail={"code": 40008, "message": "请先确认碰头"})

    meet.status = MeetStatus.success
    meet.completed_at = datetime.now(timezone.utc)

    # 积分奖励：狗狗碰头 10 分，猫咪碰头 5 分
    initiator_pet = (await db.execute(select(Pet).where(Pet.id == meet.initiator_pet_id))).scalar_one()
    receiver_pet = (await db.execute(select(Pet).where(Pet.id == meet.receiver_pet_id))).scalar_one()

    points = 10 if initiator_pet.type == PetType.dog else 5
    meet.points_awarded = points

    # 双方各得积分
    await _award_points(db, initiator_pet.user_id, points, PointType.meet, str(meet.id))
    await _award_points(db, receiver_pet.user_id, points, PointType.meet, str(meet.id))

    await db.commit()
    await db.refresh(meet)

    return {"code": 0, "data": _meet_to_dict(meet)}

@router.put("/meets/{meet_id}/cancel", response_model=dict)
async def cancel_meet(
    meet_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """取消碰头"""
    result = await db.execute(select(Meet).where(Meet.id == meet_id))
    meet = result.scalar_one_or_none()
    if not meet:
        raise HTTPException(404, detail={"code": 40005, "message": "碰头记录不存在"})

    if meet.status not in [MeetStatus.pending, MeetStatus.confirmed]:
        raise HTTPException(400, detail={"code": 40009, "message": "该碰头已结束"})

    meet.status = MeetStatus.cancelled
    await db.commit()

    return {"code": 0, "message": "success"}

@router.get("/meets", response_model=dict)
async def list_meets(
    status: Optional[MeetStatus] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """碰头记录列表"""
    # 查询当前用户所有宠物的碰头记录
    pet_ids_subquery = select(Pet.id).where(Pet.user_id == int(user["sub"]))
    conditions = [
        Meet.initiator_pet_id.in_(pet_ids_subquery) | Meet.receiver_pet_id.in_(pet_ids_subquery)
    ]
    if status:
        conditions.append(Meet.status == status)

    count_result = await db.execute(
        select(func.count()).where(*conditions).select_from(Meet)
    )
    total = count_result.scalar()

    result = await db.execute(
        select(Meet)
        .where(*conditions)
        .order_by(Meet.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    meets = result.scalars().all()

    return {
        "code": 0,
        "data": [_meet_to_dict(m) for m in meets],
        "pagination": {"page": page, "size": size, "total": total}
    }
