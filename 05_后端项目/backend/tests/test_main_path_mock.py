"""主路径 TestClient：SQLite + 进程内 Mock，不连真实 PG/Redis/Mongo。

不设置 PAWTRACK_TEST_DB；19 条集成测试仍应保持 skip。
不得把本文件写成已对接真硬件 / 微信 / 短信 / 支付 / 地图。
"""
from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# 本文件不是 integration，未设置 PAWTRACK_TEST_DB 时也必须执行
assert os.environ.get("PAWTRACK_TEST_DB") != "1"

from app.config import settings  # noqa: E402
from app.database import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base, Device, Pet  # noqa: E402
from app.services.mock_notice import (  # noqa: E402
    DEVICE_BIND_NOTICE,
    DEVICE_BOUND_OTHER_PET,
    INVALID_DEVICE_MESSAGE,
    LOCATION_NOTICE,
)

SMS_CODE = settings.DEV_SMS_CODE
ADMIN_USER = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASSWORD", "pawtrack_admin_2026")


class ThreadedAsyncSession:
    """把同步 SQLite Session 包成路由所用的 await db.execute / commit / flush。"""

    def __init__(self, sync_session: Session):
        self._s = sync_session

    async def execute(self, *args, **kwargs):
        return await asyncio.to_thread(self._s.execute, *args, **kwargs)

    async def commit(self):
        return await asyncio.to_thread(self._s.commit)

    async def flush(self, *args, **kwargs):
        return await asyncio.to_thread(self._s.flush, *args, **kwargs)

    async def refresh(self, obj):
        return await asyncio.to_thread(self._s.refresh, obj)

    def add(self, obj):
        self._s.add(obj)

    async def close(self):
        return await asyncio.to_thread(self._s.close)


_ID_SEQ: dict = {}


def _assign_sqlite_ids(session, flush_context, instances):
    for obj in list(session.new):
        if not hasattr(obj, "id") or getattr(obj, "id") is not None:
            continue
        key = type(obj)
        _ID_SEQ[key] = _ID_SEQ.get(key, 0) + 1
        obj.id = _ID_SEQ[key]


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    event.listen(Session, "before_flush", _assign_sqlite_ids)

    class _AsyncCM:
        def __init__(self):
            self._sync = SessionLocal()
            self._wrapped = ThreadedAsyncSession(self._sync)

        async def __aenter__(self):
            return self._wrapped

        async def __aexit__(self, exc_type, exc, tb):
            self._sync.close()

    async def _override_get_db():
        cm = _AsyncCM()
        try:
            yield await cm.__aenter__()
        finally:
            await cm.__aexit__(None, None, None)

    @asynccontextmanager
    async def _noop_lifespan(_app):
        _app.state.redis_client = None
        yield

    import app.auth as auth_mod
    app.dependency_overrides[get_db] = _override_get_db
    original_session_local = auth_mod.SessionLocal
    auth_mod.SessionLocal = _AsyncCM
    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = _noop_lifespan
    _ID_SEQ.clear()
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_db, None)
        auth_mod.SessionLocal = original_session_local
        app.router.lifespan_context = original_lifespan
        event.remove(Session, "before_flush", _assign_sqlite_ids)
        engine.dispose()


