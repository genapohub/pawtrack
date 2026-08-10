"""
宠迹 PawTrack — 数据库模型（SQLAlchemy ORM）
"""
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean, DateTime, ForeignKey,
    Numeric, Enum as SQLEnum, Index, UniqueConstraint, func
)
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
from typing import Any

# ── 自定义类型 ──────────────────────────────────────────────

class Base(DeclarativeBase):
    pass

# ── 枚举（与 init-db.sql 保持一致）──────────────────────────
# 枚举定义统一维护在 app/enums.py，此处复用，避免循环导入

from app.enums import (
    MemberLevel, PetType, PetGender, DeviceStatus,
    AlarmType, AlarmSeverity, AlarmStatus, MeetStatus,
    OrderStatus, PayChannel, SubscriptionPlan, SubscriptionStatus,
    PointType, PrivacyLevel
)

# ── 用户表 ──────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    nickname = Column(String(50))
    avatar = Column(String(255))
    wechat_openid = Column(String(64), unique=True)
    apple_id = Column(String(64), unique=True)
    password_hash = Column(String(128))
    member_level = Column(SQLEnum(MemberLevel), default=MemberLevel.free, nullable=False)
    member_expire_at = Column(DateTime(timezone=True))
    points = Column(Integer, default=0, nullable=False)
    privacy_location = Column(SQLEnum(PrivacyLevel), default=PrivacyLevel.friends)
    invite_code = Column(String(20), unique=True, index=True)  # 我的邀请码
    invited_by = Column(BigInteger)  # 邀请人 user_id（注册时记录）
    emergency_contacts = Column(JSON, default=list)  # [{name, phone}]
    notify_push = Column(Boolean, default=True)  # Push 通知开关
    notify_sms = Column(Boolean, default=False)  # 短信通知开关（Pro 权益）
    status = Column(String(20), default="active")
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # 关系
    pets = relationship("Pet", back_populates="owner", cascade="all, delete-orphan")
    devices = relationship("Device", back_populates="owner")
    subscriptions = relationship("Subscription", back_populates="user")

# ── 宠物表 ──────────────────────────────────────────────────

class Pet(Base):
    __tablename__ = "pets"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    type = Column(SQLEnum(PetType), nullable=False)
    breed = Column(String(50))
    gender = Column(SQLEnum(PetGender), default=PetGender.unknown)
    birthday = Column(DateTime(timezone=True))
    weight = Column(Numeric(5, 2))
    avatar = Column(String(255))
    fence_enabled = Column(Boolean, default=True)
    fence_center_lat = Column(Numeric(10, 7))
    fence_center_lng = Column(Numeric(10, 7))
    fence_radius = Column(Integer, default=100)
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    __table_args__ = ()

    # 关系
    owner = relationship("User", back_populates="pets")
    device = relationship("Device", back_populates="pet", uselist=False)
    alarms = relationship("Alarm", back_populates="pet")

# ── 设备表 ──────────────────────────────────────────────────

class Device(Base):
    __tablename__ = "devices"

    id = Column(BigInteger, primary_key=True)
    sn = Column(String(32), unique=True, nullable=False, index=True)
    pet_id = Column(BigInteger, ForeignKey("pets.id", ondelete="SET NULL"))
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True, index=True)  # 设备先注册后绑定用户
    hardware_type = Column(String(20), nullable=False)  # cat / dog
    firmware_version = Column(String(20), default="1.0.0")
    battery_level = Column(Integer, default=100)
    status = Column(SQLEnum(DeviceStatus), default=DeviceStatus.offline)
    last_online_at = Column(DateTime(timezone=True))
    sim_iccid = Column(String(32))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # 关系
    owner = relationship("User", back_populates="devices")
    pet = relationship("Pet", back_populates="device")

# ── 报警记录表 ──────────────────────────────────────────────

class Alarm(Base):
    __tablename__ = "alarms"

    id = Column(BigInteger, primary_key=True)
    pet_id = Column(BigInteger, ForeignKey("pets.id"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    device_id = Column(BigInteger, ForeignKey("devices.id"))
    type = Column(SQLEnum(AlarmType), nullable=False)
    severity = Column(SQLEnum(AlarmSeverity), default=AlarmSeverity.medium)
    lat = Column(Numeric(11, 8))
    lng = Column(Numeric(12, 8))
    address = Column(String(255))
    status = Column(SQLEnum(AlarmStatus), default=AlarmStatus.active)
    handled_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now())

    __table_args__ = (
        Index("idx_alarms_pet_created", pet_id, created_at.desc()),
        Index("idx_alarms_user_created", user_id, created_at.desc()),
        Index("idx_alarms_status_created", status, created_at.desc()),
    )

    pet = relationship("Pet", back_populates="alarms")

# ── 碰头记录表 ──────────────────────────────────────────────

class Meet(Base):
    __tablename__ = "meets"

    id = Column(BigInteger, primary_key=True)
    initiator_pet_id = Column(BigInteger, ForeignKey("pets.id"), nullable=False, index=True)
    receiver_pet_id = Column(BigInteger, ForeignKey("pets.id"), nullable=False, index=True)
    status = Column(SQLEnum(MeetStatus), default=MeetStatus.pending)
    start_lat = Column(Numeric(11, 8))
    start_lng = Column(Numeric(12, 8))
    end_lat = Column(Numeric(11, 8))
    end_lng = Column(Numeric(12, 8))
    started_at = Column(DateTime(timezone=True))
    confirmed_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    points_awarded = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=func.now())

    __table_args__ = (
        Index("idx_meets_status_created", status, created_at.desc()),
    )

# ── 订单表 ──────────────────────────────────────────────────

class Order(Base):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True)
    order_no = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(20), nullable=False)
    product_id = Column(String(50))
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.pending)
    pay_channel = Column(SQLEnum(PayChannel))
    transaction_id = Column(String(64), unique=True)
    paid_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now())

    __table_args__ = (
        Index("idx_orders_status_created", status, created_at.desc()),
    )

# ── 订阅记录表 ──────────────────────────────────────────────

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), unique=True)
    plan = Column(SQLEnum(SubscriptionPlan), nullable=False)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.active)
    started_at = Column(DateTime(timezone=True), nullable=False)
    expire_at = Column(DateTime(timezone=True), nullable=False)
    auto_renew = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=func.now())

    user = relationship("User", back_populates="subscriptions")

# ── 积分记录表 ──────────────────────────────────────────────

class PointsLog(Base):
    __tablename__ = "points_log"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    change = Column(Integer, nullable=False)
    type = Column(SQLEnum(PointType), nullable=False)
    related_id = Column(String(50))
    balance = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    __table_args__ = (
        Index("idx_points_user_created", user_id, created_at.desc()),
    )

# ── 本地消息表（Outbox Pattern）─────────────────────────────

class EventOutbox(Base):
    __tablename__ = "event_outbox"

    id = Column(BigInteger, primary_key=True)
    event_type = Column(String(50), nullable=False)
    payload = Column(Text, nullable=False)  # JSONB 在 init-db 中 ALTER
    status = Column(String(20), default="pending")
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=func.now())
    sent_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_outbox_status_created", status, created_at.desc()),
    )
