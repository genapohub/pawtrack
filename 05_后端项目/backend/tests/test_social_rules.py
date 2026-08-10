"""
宠迹 PawTrack — 社交业务规则单元测试（V2.0）

覆盖 PRD 16.1/11.2 规则：
- 碰头成功积分 = 100（MEET_POINTS）
- 发起碰头最小距离 >50m（MEET_MIN_DISTANCE）
- 同一对手每日限 1 次（DAILY_MEET_LIMIT）
- Haversine 距离计算正确性
"""
import math
import pytest

from app.social_rules import (
    MEET_MIN_DISTANCE, MEET_POINTS, DAILY_MEET_LIMIT,
    haversine
)


class TestMeetRules:
    def test_meet_points_is_100(self):
        """PRD 16.3：碰头成功双方各得 100 积分"""
        assert MEET_POINTS == 100

    def test_meet_min_distance_is_50(self):
        """PRD 11.2：发起碰头需距离 >50m"""
        assert MEET_MIN_DISTANCE == 50

    def test_daily_limit_is_1(self):
        """PRD 16.1：同一对手每日限 1 次"""
        assert DAILY_MEET_LIMIT == 1


class TestHaversine:
    def test_zero_distance(self):
        """同一点距离为 0"""
        assert haversine(34.7466, 113.6253, 34.7466, 113.6253) < 0.01

    def test_known_distance(self):
        """郑州→北京约 690km ±10%"""
        d = haversine(34.7466, 113.6253, 39.9042, 116.4074)
        assert 620_000 < d < 760_000

    def test_distance_below_50m(self):
        """相距 30m 内，不允许发起碰头"""
        # 1 度纬度 ≈ 111km，30m ≈ 0.00027 度
        d = haversine(34.7466, 113.6253, 34.7466 + 0.00027, 113.6253)
        assert d < MEET_MIN_DISTANCE

    def test_distance_above_50m(self):
        """相距 100m 以上，允许发起碰头"""
        d = haversine(34.7466, 113.6253, 34.7466 + 0.001, 113.6253)
        assert d > MEET_MIN_DISTANCE
