"""
宠迹 PawTrack — 枚举定义（纯 Python，无数据库依赖）

与 init-db.sql 枚举类型及 PRD 数据字典保持一致。
models.py 与各路由从此导入，便于单独测试。
"""
from enum import Enum


class MemberLevel(str, Enum):
    free = "free"
    basic = "basic"
    pro = "pro"


class PetType(str, Enum):
    cat = "cat"
    dog = "dog"


class PetGender(str, Enum):
    male = "male"
    female = "female"
    unknown = "unknown"


class DeviceStatus(str, Enum):
    online = "online"
    offline = "offline"
    low_battery = "low_battery"


class AlarmType(str, Enum):
    leave_fence = "leave_fence"
    leave_fence_cat = "leave_fence_cat"
    enter_fence = "enter_fence"
    low_battery = "low_battery"
    low_battery_critical = "low_battery_critical"
    offline_warning = "offline_warning"
    tamper_detected = "tamper_detected"
    fall_detected = "fall_detected"


class AlarmSeverity(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class AlarmStatus(str, Enum):
    active = "active"
    handled = "handled"
    false_positive = "false_positive"


class MeetStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    success = "success"
    failed = "failed"
    cancelled = "cancelled"


class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    cancelled = "cancelled"
    refunded = "refunded"


class PayChannel(str, Enum):
    wechat = "wechat"
    alipay = "alipay"
    apple = "apple"


class SubscriptionPlan(str, Enum):
    basic_month = "basic_month"
    basic_year = "basic_year"
    pro_month = "pro_month"
    pro_year = "pro_year"


class SubscriptionStatus(str, Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"


class PointType(str, Enum):
    meet = "meet"
    invite = "invite"
    signin = "signin"
    purchase = "purchase"
    expire = "expire"
    admin = "admin"


class PrivacyLevel(str, Enum):
    public = "public"
    friends = "friends"
    private = "private"
