"""
宠迹 PawTrack — JWT 鉴权逻辑单测（纯逻辑，无需数据库）

覆盖：
- access_token 生成与解码
- refresh_token 生成与 family
- admin_token 生成与解码
- 过期/篡改 token 解码失败
- audience 隔离（app token 不能用作 admin token）
"""
import time
import pytest

from app.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    create_admin_token,
    decode_admin_token,
)
from app.config import settings


class TestAccessToken:
    def test_create_and_decode(self):
        token = create_access_token(user_id=123, phone="138****8888", member_level="pro", device_ids=[1, 2])
        payload = decode_token(token)
        assert payload["sub"] == "123"
        assert payload["phone"] == "138****8888"
        assert payload["member_level"] == "pro"
        assert payload["device_ids"] == [1, 2]
        assert payload["token_type"] == "access"
        assert payload["aud"] == "pawtrack-app"

    def test_token_contains_jti_and_iat(self):
        token = create_access_token(1, "138", "free", [])
        payload = decode_token(token)
        assert "jti" in payload and payload["jti"]
        assert "iat" in payload and payload["iat"]
        assert payload["exp"] - payload["iat"] == settings.ACCESS_TOKEN_EXPIRE_SECONDS


class TestRefreshToken:
    def test_create_returns_token_and_family(self):
        token, family = create_refresh_token(123)
        assert isinstance(token, str)
        assert isinstance(family, str) and family
        # 同一 family 多次生成应生成不同 jti
        token2, family2 = create_refresh_token(123, family)
        assert family2 == family
        # 两个 token 字符串应不同（jti 不同）
        assert token != token2

    def test_refresh_token_decodable_as_app_token(self):
        token, _ = create_refresh_token(456)
        payload = decode_token(token)
        assert payload["sub"] == "456"
        assert payload["token_type"] == "refresh"


class TestAdminToken:
    def test_create_and_decode(self):
        token = create_admin_token("admin", role="super_admin")
        payload = decode_admin_token(token)
        assert payload["sub"] == "admin"
        assert payload["role"] == "super_admin"
        assert payload["scope"] == "admin"
        assert payload["aud"] == "pawtrack-admin"
        assert payload["token_type"] == "admin_access"

    def test_app_token_cannot_be_used_as_admin(self):
        """app 端 token 不能用于 admin 接口（audience 隔离）"""
        app_token = create_access_token(1, "138", "free", [])
        with pytest.raises(Exception):
            decode_admin_token(app_token)

    def test_admin_token_cannot_be_used_as_app(self):
        """admin token 不能用于 app 接口"""
        admin_token = create_admin_token("admin")
        with pytest.raises(Exception):
            decode_token(admin_token)


class TestTokenTamper:
    def test_tampered_token_rejected(self):
        token = create_access_token(1, "138", "free", [])
        # 篡改 payload 部分
        parts = token.split(".")
        assert len(parts) == 3
        tampered = parts[0] + "." + parts[1][:-4] + "AAAA" + "." + parts[2]
        with pytest.raises(Exception):
            decode_token(tampered)

    def test_garbage_token_rejected(self):
        with pytest.raises(Exception):
            decode_token("not.a.valid.jwt")
