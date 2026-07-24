"""
宠迹 PawTrack — Locust 性能压测脚本

用法：
    cd backend
    pip install locust
    locust -f tests/load/locustfile.py --host=http://localhost:8000

然后在浏览器打开 http://localhost:8089 配置并发用户数与爬坡速率。

场景：
    1. MobileUser   — 模拟 App 用户：登录→宠物/设备列表→位置查询→报警→社交
    2. DeviceReport — 模拟设备高频上报位置（最关键性能场景）
    3. AdminUser    — 模拟后台运营：登录→dashboard→各管理列表

性能基线（单实例参考，2C4G）：
    - 登录 P95 < 200ms
    - 宠物/设备列表 P95 < 100ms
    - 位置上报 P95 < 50ms（Redis Stream 写入）
    - 报警列表 P95 < 150ms
    - 附近宠物 P95 < 200ms（Redis GEO）
    - 整体错误率 < 0.5%
"""
import random
import time
from locust import HttpUser, task, between, tag


def random_phone() -> str:
    """生成随机手机号（13xxxxxxxxx）"""
    return "13" + "".join(str(random.randint(0, 9)) for _ in range(9))


def random_coord() -> tuple[float, float]:
    """生成随机经纬度（北京周边）"""
    lat = round(random.uniform(39.8, 40.0), 6)
    lng = round(random.uniform(116.3, 116.5), 6)
    return lat, lng


class MobileUser(HttpUser):
    """模拟 App 用户行为"""
    wait_time = between(1, 3)
    weight = 5  # 占比最大

    def on_start(self):
        """登录获取 token"""
        phone = random_phone()
        # 注册（MVP 阶段验证码任意）
        r = self.client.post("/api/v1/auth/register", json={
            "phone": phone, "code": "1234", "nickname": f"压测用户{phone[-4:]}"
        }, name="注册")
        if r.status_code != 200:
            # 已注册则登录
            r = self.client.post("/api/v1/auth/login", json={
                "phone": phone, "code": "1234"
            }, name="登录")
        try:
            self.token = r.json()["data"]["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        except Exception:
            self.token = None
            self.headers = {}

    @task(3)
    @tag("read", "pets")
    def list_pets(self):
        self.client.get("/api/v1/pets", headers=self.headers, name="宠物列表")

    @task(3)
    @tag("read", "devices")
    def list_devices(self):
        self.client.get("/api/v1/devices", headers=self.headers, name="设备列表")

    @task(2)
    @tag("read", "alarms")
    def list_alarms(self):
        self.client.get("/api/v1/alarms?status=active&page=1&size=20",
                        headers=self.headers, name="报警列表")

    @task(2)
    @tag("read", "alarms")
    def unread_alarms(self):
        self.client.get("/api/v1/alarms/unread/count",
                        headers=self.headers, name="未读报警数")

    @task(2)
    @tag("read", "social")
    def nearby_pets(self):
        lat, lng = random_coord()
        self.client.get(f"/api/v1/social/nearby?lat={lat}&lng={lng}&radius=1000",
                        headers=self.headers, name="附近宠物")

    @task(1)
    @tag("read", "orders")
    def list_plans(self):
        self.client.get("/api/v1/orders/plans", headers=self.headers, name="套餐列表")

    @task(1)
    @tag("read", "points")
    def points_balance(self):
        self.client.get("/api/v1/points/balance", headers=self.headers, name="积分余额")


class DeviceReport(HttpUser):
    """模拟设备高频上报位置（性能关键路径）"""
    wait_time = between(0.1, 0.5)  # 高频：每 0.1-0.5s 上报一次
    weight = 3

    def on_start(self):
        # 设备上报不需要用户 token（内网调用），但需有效 device_id
        # 压测时假设 device_id=1 存在；若不存在会 404，错误率会反映
        self.device_id = random.randint(1, 100)

    @task
    @tag("write", "location")
    def upload_location(self):
        lat, lng = random_coord()
        self.client.post("/api/v1/location/upload", json={
            "device_id": self.device_id,
            "lat": lat,
            "lng": lng,
            "accuracy": 5.0,
            "speed": 0.0,
            "source": "gps",
            "is_indoor": False,
            "battery": random.randint(20, 100),
            "ts": int(time.time())
        }, name="位置上报")


class AdminUser(HttpUser):
    """模拟后台运营"""
    wait_time = between(2, 5)
    weight = 1

    def on_start(self):
        r = self.client.post("/api/v1/admin/login", json={
            "username": "admin", "password": "pawtrack_admin_2026"
        }, name="Admin登录")
        try:
            self.token = r.json()["data"]["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        except Exception:
            self.token = None
            self.headers = {}

    @task(2)
    @tag("admin")
    def dashboard(self):
        self.client.get("/api/v1/admin/dashboard", headers=self.headers, name="Admin Dashboard")

    @task(1)
    @tag("admin")
    def list_users(self):
        self.client.get("/api/v1/admin/users?page=1&size=20",
                        headers=self.headers, name="Admin 用户列表")

    @task(1)
    @tag("admin")
    def list_orders(self):
        self.client.get("/api/v1/admin/orders?status=paid&page=1&size=20",
                        headers=self.headers, name="Admin 订单列表")

    @task(1)
    @tag("admin")
    def list_alarms(self):
        self.client.get("/api/v1/admin/alarms?status=active&page=1&size=20",
                        headers=self.headers, name="Admin 报警列表")
