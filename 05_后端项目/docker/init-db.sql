-- 宠迹 PawTrack 数据库初始化脚本
-- PostgreSQL 16 + PostGIS 3.4
-- 自动执行（Docker Compose 首次启动）

-- 1. 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. 创建枚举类型
CREATE TYPE member_level AS ENUM ('free', 'basic', 'pro');
CREATE TYPE user_status AS ENUM ('active', 'blocked');
CREATE TYPE pet_type AS ENUM ('cat', 'dog');
CREATE TYPE pet_gender AS ENUM ('male', 'female', 'unknown');
CREATE TYPE pet_status AS ENUM ('active', 'deleted');
CREATE TYPE device_status AS ENUM ('online', 'offline', 'low_battery');
CREATE TYPE device_hw_type AS ENUM ('cat', 'dog');
CREATE TYPE alarm_type AS ENUM ('leave_fence', 'leave_fence_cat', 'enter_fence', 'low_battery', 'low_battery_critical', 'offline_warning', 'tamper_detected', 'fall_detected');
CREATE TYPE alarm_severity AS ENUM ('high', 'medium', 'low');
CREATE TYPE alarm_status AS ENUM ('active', 'handled', 'false_positive');
CREATE TYPE meet_status AS ENUM ('pending', 'confirmed', 'success', 'failed', 'cancelled');
CREATE TYPE order_type AS ENUM ('hardware', 'subscription', 'accessory');
CREATE TYPE order_status AS ENUM ('pending', 'paid', 'failed', 'cancelled', 'refunded');
CREATE TYPE pay_channel AS ENUM ('wechat', 'alipay', 'apple');
CREATE TYPE subscription_plan AS ENUM ('basic_month', 'basic_year', 'pro_month', 'pro_year');
CREATE TYPE subscription_status AS ENUM ('active', 'expired', 'cancelled');
CREATE TYPE point_type AS ENUM ('meet', 'invite', 'signin', 'purchase', 'expire', 'admin');
CREATE TYPE privacy_level AS ENUM ('public', 'friends', 'private');
CREATE TYPE outbox_status AS ENUM ('pending', 'sent', 'failed');

-- 3. 创建核心表
-- 3.1 用户表
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,
    nickname VARCHAR(50),
    avatar VARCHAR(255),
    wechat_openid VARCHAR(64) UNIQUE,
    apple_id VARCHAR(64) UNIQUE,
    password_hash VARCHAR(128),
    member_level member_level DEFAULT 'free' NOT NULL,
    member_expire_at TIMESTAMP WITH TIME ZONE,
    points INTEGER DEFAULT 0,
    privacy_location privacy_level DEFAULT 'friends',
    status user_status DEFAULT 'active',
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_wechat ON users(wechat_openid);
CREATE INDEX idx_users_member ON users(member_level) WHERE status = 'active';

-- 3.2 宠物表
CREATE TABLE pets (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    type pet_type NOT NULL,
    breed VARCHAR(50),
    gender pet_gender DEFAULT 'unknown',
    birthday DATE,
    weight DECIMAL(5,2),
    avatar VARCHAR(255),
    fence_enabled BOOLEAN DEFAULT true,
    fence_center GEOGRAPHY(Point, 4326),
    fence_radius INTEGER DEFAULT 100,
    status pet_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_pets_user_id ON pets(user_id);
CREATE INDEX idx_pets_type ON pets(type);
CREATE INDEX idx_pets_fence_center ON pets USING GIST (fence_center);

-- 3.3 设备表
CREATE TABLE devices (
    id BIGSERIAL PRIMARY KEY,
    sn VARCHAR(32) UNIQUE NOT NULL,
    pet_id BIGINT REFERENCES pets(id) ON DELETE SET NULL,
    user_id BIGINT NOT NULL REFERENCES users(id),
    hardware_type device_hw_type NOT NULL,
    firmware_version VARCHAR(20) DEFAULT '1.0.0',
    battery_level INTEGER DEFAULT 100 CHECK (battery_level >= 0 AND battery_level <= 100),
    status device_status DEFAULT 'offline',
    last_online_at TIMESTAMP WITH TIME ZONE,
    sim_iccid VARCHAR(32),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_devices_sn ON devices(sn);
CREATE INDEX idx_devices_pet_id ON devices(pet_id);
CREATE INDEX idx_devices_user_id ON devices(user_id);

-- 3.4 报警记录表（按月分区）
CREATE TABLE alarms (
    id BIGSERIAL,
    pet_id BIGINT NOT NULL REFERENCES pets(id),
    user_id BIGINT NOT NULL REFERENCES users(id),
    device_id BIGINT REFERENCES devices(id),
    type alarm_type NOT NULL,
    severity alarm_severity DEFAULT 'medium',
    lat DECIMAL(11,8),
    lng DECIMAL(12,8),
    address VARCHAR(255),
    status alarm_status DEFAULT 'active',
    handled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- 创建初始分区
CREATE TABLE alarms_2026_07 PARTITION OF alarms
  FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');
CREATE TABLE alarms_2026_08 PARTITION OF alarms
  FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');

CREATE INDEX idx_alarms_pet_id ON alarms(pet_id, created_at DESC);
CREATE INDEX idx_alarms_user_id ON alarms(user_id, created_at DESC);
CREATE INDEX idx_alarms_created_at ON alarms(created_at DESC);

-- 3.5 碰头记录表
CREATE TABLE meets (
    id BIGSERIAL PRIMARY KEY,
    initiator_pet_id BIGINT NOT NULL REFERENCES pets(id),
    receiver_pet_id BIGINT NOT NULL REFERENCES pets(id),
    status meet_status DEFAULT 'pending',
    start_lat DECIMAL(11,8),
    start_lng DECIMAL(12,8),
    end_lat DECIMAL(11,8),
    end_lng DECIMAL(12,8),
    started_at TIMESTAMP WITH TIME ZONE,
    confirmed_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    points_awarded INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_meets_initiator ON meets(initiator_pet_id, created_at DESC);
CREATE INDEX idx_meets_receiver ON meets(receiver_pet_id, created_at DESC);

-- 3.6 订单表
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    order_no VARCHAR(32) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL REFERENCES users(id),
    type order_type NOT NULL,
    product_id VARCHAR(50),
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    status order_status DEFAULT 'pending',
    pay_channel pay_channel,
    transaction_id VARCHAR(64),
    paid_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE UNIQUE INDEX idx_orders_transaction_id ON orders(transaction_id) WHERE transaction_id IS NOT NULL;
CREATE INDEX idx_orders_user_id ON orders(user_id, created_at DESC);

-- 3.7 订阅记录表
CREATE TABLE subscriptions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    order_id BIGINT REFERENCES orders(id),
    plan subscription_plan NOT NULL,
    status subscription_status DEFAULT 'active',
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    expire_at TIMESTAMP WITH TIME ZONE NOT NULL,
    auto_renew BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (order_id)
);
CREATE INDEX idx_subs_user_id ON subscriptions(user_id, status);
CREATE INDEX idx_subs_expire ON subscriptions(expire_at) WHERE status = 'active';

-- 3.8 积分记录表
CREATE TABLE points_log (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    change INTEGER NOT NULL,
    type point_type NOT NULL,
    related_id VARCHAR(50),
    balance INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_points_user_id ON points_log(user_id, created_at DESC);

-- 3.9 本地消息表（Outbox Pattern）
CREATE TABLE event_outbox (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    status outbox_status DEFAULT 'pending',
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sent_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX idx_outbox_status ON event_outbox(status, created_at);

-- 4. 验证
SELECT '✅ 宠迹数据库初始化完成' AS result;
