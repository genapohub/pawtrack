"""
关键安全与业务阻断回归测试。

需要 PAWTRACK_TEST_DB=1 以及可用的 PostgreSQL / Redis / MongoDB。
"""
import os
import time

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def state(client):
    suffix = str(int(time.time()))[-7:]
    data = {"suffix": suffix}
    for key in ["a", "b", "c", "d"]:
        phone = "137" + suffix + str(len(data))
        resp = client.post("/api/v1/auth/register", json={
            "phone": phone, "code": "123456", "nickname": f"回归{key.upper()}"
        })
        assert resp.status_code == 200, resp.text
        data[key] = resp.json()["data"]
    return data


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def register_pet(client, token, name):
    resp = client.post("/api/v1/pets", headers=auth(token), json={
        "name": name, "pet_type": "dog", "fence_enabled": False
    })
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]["id"]


def register_device(client, token, pet_id, suffix, lat):
    sn = "REG" + suffix + str(pet_id)
    resp = client.post("/api/v1/devices/register", json={
        "sn": sn, "activation_code": "PT-TEST-0001", "hw_type": "dog"
    })
    assert resp.status_code == 200, resp.text
    device_id = resp.json()["data"]["device_id"]
    resp = client.post("/api/v1/devices/bind", headers=auth(token), json={"sn": sn, "pet_id": pet_id})
    assert resp.status_code == 200, resp.text
    resp = client.post("/api/v1/location/upload", headers=auth(token), json={
        "device_id": device_id, "lat": lat, "lng": 113.6253, "battery": 90, "ts": int(time.time())
    })
    assert resp.status_code == 200, resp.text
    return device_id


class TestAccountSecurity:
    def test_wrong_sms_code_rejected(self, client):
        resp = client.post("/api/v1/auth/login", json={"phone": "13700000000", "code": "000000"})
        assert resp.status_code in (400, 404)

    def test_wechat_same_code_returns_same_account(self, client):
        code = "regression-wechat-code"
        ids = []
        for _ in range(2):
            resp = client.post("/api/v1/auth/wechat-login", json={"code": code, "nickname": "微信回归"})
            assert resp.status_code == 200, resp.text
            ids.append(resp.json()["data"]["user_id"])
        assert ids[0] == ids[1]

    def test_blocked_user_login_and_token_rejected(self, client, state):
        login = client.post("/api/v1/admin/login", json={"username": "admin", "password": "pawtrack_admin_2026"})
        admin = login.json()["data"]["access_token"]
        user_id = state["a"]["user_id"]
        assert client.put(f"/api/v1/admin/users/{user_id}/ban?action=ban", headers=auth(admin)).status_code == 200
        resp = client.post("/api/v1/auth/login", json={"phone": state["a"]["phone"], "code": "123456"})
        assert resp.status_code == 403
        resp = client.get("/api/v1/pets", headers=auth(state["a"]["access_token"]))
        assert resp.status_code == 403
        assert client.put(f"/api/v1/admin/users/{user_id}/ban?action=unban", headers=auth(admin)).status_code == 200


class TestPaymentAndDeviceSecurity:
    def test_anonymous_payment_callback_rejected_and_owner_allowed(self, client, state):
        resp = client.post("/api/v1/orders", headers=auth(state["a"]["access_token"]), json={
            "plan": "basic_month", "pay_channel": "wechat"
        })
        order_no = resp.json()["data"]["order_no"]
        payload = {"order_no": order_no, "transaction_id": "txn-regression-1"}
        assert client.post("/api/v1/orders/pay-callback", json=payload).status_code == 401
        resp = client.post("/api/v1/orders/pay-callback", json=payload, headers=auth(state["a"]["access_token"]))
        assert resp.status_code == 200, resp.text
        assert resp.json()["data"]["plan"] == "basic_month"

    def test_invalid_activation_and_device_theft_rejected(self, client, state):
        assert client.post("/api/v1/devices/register", json={
            "sn": "BADREG0001", "activation_code": "not-valid-code", "hw_type": "dog"
        }).status_code == 400
        pet_a = register_pet(client, state["a"]["access_token"], "设备归属A")
        pet_b = register_pet(client, state["b"]["access_token"], "设备归属B")
        sn = "THEFTREG001"
        assert client.post("/api/v1/devices/register", json={
            "sn": sn, "activation_code": "PT-TEST-0001", "hw_type": "dog"
        }).status_code == 200
        assert client.post("/api/v1/devices/bind", headers=auth(state["a"]["access_token"]), json={
            "sn": sn, "pet_id": pet_a
        }).status_code == 200
        assert client.post("/api/v1/devices/bind", headers=auth(state["b"]["access_token"]), json={
            "sn": sn, "pet_id": pet_b
        }).status_code == 409

    def test_location_upload_requires_owner_and_history_written(self, client, state):
        pet_id = register_pet(client, state["c"]["access_token"], "历史轨迹狗")
        device_id = register_device(client, state["c"]["access_token"], pet_id, state["suffix"], 34.7466)
        anonymous = client.post("/api/v1/location/upload", json={
            "device_id": device_id, "lat": 34.7467, "lng": 113.6253, "battery": 90, "ts": int(time.time())
        })
        assert anonymous.status_code == 401
        resp = client.get(f"/api/v1/location/history/{pet_id}", headers=auth(state["c"]["access_token"]))
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1


