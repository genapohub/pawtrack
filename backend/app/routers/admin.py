"""
宠迹 PawTrack — 后台管理路由（Sprint 3）

功能：
1. 管理员登录（用户名+密码，签发 admin JWT）
2. 数据概览（用户/宠物/设备/报警/订单/碰头 统计）
3. 用户管理（列表/封禁/解封）
4. 宠物管理（列表）
5. 设备管理（列表）
6. 报警管理（列表/规则占位）
7. 订单管理（列表/退款占位）
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta

from app.database import get_db
from app.models import User, Pet, Device, Alarm, Order, Meet, Subscription, AlarmStatus, OrderStatus
from app.auth import create_admin_token, get_admin_user
from app.config import settings

router = APIRouter(prefix="/api/v1/admin", tags=["后台管理"])


# ── 请求模型 ──────────────────────────────────────────────

class AdminLoginRequest(BaseModel):
    username: str
    password: str


# ── 登录 ──────────────────────────────────────────────

@router.post("/login", response_model=dict)
async def admin_login(body: AdminLoginRequest):
    """管理员登录"""
    if body.username != settings.ADMIN_USERNAME or body.password != settings.ADMIN_PASSWORD:
        raise HTTPException(401, detail={"code": 10004, "message": "用户名或密码错误"})
    token = create_admin_token(body.username)
    return {
        "code": 0,
        "data": {
            "access_token": token,
            "token_type": "Bearer",
            "username": body.username,
            "role": "super_admin",
            "expires_in": settings.ADMIN_TOKEN_EXPIRE_SECONDS
        }
    }


# ── 数据概览 ──────────────────────────────────────────────

@router.get("/dashboard", response_model=dict)
async def dashboard(
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """数据概览"""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    user_count = (await db.execute(select(func.count()).select_from(User))).scalar()
    pet_count = (await db.execute(select(func.count()).select_from(Pet).where(Pet.status == "active"))).scalar()
    device_count = (await db.execute(select(func.count()).select_from(Device))).scalar()
    online_devices = (await db.execute(
        select(func.count()).select_from(Device).where(Device.status == "online")
    )).scalar()
    active_alarms = (await db.execute(
        select(func.count()).select_from(Alarm).where(Alarm.status == AlarmStatus.active)
    )).scalar()
    today_alarms = (await db.execute(
        select(func.count()).select_from(Alarm).where(Alarm.created_at >= today_start)
    )).scalar()
    paid_orders = (await db.execute(
        select(func.count()).select_from(Order).where(Order.status == OrderStatus.paid)
    )).scalar()
    revenue = (await db.execute(
        select(func.coalesce(func.sum(Order.amount), 0)).where(Order.status == OrderStatus.paid)
    )).scalar()
    meet_count = (await db.execute(select(func.count()).select_from(Meet))).scalar()
    success_meets = (await db.execute(
        select(func.count()).select_from(Meet).where(Meet.status == "success")
    )).scalar()
    active_subs = (await db.execute(
        select(func.count()).select_from(Subscription).where(Subscription.status == "active")
    )).scalar()

    return {
        "code": 0,
        "data": {
            "users": user_count,
            "pets": pet_count,
            "devices": device_count,
            "online_devices": online_devices,
            "active_alarms": active_alarms,
            "today_alarms": today_alarms,
            "paid_orders": paid_orders,
            "revenue": float(revenue or 0),
            "meets": meet_count,
            "success_meets": success_meets,
            "active_subs": active_subs
        }
    }


# ── 用户管理 ──────────────────────────────────────────────

@router.get("/users", response_model=dict)
async def list_users(
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    conditions = []
    if keyword:
        conditions.append((User.phone.contains(keyword)) | (User.nickname.contains(keyword)))
    if status:
        conditions.append(User.status == status)

    where = conditions if conditions else [func.true()]
    total = (await db.execute(select(func.count()).select_from(User).where(*where))).scalar()
    rows = (await db.execute(
        select(User).where(*where).order_by(User.created_at.desc())
        .offset((page - 1) * size).limit(size)
    )).scalars().all()

    return {
        "code": 0,
        "data": [{
            "id": u.id, "phone": u.phone, "nickname": u.nickname,
            "member_level": u.member_level.value if u.member_level else "free",
            "member_expire_at": u.member_expire_at.isoformat() if u.member_expire_at else None,
            "points": u.points, "status": u.status,
            "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
            "created_at": u.created_at.isoformat() if u.created_at else ""
        } for u in rows],
        "pagination": {"page": page, "size": size, "total": total}
    }


@router.put("/users/{user_id}/ban", response_model=dict)
async def ban_user(
    user_id: int,
    action: str = Query("ban", regex="^(ban|unban)$"),
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """封禁/解封用户"""
    new_status = "blocked" if action == "ban" else "active"
    await db.execute(update(User).where(User.id == user_id).values(status=new_status))
    await db.commit()
    return {"code": 0, "message": f"已{'封禁' if action == 'ban' else '解封'}用户"}


# ── 宠物管理 ──────────────────────────────────────────────

@router.get("/pets", response_model=dict)
async def list_pets(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    total = (await db.execute(select(func.count()).select_from(Pet))).scalar()
    rows = (await db.execute(
        select(Pet).order_by(Pet.created_at.desc()).offset((page - 1) * size).limit(size)
    )).scalars().all()

    return {
        "code": 0,
        "data": [{
            "id": p.id, "user_id": p.user_id, "name": p.name,
            "type": p.type.value, "breed": p.breed, "gender": p.gender.value if p.gender else None,
            "fence_enabled": p.fence_enabled, "fence_radius": p.fence_radius,
            "status": p.status, "created_at": p.created_at.isoformat() if p.created_at else ""
        } for p in rows],
        "pagination": {"page": page, "size": size, "total": total}
    }


# ── 设备管理 ──────────────────────────────────────────────

@router.get("/devices", response_model=dict)
async def list_devices(
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    conditions = []
    if keyword:
        conditions.append(Device.sn.contains(keyword))
    if status:
        conditions.append(Device.status == status)
    where = conditions if conditions else [func.true()]

    total = (await db.execute(select(func.count()).select_from(Device).where(*where))).scalar()
    rows = (await db.execute(
        select(Device).where(*where).order_by(Device.created_at.desc())
        .offset((page - 1) * size).limit(size)
    )).scalars().all()

    return {
        "code": 0,
        "data": [{
            "id": d.id, "sn": d.sn, "user_id": d.user_id, "pet_id": d.pet_id,
            "hardware_type": d.hardware_type, "firmware_version": d.firmware_version,
            "battery_level": d.battery_level, "status": d.status.value if d.status else None,
            "last_online_at": d.last_online_at.isoformat() if d.last_online_at else None,
            "created_at": d.created_at.isoformat() if d.created_at else ""
        } for d in rows],
        "pagination": {"page": page, "size": size, "total": total}
    }


# ── 报警管理 ──────────────────────────────────────────────

@router.get("/alarms", response_model=dict)
async def list_alarms(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    conditions = []
    if status:
        conditions.append(Alarm.status == status)
    where = conditions if conditions else [func.true()]

    total = (await db.execute(select(func.count()).select_from(Alarm).where(*where))).scalar()
    rows = (await db.execute(
        select(Alarm).where(*where).order_by(Alarm.created_at.desc())
        .offset((page - 1) * size).limit(size)
    )).scalars().all()

    return {
        "code": 0,
        "data": [{
            "id": a.id, "pet_id": a.pet_id, "user_id": a.user_id, "device_id": a.device_id,
            "type": a.type.value, "severity": a.severity.value,
            "lat": float(a.lat) if a.lat else None, "lng": float(a.lng) if a.lng else None,
            "address": a.address, "status": a.status.value,
            "handled_at": a.handled_at.isoformat() if a.handled_at else None,
            "created_at": a.created_at.isoformat() if a.created_at else ""
        } for a in rows],
        "pagination": {"page": page, "size": size, "total": total}
    }


@router.put("/alarms/rules", response_model=dict)
async def update_alarm_rules(
    admin: dict = Depends(get_admin_user)
):
    """报警规则配置（占位）"""
    return {"code": 0, "message": "报警规则配置已保存（MVP 占位）"}


# ── 订单管理 ──────────────────────────────────────────────

@router.get("/orders", response_model=dict)
async def list_orders(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    conditions = []
    if status:
        conditions.append(Order.status == status)
    where = conditions if conditions else [func.true()]

    total = (await db.execute(select(func.count()).select_from(Order).where(*where))).scalar()
    rows = (await db.execute(
        select(Order).where(*where).order_by(Order.created_at.desc())
        .offset((page - 1) * size).limit(size)
    )).scalars().all()

    return {
        "code": 0,
        "data": [{
            "id": o.id, "order_no": o.order_no, "user_id": o.user_id,
            "type": o.type, "product_id": o.product_id, "amount": float(o.amount),
            "status": o.status.value, "pay_channel": o.pay_channel.value if o.pay_channel else None,
            "transaction_id": o.transaction_id,
            "paid_at": o.paid_at.isoformat() if o.paid_at else None,
            "created_at": o.created_at.isoformat() if o.created_at else ""
        } for o in rows],
        "pagination": {"page": page, "size": size, "total": total}
    }


@router.put("/orders/{order_no}/refund", response_model=dict)
async def refund_order(
    order_no: str,
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """退款审批（占位）"""
    result = await db.execute(select(Order).where(Order.order_no == order_no))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(404, detail={"code": 40001, "message": "订单不存在"})
    if order.status != OrderStatus.paid:
        raise HTTPException(400, detail={"code": 40002, "message": "仅已支付订单可退款"})

    order.status = OrderStatus.refunded
    await db.commit()
    return {"code": 0, "message": "退款已审批通过（MVP 占位）"}


# ── 监控告警 ──────────────────────────────────────────────

@router.get("/alerts", response_model=dict)
async def list_alerts(admin: dict = Depends(get_admin_user)):
    """查看最近告警记录（来自内存缓冲）"""
    from app.monitoring import get_alert_buffer
    return {"code": 0, "data": get_alert_buffer()}


@router.get("/health", response_model=dict)
async def admin_deep_health(admin: dict = Depends(get_admin_user)):
    """后台查看深度健康检查（需 admin 鉴权）"""
    from app.monitoring import deep_health
    return await deep_health()
