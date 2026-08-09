"""
宠迹 PawTrack — 邀请好友路由

功能：
1. 获取我的邀请码与邀请记录
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/invites", tags=["邀请"])


@router.get("", response_model=dict)
async def my_invites(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取我的邀请码与已邀请用户列表"""
    me = (await db.execute(select(User).where(User.id == int(user["sub"])))).scalar_one_or_none()
    if not me:
        return {"code": 0, "data": {"invite_code": "", "items": []}}

    # 通过 invited_by 字段找到被邀请的用户
    invited = (await db.execute(
        select(User).where(User.invited_by == me.id).order_by(User.created_at.desc())
    )).scalars().all()

    return {
        "code": 0,
        "data": {
            "invite_code": me.invite_code or f"PT{me.id:06d}",
            "items": [{
                "id": u.id,
                "nickname": u.nickname,
                "phone": u.phone,
                "points_awarded": 50,
                "created_at": u.created_at.isoformat() if u.created_at else "",
            } for u in invited],
        }
    }