class TestCoreRules:
    def test_alarm_settings_read_and_update(self, client, state):
        token = state["a"]["access_token"]
        assert client.get("/api/v1/alarms/settings", headers=auth(token)).status_code == 200
        resp = client.put("/api/v1/alarms/settings", headers=auth(token), json={
            "leave_fence_notify": True,
            "enter_fence_notify": False,
            "low_battery_threshold": 20,
            "emergency_contacts": [{"name": "回归联系人", "phone": "13900000000"}],
            "notify_push": True,
            "notify_sms": False,
        })
        assert resp.status_code == 200, resp.text

    def test_pet_fence_defaults_and_cat_cannot_disable(self, client, state):
        token = state["d"]["access_token"]
        dog = client.post("/api/v1/pets", headers=auth(token), json={"name": "默认狗", "pet_type": "dog"})
        assert dog.status_code == 200
        assert dog.json()["data"]["fence_radius"] == 300
        assert dog.json()["data"]["fence_enabled"] is False
        cat = client.post("/api/v1/pets", headers=auth(token), json={"name": "默认猫", "pet_type": "cat"})
        assert cat.status_code == 200
        cat_id = cat.json()["data"]["id"]
        assert cat.json()["data"]["fence_radius"] == 100
        assert cat.json()["data"]["fence_enabled"] is True
        assert client.put(f"/api/v1/pets/{cat_id}/fence", headers=auth(token), json={
            "fence_enabled": False
        }).status_code == 400

    def test_admin_dynamic_lists(self, client):
        login = client.post("/api/v1/admin/login", json={"username": "admin", "password": "pawtrack_admin_2026"})
        token = login.json()["data"]["access_token"]
        for path in ["users", "devices", "alarms", "orders"]:
            resp = client.get(f"/api/v1/admin/{path}?page=1&size=20", headers=auth(token))
            assert resp.status_code == 200, (path, resp.text)

    def test_same_utc_day_signin_rejected(self, client, state):
        token = state["d"]["access_token"]
        first = client.post("/api/v1/points/signin", headers=auth(token))
        assert first.status_code in (200, 400)
        second = client.post("/api/v1/points/signin", headers=auth(token))
        assert second.status_code == 400


class TestMeetSecurity:
    def test_meet_participants_and_arrival_guard(self, client, state):
        token_a = state["a"]["access_token"]
        token_b = state["b"]["access_token"]
        token_c = state["c"]["access_token"]
        pet_a = register_pet(client, token_a, "碰头A")
        pet_b = register_pet(client, token_b, "碰头B")
        register_device(client, token_a, pet_a, state["suffix"] + "A", 34.7466)
        register_device(client, token_b, pet_b, state["suffix"] + "B", 34.7486)

        resp = client.post("/api/v1/social/meets", headers=auth(token_a), json={
            "receiver_pet_id": pet_b, "start_lat": 34.7466, "start_lng": 113.6253
        })
        assert resp.status_code == 200, resp.text
        meet_id = resp.json()["data"]["id"]
        assert client.put(f"/api/v1/social/meets/{meet_id}/confirm", headers=auth(token_b), json={}).status_code == 200

        assert client.get(f"/api/v1/social/meets/{meet_id}/distance", headers=auth(token_c)).status_code == 403
        assert client.put(f"/api/v1/social/meets/{meet_id}/complete", headers=auth(token_c), json={}).status_code == 403
        assert client.put(f"/api/v1/social/meets/{meet_id}/cancel", headers=auth(token_c), json={}).status_code == 403
        assert client.put(f"/api/v1/social/meets/{meet_id}/complete", headers=auth(token_b), json={}).status_code == 400
