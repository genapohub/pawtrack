"""
宠迹 PawTrack — 会员套餐配置（纯 Python，无数据库依赖）

与 PRD 会员等级价格一致：basic ¥19.9/月，pro ¥29.9/月。
orders 路由与测试从此导入，便于单独测试。
"""
from app.enums import SubscriptionPlan

PLAN_CONFIG = {
    SubscriptionPlan.basic_month: {"name": "基础版月卡", "price": 19.9, "level": "basic", "days": 30},
    SubscriptionPlan.basic_year: {"name": "基础版年卡", "price": 199.0, "level": "basic", "days": 365},
    SubscriptionPlan.pro_month: {"name": "Pro版月卡", "price": 29.9, "level": "pro", "days": 30},
    SubscriptionPlan.pro_year: {"name": "Pro版年卡", "price": 299.0, "level": "pro", "days": 365},
}