def _auth(client: TestClient, phone: str = "13800138000") -> dict:
    r = client.post("/api/v1/auth/register", json={
        "phone": phone, "code": SMS_CODE, "nickname": "预览用户",
    })
    if r.status_code == 400 and "已注册" in r.text:
        r = client.post("/api/v1/auth/login", json={"phone": phone, "code": SMS_CODE})
    assert r.status_code == 200, r.text
    token = r.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_main_path_login_pet_device_location_alarm_me_admin(client):
    headers = _auth(client)

    # 添加宠物：猫默认 100m 围栏开启，狗 300m 报警默认关
    cat = client.post("/api/v1/pets", headers=headers, json={"name": "小花", "pet_type": "cat"})
    assert cat.status_code == 200, cat.text
    cat_data = cat.json()["data"]
    assert cat_data["fence_enabled"] is True
    assert cat_data["fence_radius"] == 100
    dog = client.post("/api/v1/pets", headers=headers, json={"name": "阿黄", "pet_type": "dog"})
    assert dog.status_code == 200, dog.text
    dog_data = dog.json()["data"]
    assert dog_data["fence_enabled"] is False
    assert dog_data["fence_radius"] == 300
    pets = client.get("/api/v1/pets", headers=headers)
    assert pets.status_code == 200 and len(pets.json()["data"]) == 2

    # 无效激活码 / 绑定不存在的 SN
    bad = client.post("/api/v1/devices/register", json={
        "sn": "SNMOCK0001", "activation_code": "INVALID00", "hw_type": "cat",
    })
    assert bad.status_code == 400
    assert INVALID_DEVICE_MESSAGE in bad.text
    missing = client.post("/api/v1/devices/bind", headers=headers, json={
        "sn": "UNKNOWN99", "pet_id": cat_data["id"],
    })
    assert missing.status_code == 404
    assert INVALID_DEVICE_MESSAGE in missing.text

    # 示例激活码注册并绑定（本地示意，非真机）
    reg = client.post("/api/v1/devices/register", json={
        "sn": "SNMOCK0001", "activation_code": "PT-TEST-0001", "hw_type": "cat",
    })
    assert reg.status_code == 200, reg.text
    assert reg.json()["data"]["is_simulated"] is True
    assert "非真机" in reg.json()["data"]["notice"]
    assert reg.json()["data"]["mqtt_url"] is None
    bind = client.post("/api/v1/devices/bind", headers=headers, json={
        "sn": "SNMOCK0001", "pet_id": cat_data["id"],
    })
    assert bind.status_code == 200, bind.text
    assert bind.json()["data"]["pet_id"] == cat_data["id"]
    assert DEVICE_BIND_NOTICE in bind.json()["message"]
    steal = client.post("/api/v1/devices/bind", headers=headers, json={
        "sn": "SNMOCK0001", "pet_id": dog_data["id"],
    })
    assert steal.status_code == 409
    assert DEVICE_BOUND_OTHER_PET in steal.text
    device_id = bind.json()["data"]["device_id"]

    # 上报与查看位置 / 轨迹（示意坐标）
    ts = int(datetime.now(timezone.utc).timestamp())
    up = client.post("/api/v1/location/upload", headers=headers, json={
        "device_id": device_id, "lat": 31.2304, "lng": 121.4737,
        "source": "wifi", "battery": 80, "ts": ts,
    })
    assert up.status_code == 200, up.text
    assert up.json()["is_simulated"] is True
    assert LOCATION_NOTICE in up.json()["notice"]
    realtime = client.get(f"/api/v1/location/realtime/{cat_data['id']}", headers=headers)
    assert realtime.status_code == 200, realtime.text
    rdata = realtime.json()["data"]
    assert rdata["lat"] and rdata["lng"]
    assert rdata["is_simulated"] is True
    hist = client.get(f"/api/v1/location/history/{cat_data['id']}", headers=headers)
    assert hist.status_code == 200, hist.text
    assert hist.json()["pagination"]["total"] >= 1
    assert hist.json()["is_simulated"] is True

    # 围栏中心 + 出圈告警
    fence = client.put(f"/api/v1/pets/{cat_data['id']}/fence", headers=headers, json={
        "fence_enabled": True,
        "fence_center_lat": 31.2304,
        "fence_center_lng": 121.4737,
        "fence_radius": 100,
    })
    assert fence.status_code == 200, fence.text
    inside = client.post("/api/v1/alarms/fence-check", json={
        "device_id": device_id, "lat": 31.2304, "lng": 121.4737,
    })
    assert inside.status_code == 200, inside.text
    assert inside.json()["data"]["triggered"] is False
    outside = client.post("/api/v1/alarms/fence-check", json={
        "device_id": device_id, "lat": 31.25, "lng": 121.50,
    })
    assert outside.status_code == 200, outside.text
    assert outside.json()["data"]["triggered"] is True
    alarms = client.get("/api/v1/alarms", headers=headers)
    assert alarms.status_code == 200, alarms.text
    assert len(alarms.json()["data"]) >= 1

    # 我的 / 设置
    me = client.get("/api/v1/users/me", headers=headers)
    assert me.status_code == 200, me.text
    assert me.json()["data"]["phone"] == "13800138000"
    settings_resp = client.get("/api/v1/alarms/settings", headers=headers)
    assert settings_resp.status_code == 200, settings_resp.text

    # 管理端只读
    login = client.post("/api/v1/admin/login", json={"username": ADMIN_USER, "password": ADMIN_PASS})
    assert login.status_code == 200, login.text
    admin_h = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}
    dash = client.get("/api/v1/admin/dashboard", headers=admin_h)
    assert dash.status_code == 200, dash.text
    assert dash.json()["data"]["pets"] >= 2
    assert dash.json()["data"]["users"] >= 1
    admin_pets = client.get("/api/v1/admin/pets", headers=admin_h)
    assert admin_pets.status_code == 200, admin_pets.text
    admin_alarms = client.get("/api/v1/admin/alarms", headers=admin_h)
    assert admin_alarms.status_code == 200, admin_alarms.text
