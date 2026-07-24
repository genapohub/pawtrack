"""
宠迹 PawTrack — 模型枚举与套餐配置单测

覆盖：
- 枚举值与 init-db.sql / PRD 数据字典一致
- orders 路由的 PLAN_CONFIG 套餐价格与 PRD 一致
- 积分奖励规则
"""
import pytest

from app.enums import (
    MemberLevel, PetType, PetGender, DeviceStatus, AlarmType,
    AlarmSeverity, AlarmStatus, MeetStatus, OrderStatus, PayChannel,
    SubscriptionPlan, SubscriptionStatus, PointType, PrivacyLevel
)
from app.plans import PLAN_CONFIG


class TestEnums:
    def test_member_level(self):
        assert {e.value for e in MemberLevel} == {"free", "basic", "pro"}

    def test_pet_type(self):
        assert {e.value for e in PetType} == {"cat", "dog"}

    def test_pet_gender(self):
        assert {e.value for e in PetGender} == {"male", "female", "unknown"}

    def test_device_status(self):
        assert {e.value for e in DeviceStatus} == {"online", "offline", "low_battery"}

    def test_alarm_type(self):
        values = {e.value for e in AlarmType}
        assert "leave_fence" in values
        assert "low_battery" in values
        assert "tamper_detected" in values

    def test_alarm_status(self):
        assert {e.value for e in AlarmStatus} == {"active", "handled", "false_positive"}

    def test_meet_status(self):
        assert {e.value for e in MeetStatus} == {"pending", "confirmed", "success", "failed", "cancelled"}

    def test_order_status(self):
        assert {e.value for e in OrderStatus} == {"pending", "paid", "failed", "cancelled", "refunded"}

    def test_pay_channel(self):
        assert {e.value for e in PayChannel} == {"wechat", "alipay", "apple"}

    def test_subscription_plan(self):
        assert {e.value for e in SubscriptionPlan} == {"basic_month", "basic_year", "pro_month", "pro_year"}

    def test_point_type(self):
        assert {e.value for e in PointType} == {"meet", "invite", "signin", "purchase", "expire", "admin"}

    def test_privacy_level(self):
        assert {e.value for e in PrivacyLevel} == {"public", "friends", "private"}


class TestPlanConfig:
    """套餐配置与 PRD 会员价格一致：basic ¥19.9/月，pro ¥29.9/月"""

    def test_basic_month_price(self):
        assert PLAN_CONFIG[SubscriptionPlan.basic_month]["price"] == 19.9
        assert PLAN_CONFIG[SubscriptionPlan.basic_month]["days"] == 30
        assert PLAN_CONFIG[SubscriptionPlan.basic_month]["level"] == "basic"

    def test_pro_month_price(self):
        assert PLAN_CONFIG[SubscriptionPlan.pro_month]["price"] == 29.9
        assert PLAN_CONFIG[SubscriptionPlan.pro_month]["level"] == "pro"

    def test_year_plan_discount(self):
        """年卡应比月卡×12 更优惠"""
        basic_month_total = PLAN_CONFIG[SubscriptionPlan.basic_month]["price"] * 12
        basic_year = PLAN_CONFIG[SubscriptionPlan.basic_year]["price"]
        assert basic_year < basic_month_total

        pro_month_total = PLAN_CONFIG[SubscriptionPlan.pro_month]["price"] * 12
        pro_year = PLAN_CONFIG[SubscriptionPlan.pro_year]["price"]
        assert pro_year < pro_month_total

    def test_all_plans_have_required_fields(self):
        for plan_key, cfg in PLAN_CONFIG.items():
            assert "name" in cfg
            assert "price" in cfg and cfg["price"] > 0
            assert "level" in cfg and cfg["level"] in ("basic", "pro")
            assert "days" in cfg and cfg["days"] in (30, 365)
