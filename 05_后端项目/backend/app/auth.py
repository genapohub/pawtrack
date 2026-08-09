"""
宠迹 PawTrack — JWT 工具类（RS256 双Token）
"""
import jwt
import time
import uuid
import datetime
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

# ── 加载密钥 ──────────────────────────────────────────────

def _generate_rsa_keypair() -> tuple[str, str]:
    """生成临时 RSA 密钥对，返回 (private_pem, public_pem)"""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()
    pub_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    return priv_pem, pub_pem


def _load_keypair() -> tuple[str, str]:
    """加载私钥+公钥；文件缺失时：dev 生成临时密钥，prod 直接报错"""
    try:
        with open(settings.JWT_PRIVATE_KEY_PATH, "r") as f:
            priv = f.read()
        with open(settings.JWT_PUBLIC_KEY_PATH, "r") as f:
            pub = f.read()
        return priv, pub
    except FileNotFoundError:
        if settings.is_prod:
            raise RuntimeError(
                f"生产环境 (ENV=prod) 必须提供 JWT 密钥文件："
                f"{settings.JWT_PRIVATE_KEY_PATH} / {settings.JWT_PUBLIC_KEY_PATH}，"
                f"请挂载 keys 目录或设置 JWT_PRIVATE_KEY_PATH/JWT_PUBLIC_KEY_PATH"
            )
        print("⚠️  JWT 密钥文件不存在，生成临时 RSA 密钥对（仅开发环境）")
        return _generate_rsa_keypair()


PRIVATE_KEY, PUBLIC_KEY = _load_keypair()

# ── Token 生成 ──────────────────────────────────────────────

def create_access_token(user_id: int, phone: str, member_level: str, device_ids: list) -> str:
    """生成 access_token（2小时有效）"""
    now = int(time.time())
    payload = {
        "iss": "https://api.pawtrack.app",
        "sub": str(user_id),
        "aud": "pawtrack-app",
        "exp": now + settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "phone": phone,
        "member_level": member_level,
        "device_ids": device_ids or [],
        "token_type": "access"
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(user_id: int, token_family: str = None) -> tuple[str, str]:
    """生成 refresh_token（30天有效），返回 (token, family)"""
    now = int(time.time())
    family = token_family or str(uuid.uuid4())
    payload = {
        "iss": "https://api.pawtrack.app",
        "sub": str(user_id),
        "aud": "pawtrack-app",
        "exp": now + settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "token_family": family,
        "token_type": "refresh"
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm=settings.JWT_ALGORITHM), family

# ── Token 验证 ──────────────────────────────────────────────

def decode_token(token: str) -> Dict[str, Any]:
    """解码并验证 JWT（RS256）"""
    try:
        return jwt.decode(
            token, PUBLIC_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer="https://api.pawtrack.app",
            audience="pawtrack-app"
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail={"code": 10003, "message": "Token 已过期"})
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail={"code": 10004, "message": "Token 无效"})

# ── FastAPI 依赖注入 ────────────────────────────────────────

security = HTTPBearer(auto_error=False)

async def get_current_user(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """获取当前用户（从 Authorization Header 解析 JWT）"""
    if not credentials:
        raise HTTPException(status_code=401, detail={"code": 10001, "message": "未提供 Token"})
    return decode_token(credentials.credentials)

async def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """获取当前用户（可选，用于公开接口）"""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    try:
        return decode_token(auth[7:])
    except HTTPException:
        return None

# ── 后台管理员 Token ────────────────────────────────────────

def create_admin_token(username: str, role: str = "super_admin") -> str:
    """生成后台管理员 access_token"""
    now = int(time.time())
    payload = {
        "iss": "https://api.pawtrack.app",
        "sub": username,
        "aud": "pawtrack-admin",
        "exp": now + settings.ADMIN_TOKEN_EXPIRE_SECONDS,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "username": username,
        "role": role,
        "scope": "admin",
        "token_type": "admin_access"
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_admin_token(token: str) -> Dict[str, Any]:
    """解码并验证后台管理员 JWT"""
    try:
        return jwt.decode(
            token, PUBLIC_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer="https://api.pawtrack.app",
            audience="pawtrack-admin"
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail={"code": 10003, "message": "管理员 Token 已过期"})
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail={"code": 10004, "message": "管理员 Token 无效"})


async def get_admin_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """获取当前管理员（强制 admin scope）"""
    if not credentials:
        raise HTTPException(status_code=401, detail={"code": 10001, "message": "未提供管理员 Token"})
    payload = decode_admin_token(credentials.credentials)
    if payload.get("scope") != "admin":
        raise HTTPException(status_code=403, detail={"code": 10006, "message": "非管理员 Token，禁止访问"})
    return payload
