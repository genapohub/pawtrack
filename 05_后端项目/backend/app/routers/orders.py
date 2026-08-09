"""
宠迹 PawTrack — 订单与订阅路由（Sprint 2）

功能：
1. 创建订单（会员购买）
2. 支付回调（模拟支付成功）
3. 订阅状态查询
4. 取消订阅
5. 会员权益检查
6. Outbox Pattern 保证支付-订阅最终一致性
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone, timedelta

from app.database import get_db
from app.models import (
    Order, Subscription, User, MemberLevel,
    OrderStatus, PayChannel, SubscriptionPlan, SubscriptionStatus,
    EventOutbox
)
from app.auth import get_current_user
from app.plans import PLAN_CONFIG

router = APIRouter(prefix="/api/v1/orders", tags=["订单订阅"])

# ── 请求模型 ──────────────────────────────────────────────

class CreateOrderRequest(BaseModel):
    plan: SubscriptionPlan
    pay_channel: PayChannel = PayChannel.wechat

class PayCallbackRequest(BaseModel):
    """支付回调（MVP：模拟支付成功）"""
    order_no: str
    transaction_id: str = Field(..., min_length=8)

class CancelSubscriptionRequest(BaseModel):
    auto_renew: bool = False

# ── 工具函数 ──────────────────────────────────────────────

def _order_to_dict(order: Order) -> dict:
    return {
        "id": order.id,
        "order_no": order.order_no,
        "type": order.type,
        "amount": float(order.amount),
        "status": order.status.value,
        "pay_channel": order.pay_channel.value if order.pay_channel else None,
        "paid_at": order.paid_at.isoformat() if order.paid_at else None,
        "created_at": order.created_at.isoformat() if order.created_at else ""
    }

def _sub_to_dict(sub: Subscription) -> dict:
    return {
        "id": sub.id,
        "plan": sub.plan.value,
        "status": sub.status.value,
        "started_at": sub.started_at.isoformat() if sub.started_at else None,
        "expire_at": sub.expire_at.isoformat() if sub.expire_at else None,
        "auto_renew": sub.auto_renew,
        "created_at": sub.created_at.isoformat() if sub.created_at else ""
    }

# ── 接口实现 ──────────────────────────────────────────────

@router.get("/plans", response_model=dict)
async def list_plans():
    """获取套餐列表"""
    plans = []
    for plan_key, config in PLAN_CONFIG.items():
        plans.append({
            "plan": plan_key.value,
            "name": config["name"],
            "price": config["price"],
            "level": config["level"],
            "days": config["days"]
        })
    return {"code": 0, "data": plans}

@router.post("", response_model=dict)
async def create_order(
    body: CreateOrderRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建订单"""
    config = PLAN_CONFIG[body.plan]

    order = Order(
        order_no=f"PT{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}",
        user_id=int(user["sub"]),
        type="subscription",
        product_id=body.plan.value,
        amount=config["price"],
        status=OrderStatus.pending,
        pay_channel=body.pay_channel
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    return {
        "code": 0,
        "data": {
            **_order_to_dict(order),
            "plan_name": config["name"],
            "pay_info": {
                "method": body.pay_channel.value,
                "amount": config["price"],
                # MVP：返回模拟支付参数
                "pay_url": f"mock://pay/{order.order_no}",
                "expire_at": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
            }
        }
    }

@router.post("/pay-callback", response_model=dict)
async def pay_callback(
    body: PayCallbackRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    支付回调（MVP：模拟支付成功）
    正式环境由微信/支付宝服务端调用
    使用 Outbox Pattern 保证最终一致性
    """
    result = await db.execute(select(Order).where(Order.order_no == body.order_no))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(404, detail={"code": 50001, "message": "订单不存在"})

    if order.status != OrderStatus.pending:
        raise HTTPException(400, detail={"code": 50002, "message": "订单状态异常"})

    # 1. 更新订单状态
    order.status = OrderStatus.paid
    order.transaction_id = body.transaction_id
    order.paid_at = datetime.now(timezone.utc)

    # 2. 创建订阅记录
    plan = SubscriptionPlan(order.product_id)
    config = PLAN_CONFIG[plan]
    now = datetime.now(timezone.utc)

    # 查询是否有现有订阅（续费场景）
    existing_sub = await db.execute(
        select(Subscription).where(
            Subscription.user_id == order.user_id,
            Subscription.status == SubscriptionStatus.active
        )
    )
    existing = existing_sub.scalar_one_or_none()

    if existing:
        # 续费：在原到期时间基础上延长
        base_time = existing.expire_at if existing.expire_at > now else now
        existing.expire_at = base_time + timedelta(days=config["days"])
        existing.plan = plan
        sub = existing
    else:
        sub = Subscription(
            user_id=order.user_id,
            order_id=order.id,
            plan=plan,
            status=SubscriptionStatus.active,
            started_at=now,
            expire_at=now + timedelta(days=config["days"]),
            auto_renew=True
        )
        db.add(sub)

    # 3. 更新用户会员等级
    user_result = await db.execute(select(User).where(User.id == order.user_id))
    u = user_result.scalar_one_or_none()
    if u:
        u.member_level = MemberLevel(config["level"])
        u.member_expire_at = sub.expire_at

    # 4. 写入 Outbox 事件（最终一致性保障）
    outbox_event = EventOutbox(
        event_type="subscription.activated",
        payload=f'{{"user_id":{order.user_id},"plan":"{plan.value}","expire_at":"{sub.expire_at.isoformat()}"}}',
        status="pending"
    )
    db.add(outbox_event)

    await db.commit()
    await db.refresh(sub)

    return {"code": 0, "message": "支付成功", "data": _sub_to_dict(sub)}

@router.get("/subscription", response_model=dict)
async def get_subscription(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """查询当前订阅状态"""
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == int(user["sub"]),
            Subscription.status == SubscriptionStatus.active
        ).order_by(Subscription.created_at.desc()).limit(1)
    )
    sub = result.scalar_one_or_none()

    if not sub:
        return {"code": 0, "data": {"plan": "free", "status": "active", "expire_at": None}}

    # 检查是否过期
    if sub.expire_at < datetime.now(timezone.utc):
        sub.status = SubscriptionStatus.expired
        await db.commit()
        return {"code": 0, "data": {"plan": sub.plan.value, "status": "expired", "expire_at": sub.expire_at.isoformat()}}

    return {"code": 0, "data": _sub_to_dict(sub)}

@router.put("/subscription/cancel", response_model=dict)
async def cancel_subscription(
    body: CancelSubscriptionRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """取消自动续费"""
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == int(user["sub"]),
            Subscription.status == SubscriptionStatus.active
        )
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(404, detail={"code": 50003, "message": "无活跃订阅"})

    sub.auto_renew = body.auto_renew
    await db.commit()

    return {"code": 0, "data": _sub_to_dict(sub)}

@router.get("/history", response_model=dict)
async def order_history(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """订单历史"""
    count_result = await db.execute(
        select(func.count()).where(Order.user_id == int(user["sub"])).select_from(Order)
    )
    total = count_result.scalar()

    result = await db.execute(
        select(Order)
        .where(Order.user_id == int(user["sub"]))
        .order_by(Order.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    orders = result.scalars().all()

    return {
        "code": 0,
        "data": [_order_to_dict(o) for o in orders],
        "pagination": {"page": page, "size": size, "total": total}
    }


@router.get("/{order_no}", response_model=dict)
async def order_detail(
    order_no: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """订单详情"""
    result = await db.execute(
        select(Order).where(Order.order_no == order_no, Order.user_id == int(user["sub"]))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(404, detail={"code": 50001, "message": "订单不存在"})
    return {"code": 0, "data": _order_to_dict(order)}


class PayRequest(BaseModel):
    """发起支付（MVP：返回模拟支付参数，前端调起支付后回调 pay-callback）"""
    pay_channel: PayChannel = PayChannel.wechat


@router.post("/{order_no}/pay", response_model=dict)
async def initiate_pay(
    order_no: str,
    body: PayRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """发起支付（MVP：返回模拟支付参数）"""
    result = await db.execute(
        select(Order).where(Order.order_no == order_no, Order.user_id == int(user["sub"]))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(404, detail={"code": 50001, "message": "订单不存在"})
    if order.status != OrderStatus.pending:
        raise HTTPException(400, detail={"code": 50002, "message": "订单状态异常，无法支付"})

    # 更新支付渠道
    order.pay_channel = body.pay_channel
    await db.commit()

    # MVP：返回模拟支付参数（正式环境返回微信/支付宝预支付参数）
    return {
        "code": 0,
        "data": {
            "order_no": order.order_no,
            "amount": float(order.amount),
            "pay_channel": body.pay_channel.value,
            "pay_params": {
                "prepay_id": f"mock_prepay_{order.order_no}",
                "nonce_str": str(uuid.uuid4()).replace("-", "")[:32],
                "timestamp": str(int(datetime.now(timezone.utc).timestamp())),
            },
            "callback_url": "/api/v1/orders/pay-callback",
        },
        "message": "支付参数已生成（MVP 模拟）",
    }


class RenewRequest(BaseModel):
    pay_channel: PayChannel = PayChannel.wechat


@router.post("/subscription/renew", response_model=dict)
async def renew_subscription(
    body: RenewRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """续费（基于当前订阅计划创建新订单）"""
    # 查询当前订阅
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == int(user["sub"]),
            Subscription.status == SubscriptionStatus.active
        ).order_by(Subscription.created_at.desc()).limit(1)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(400, detail={"code": 50003, "message": "无活跃订阅，无法续费"})

    plan = sub.plan
    config = PLAN_CONFIG[plan]
    now = datetime.now(timezone.utc)

    # 创建续费订单
    order = Order(
        order_no=f"PT{now.strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}",
        user_id=int(user["sub"]),
        type="renew",
        product_id=plan.value,
        amount=config["price"],
        status=OrderStatus.pending,
        pay_channel=body.pay_channel
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    return {
        "code": 0,
        "data": _order_to_dict(order),
        "message": "续费订单已创建，请前往支付"
    }
