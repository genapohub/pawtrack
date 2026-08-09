"""
宠迹 PawTrack — 认证路由（注册/登录/刷新Token）
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Optional
import uuid

from app.database import get_db
from app.models import User, MemberLevel
from app.auth import (
    create_access_token, create_refresh_token, decode_token,
    get_current_user, get_current_user_optional
)

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])

# ── 请求/响应模型 ──────────────────────────────────────────

class RegisterRequest(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    code: str = Field(..., min_length=4, max_length=6, description="短信验证码")
    nickname: Optional[str] = Field(None, max_length=50)
    invite_code: Optional[str] = None

class LoginRequest(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")
    code: str = Field(..., min_length=4, max_length=6)

class WechatLoginRequest(BaseModel):
    code: str = Field(..., description="微信授权码")
    nickname: Optional[str] = None
    avatar: Optional[str] = None

class TokenResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: dict

class RefreshRequest(BaseModel):
    refresh_token: str

# ── 工具函数 ──────────────────────────────────────────────

async def _verify_sms_code(phone: str, code: str) -> bool:
    """验证短信验证码（MVP阶段：跳过验证，直接返回 True）"""
    # TODO: 接入短信服务后实现
    return True

async def _get_user_device_ids(db: AsyncSession, user_id: int) -> list:
    # MVP 阶段返回空列表，后续从 devices 表查询
    return []

# ── 接口实现 ──────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """手机号注册（支持邀请码奖励）"""
    if not await _verify_sms_code(body.phone, body.code):
        raise HTTPException(400, detail={"code": 20001, "message": "验证码错误"})

    # 检查用户是否已存在
    existing = await db.execute(select(User).where(User.phone == body.phone))
    if existing.scalar_one_or_none():
        raise HTTPException(400, detail={"code": 20001, "message": "手机号已注册"})

    # 处理邀请码（可选）：邀请人 +50 积分，新用户 +50 积分
    invited_by_id = None
    if body.invite_code:
        inviter_result = await db.execute(
            select(User).where(User.invite_code == body.invite_code.strip().upper())
        )
        inviter = inviter_result.scalar_one_or_none()
        if inviter:
            invited_by_id = inviter.id

    # 创建用户（生成唯一邀请码）
    user = User(
        phone=body.phone,
        nickname=body.nickname or f"用户{body.phone[-4:]}",
        member_level=MemberLevel.free,
        invited_by=invited_by_id,
        points=50 if invited_by_id else 0  # 被邀请新用户 +50
    )
    db.add(user)
    await db.flush()  # 拿到 user.id
    user.invite_code = f"PT{user.id:06d}"  # 邀请码 = PT + 6位用户ID

    # 邀请人奖励
    if invited_by_id:
        inviter_result = await db.execute(select(User).where(User.id == invited_by_id))
        inviter = inviter_result.scalar_one_or_none()
        if inviter:
            inviter.points += 50
            from app.models import PointsLog, PointType
            db.add(PointsLog(
                user_id=inviter.id, change=50, type=PointType.invite,
                related_id=f"invite_{user.id}", balance=inviter.points
            ))
        # 新用户积分流水
        from app.models import PointsLog, PointType
        db.add(PointsLog(
            user_id=user.id, change=50, type=PointType.invite,
            related_id=f"invited_{invited_by_id}", balance=50
        ))

    await db.commit()
    await db.refresh(user)

    # 生成 Token
    access = create_access_token(user.id, user.phone, user.member_level.value, [])
    refresh, family = create_refresh_token(user.id)

    return TokenResponse(data={
        "user_id": user.id,
        "phone": user.phone,
        "nickname": user.nickname,
        "member_level": user.member_level.value,
        "invite_code": user.invite_code,
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "Bearer",
        "expires_in": 7200
    })

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """手机号登录"""
    if not await _verify_sms_code(body.phone, body.code):
        raise HTTPException(400, detail={"code": 20001, "message": "验证码错误"})

    result = await db.execute(select(User).where(User.phone == body.phone))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, detail={"code": 20001, "message": "用户不存在，请先注册"})

    # 更新最后登录时间
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    device_ids = await _get_user_device_ids(db, user.id)
    access = create_access_token(user.id, user.phone, user.member_level.value, device_ids)
    refresh, family = create_refresh_token(user.id)

    return TokenResponse(data={
        "user_id": user.id,
        "phone": user.phone,
        "nickname": user.nickname,
        "member_level": user.member_level.value,
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "Bearer",
        "expires_in": 7200
    })

@router.post("/wechat-login", response_model=TokenResponse)
async def wechat_login(body: WechatLoginRequest, db: AsyncSession = Depends(get_db)):
    """微信登录（MVP：模拟实现）"""
    # TODO: 用 code 换 openid（接入微信开放平台）
    wechat_openid = f"mock_openid_{uuid.uuid4().hex[:8]}"

    result = await db.execute(select(User).where(User.wechat_openid == wechat_openid))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            wechat_openid=wechat_openid,
            nickname=body.nickname or "微信用户",
            member_level=MemberLevel.free
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    device_ids = await _get_user_device_ids(db, user.id)
    access = create_access_token(user.id, user.phone or "", user.member_level.value, device_ids)
    refresh, family = create_refresh_token(user.id)

    return TokenResponse(data={
        "user_id": user.id,
        "nickname": user.nickname,
        "member_level": user.member_level.value,
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "Bearer",
        "expires_in": 7202
    })

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest):
    """刷新 Token"""
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("token_type") != "refresh":
            raise HTTPException(401, detail={"code": 10008, "message": "不是 refresh_token"})
    except HTTPException:
        raise HTTPException(401, detail={"code": 10007, "message": "Refresh Token 已过期，请重新登录"})

    user_id = int(payload["sub"])

    # TODO: 从数据库验证 refresh_token 是否已被吊销

    # 生成新 Token（旧 refresh_token 不立即失效，但建议客户端替换）
    access = create_access_token(user_id, "", "free", [])
    new_refresh, _ = create_refresh_token(user_id, payload.get("token_family"))

    return TokenResponse(data={
        "access_token": access,
        "refresh_token": new_refresh,
        "token_type": "Bearer",
        "expires_in": 7200
    })

@router.delete("/logout")
async def logout(user: dict = Depends(get_current_user)):
    """退出登录（MVP：客户端自行清除 Token）"""
    return {"code": 0, "message": "success", "data": {"logged_out": True}}

@router.get("/.well-known/jwks.json")
async def jwks():
    """JWKS 公钥端点（供客户端验证 JWT）"""
    from app.auth import PUBLIC_KEY
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    # 解析公钥，生成 JWK
    pub_key = serialization.load_pem_public_key(PUBLIC_KEY.encode())
    if isinstance(pub_key, rsa.RSAPublicNumbers):
        numbers = pub_key.public_numbers()
    else:
        numbers = pub_key.public_numbers()

    import base64
    def int_to_base64url(n: int) -> str:
        bytes_len = (n.bit_length() + 7) // 8
        return base64.urlsafe_b64encode(n.to_bytes(bytes_len, 'big')).decode().rstrip('=')

    return {
        "keys": [{
            "kty": "RSA",
            "kid": "pawtrack-rsa-001",
            "use": "sig",
            "alg": "RS256",
            "n": int_to_base64url(numbers.n),
            "e": int_to_base64url(numbers.e)
        }]
    }
