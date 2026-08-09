"""
宠迹 PawTrack — API 集成测试

需要可用的 PostgreSQL + Redis，通过环境变量 PAWRACK_TEST_DB=1 启用。
未启用时 conftest 自动跳过。

覆盖：
- /health 与 / 根路径
- admin 登录 + dashboard 鉴权
- 未授权访问受保护接口返回 401
"""
import os
import pytest

pytestmark = pytest.mark.integration

from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c


class TestSystem:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["version"] == "0.4.0"

    def test_root(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        body = resp.json()
        assert "admin" in body["modules"]
        assert body["version"] == "0.4.0"


class TestAdminAuth:
    def test_admin_login_success(self, client):
        resp = client.post("/api/v1/admin/login", json={
            "username": os.environ.get("ADMIN_USERNAME", "admin"),
            "password": os.environ.get("ADMIN_PASSWORD", "pawtrack_admin_2026")
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["access_token"]
        assert data["role"] == "super_admin"

    def test_admin_login_wrong_password(self, client):
        resp = client.post("/api/v1/admin/login", json={"username": "admin", "password": "wrong"})
        assert resp.status_code == 401

    def test_admin_dashboard_requires_token(self, client):
        """无 token 访问 dashboard 应 401"""
        resp = client.get("/api/v1/admin/dashboard")
        assert resp.status_code == 401

    def test_admin_dashboard_with_token(self, client):
        """有效 admin token 应能访问 dashboard"""
        login = client.post("/api/v1/admin/login", json={
            "username": os.environ.get("ADMIN_USERNAME", "admin"),
            "password": os.environ.get("ADMIN_PASSWORD", "pawtrack_admin_2026")
        })
        token = login.json()["data"]["access_token"]
        resp = client.get("/api/v1/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "users" in data
        assert "revenue" in data

    def test_app_token_cannot_access_admin(self, client):
        """app 端 token（aud=pawtrack-app）不能访问 admin 接口"""
        from app.auth import create_access_token
        app_token = create_access_token(1, "138", "free", [])
        resp = client.get("/api/v1/admin/dashboard", headers={"Authorization": f"Bearer {app_token}"})
        assert resp.status_code == 401


class TestAppAuthProtection:
    def test_pets_list_requires_auth(self, client):
        """未授权访问受保护接口返回 401"""
        resp = client.get("/api/v1/pets")
        assert resp.status_code == 401
