"""
宠迹 PawTrack — 用户模块路由

接口：
1. GET    /users/me            获取当前用户信息
2. PUT    /users/me            更新用户信息
3. PUT    /users/me/password   修改密码
4. GET    /users/me/devices    我的设备列表
5. DELETE /users/me            注销账号（软删除）
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

from app.database import get_db
from app.models import User, Device
from app.auth import get_current_user
from app.security import hash_password, verify_password
from app.enums import DeviceStatus

router = APIRouter(prefix="/api/v1/users", tags=["用户"])


# ── 请求模型 ──────────────────────────────────────────────

class UpdateUserRequest(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = Field(None, max_length=255)
    privacy_location: Optional[str] = None  # friends / nearby / private

class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6, max_length=64)
    new_password: str = Field(..., min_length=6, max_length=64)


# ── 接口实现 ──────────────────────────────────────────────

@router.get("/me", response_model=dict)
async def get_me(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取当前用户信息"""
    result = await db.execute(select(User).where(User.id == int(user["sub"])))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(404, detail={"code": 20001, "message": "用户不存在"})
    return {"code": 0, "data": _user_to_dict(u)}


@router.put("/me", response_model=dict)
async def update_me(body: UpdateUserRequest, user: dict = Depends(get_current_user),
                    db: AsyncSession = Depends(get_db)):
    """更新用户信息"""
    values = {}
    if body.nickname is not None:
        values["nickname"] = body.nickname
    if body.avatar is not None:
        values["avatar"] = body.avatar
    if body.privacy_location is not None:
        if body.privacy_location not in ("friends", "nearby", "private"):
            raise HTTPException(400, detail={"code": 20002, "message": "隐私设置无效"})
        from app.enums import PrivacyLevel
        values["privacy_location"] = PrivacyLevel(body.privacy_location)
    if not values:
        raise HTTPException(400, detail={"code": 20003, "message": "无更新字段"})
    values["updated_at"] = datetime.now(timezone.utc)
    await db.execute(update(User).where(User.id == int(user["sub"])).values(**values))
    await db.commit()
    return {"code": 0, "message": "更新成功"}


@router.put("/me/password", response_model=dict)
async def change_password(body: ChangePasswordRequest, user: dict = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    """修改密码"""
    result = await db.execute(select(User).where(User.id == int(user["sub"])))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(404, detail={"code": 20001, "message": "用户不存在"})
    # 若已设置密码，需校验旧密码
    if u.password_hash:
        if not verify_password(body.old_password, u.password_hash):
            raise HTTPException(400, detail={"code": 20004, "message": "原密码错误"})
    if body.old_password == body.new_password:
        raise HTTPException(400, detail={"code": 20005, "message": "新密码不能与原密码相同"})
    u.password_hash = hash_password(body.new_password)
    u.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"code": 0, "message": "密码修改成功"}


@router.get("/me/devices", response_model=dict)
async def my_devices(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """我的设备列表"""
    result = await db.execute(
        select(Device).where(Device.user_id == int(user["sub"]))
    )
    devices = result.scalars().all()
    return {"code": 0, "data": [_device_to_dict(d) for d in devices]}


# ── S11 紧急联系人 ──────────────────────────────────────────

@router.get("/me/contacts", response_model=dict)
async def get_contacts(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取紧急联系人列表"""
    result = await db.execute(select(User).where(User.id == int(user["sub"])))
    u = result.scalar_one_or_none()
    return {"code": 0, "data": u.emergency_contacts or []}

@router.put("/me/contacts", response_model=dict)
async def save_contacts(body: dict, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """保存紧急联系人列表 [{phone, name, relation}]"""
    result = await db.execute(select(User).where(User.id == int(user["sub"])))
    u = result.scalar_one_or_none()
    contacts = body.get("contacts", [])
    # 简单校验
    for c in contacts:
        if not c.get("phone") or not c.get("name"):
            raise HTTPException(400, detail={"code": 40001, "message": "联系人姓名为空或手机号为空"})
    u.emergency_contacts = contacts
    await db.commit()
    return {"code": 0, "data": contacts}


@router.delete("/me", response_model=dict)
async def delete_me(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """注销账号（软删除：status=deleted，清除敏感字段）"""
    result = await db.execute(select(User).where(User.id == int(user["sub"])))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(404, detail={"code": 20001, "message": "用户不存在"})
    if u.status == "deleted":
        raise HTTPException(400, detail={"code": 20006, "message": "账号已注销"})
    u.status = "deleted"
    u.nickname = f"已注销用户{u.id}"
    u.avatar = None
    u.password_hash = None
    u.wechat_openid = None
    u.apple_id = None
    u.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"code": 0, "message": "账号已注销"}


# ── 序列化 ──────────────────────────────────────────────

def _user_to_dict(u: User) -> dict:
    return {
        "id": u.id,
        "phone": u.phone,
        "nickname": u.nickname,
        "avatar": u.avatar,
        "member_level": u.member_level.value if u.member_level else "free",
        "member_expire_at": u.member_expire_at.isoformat() if u.member_expire_at else None,
        "points": u.points,
        "privacy_location": u.privacy_location.value if u.privacy_location else "friends",
        "status": u.status,
        "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
        "created_at": u.created_at.isoformat() if u.created_at else "",
    }

def _device_to_dict(d: Device) -> dict:
    return {
        "id": d.id,
        "sn": d.sn,
        "pet_id": d.pet_id,
        "hardware_type": d.hardware_type,
        "firmware_version": d.firmware_version,
        "battery_level": d.battery_level,
        "status": d.status.value if d.status else DeviceStatus.offline.value,
        "last_online_at": d.last_online_at.isoformat() if d.last_online_at else None,
    }

# ── 家人共享 ──────────────────────────────────────────────

@router.get("/me/family", response_model=dict)
async def get_family(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    u = (await db.execute(select(User).where(User.id == int(user["sub"])))).scalar_one_or_none()
    return {"code": 0, "data": u.family_members if u else []}

@router.put("/me/family", response_model=dict)
async def update_family(body: dict, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    u = (await db.execute(select(User).where(User.id == int(user["sub"])))).scalar_one_or_none()
    if u:
        u.family_members = body.get("members", [])
        await db.commit()
    return {"code": 0, "message": "已更新"}
