"""
宠迹 PawTrack — 积分管理路由（Sprint 2）

功能：
1. 积分余额查询
2. 积分记录列表
3. 每日签到
4. 积分商城（兑换商品占位）
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone, date

from app.database import get_db
from app.models import User, PointsLog, PointType
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/points", tags=["积分"])

# ── 接口实现 ──────────────────────────────────────────────

@router.get("/balance", response_model=dict)
async def get_balance(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """积分余额"""
    result = await db.execute(select(User).where(User.id == int(user["sub"])))
    u = result.scalar_one_or_none()
    return {"code": 0, "data": {"balance": u.points if u else 0}}

@router.get("/logs", response_model=dict)
async def get_logs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """积分记录列表"""
    count_result = await db.execute(
        select(func.count()).where(PointsLog.user_id == int(user["sub"])).select_from(PointsLog)
    )
    total = count_result.scalar()

    result = await db.execute(
        select(PointsLog)
        .where(PointsLog.user_id == int(user["sub"]))
        .order_by(PointsLog.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    logs = result.scalars().all()

    return {
        "code": 0,
        "data": [{
            "id": log.id,
            "change": log.change,
            "type": log.type.value,
            "related_id": log.related_id,
            "balance": log.balance,
            "created_at": log.created_at.isoformat() if log.created_at else ""
        } for log in logs],
        "pagination": {"page": page, "size": size, "total": total}
    }

@router.post("/signin", response_model=dict)
async def daily_signin(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """每日签到（每天一次，+5 积分）"""
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)

    # 检查今天是否已签到
    existing = await db.execute(
        select(PointsLog).where(
            PointsLog.user_id == int(user["sub"]),
            PointsLog.type == PointType.signin,
            PointsLog.created_at >= today_start
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, detail={"code": 60001, "message": "今天已签到"})

    # 发放积分
    result = await db.execute(select(User).where(User.id == int(user["sub"])))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(404, detail={"code": 60002, "message": "用户不存在"})

    new_balance = u.points + 5
    u.points = new_balance

    log = PointsLog(
        user_id=int(user["sub"]),
        change=5,
        type=PointType.signin,
        related_id=today.isoformat(),
        balance=new_balance
    )
    db.add(log)
    await db.commit()

    return {"code": 0, "data": {"awarded": 5, "balance": new_balance}}

@router.get("/shop", response_model=dict)
async def shop_items():
    """积分商城商品列表（占位）"""
    return {"code": 0, "data": [
        {"id": 1, "name": "宠物零食大礼包", "points": 500, "image": "🍖"},
        {"id": 2, "name": "定制项圈", "points": 2000, "image": "📿"},
        {"id": 3, "name": "宠物保险抵扣券 50元", "points": 1000, "image": "🎫"},
        {"id": 4, "name": "宠物洗浴券", "points": 300, "image": "🛁"}
    ]}

# 积分商城商品（兑换用常量表，MVP 硬编码）
SHOP_CATALOG = {
    1: {"name": "宠物零食大礼包", "points": 500},
    2: {"name": "定制项圈", "points": 2000},
    3: {"name": "宠物保险抵扣券 50元", "points": 1000},
    4: {"name": "宠物洗浴券", "points": 300},
}

@router.post("/redeem", response_model=dict)
async def redeem_item(
    item_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """积分兑换商品"""
    item = SHOP_CATALOG.get(item_id)
    if not item:
        raise HTTPException(400, detail={"code": 60003, "message": "商品不存在"})

    result = await db.execute(select(User).where(User.id == int(user["sub"])))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(404, detail={"code": 60002, "message": "用户不存在"})

    if u.points < item["points"]:
        raise HTTPException(400, detail={
            "code": 60004,
            "message": f"积分不足，需要 {item['points']}，当前 {u.points}"
        })

    # 扣积分 + 记流水
    new_balance = u.points - item["points"]
    u.points = new_balance

    log = PointsLog(
        user_id=int(user["sub"]),
        change=-item["points"],
        type=PointType.purchase,
        related_id=f"item_{item_id}",
        balance=new_balance
    )
    db.add(log)
    await db.commit()

    return {
        "code": 0,
        "data": {
            "item_id": item_id,
            "item_name": item["name"],
            "points_spent": item["points"],
            "balance": new_balance,
            "note": "兑换码将在 24 小时内通过站内信发放"
        }
    }
