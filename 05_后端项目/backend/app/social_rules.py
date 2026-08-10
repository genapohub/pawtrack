"""
宠迹 PawTrack — 社交业务规则（纯逻辑，无依赖导入）

对齐 PRD 11.2 碰头状态机 / 16.1 碰头防作弊 / 16.3 积分收支：
- 发起碰头最小距离：>50m
- 碰头成功积分：双方各 +100
- 同一对手每日上限：1 次
- Haversine 球面距离计算

独立成模块是为了避免 social.py 与 app.main 的循环导入，同时便于单元测试。
"""
import math

# ── 业务常量 ──────────────────────────────────────────────
MEET_MIN_DISTANCE = 50    # 发起碰头最小距离（米，>50m 才可发起）
MEET_POINTS = 100         # 碰头成功双方各得积分
DAILY_MEET_LIMIT = 1      # 同一对手每日碰头上限


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Haversine 球面距离（米）"""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
