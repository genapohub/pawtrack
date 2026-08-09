# 宠迹 PawTrack — API 接口设计文档

> 版本：V1.0 | 日期：2026-07-21  
> 适用：前端 App + 后台管理系统 + 设备服务  
> 状态：待评审

---

## 1. API 总览

### 1.1 基础信息

| 参数 | 值 |
|------|----|
| 协议 | HTTPS + WSS（WebSocket） |
| 域名 | `api.pawtrack.app` |
| API 根路径 | `/api/v1` |
| 认证方式 | JWT RS256（双 Token） |
| 数据格式 | JSON |
| 字符编码 | UTF-8 |
| 时间格式 | Unix 时间戳（秒） |

### 1.2 API 版本管理

```
/api/v1/...   ← 当前版本
/api/v2/...   ← 未来版本（向后兼容）
```

- 版本号在 URL 路径中体现
- 废弃版本提前 3 个月通知，保留 6 个月

---

## 2. JWT 双 Token 规范

### 2.1 算法与密钥

| 参数 | 值 |
|------|----|
| 算法 | **RS256**（RSA + SHA-256） |
| 公钥 | 前端/服务间验证用（JWKS 端点） |
| 私钥 | 仅认证服务持有，不对外暴露 |
| JWKS 端点 | `GET /api/v1/.well-known/jwks.json` |

> **为什么 RS256 而不是 HS256？**
> 微服务场景下，HS256 需要所有服务共享同一个密钥，存在密钥泄露风险。
> RS256 私钥签名、公钥验证，各服务只需持有公钥，更安全。

### 2.2 Token 结构

#### Access Token（访问令牌）

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "pawtrack-rsa-001"
  },
  "payload": {
    "iss": "https://api.pawtrack.app",
    "sub": "12345",                 // user_id
    "aud": "pawtrack-app",         // 受众
    "exp": 1721539200,              // 过期时间（2小时后）
    "iat": 1721532000,              // 签发时间
    "jti": "uuid-xxx",              // JWT ID（防重放）
    "phone": "138****8888",         // 手机号（脱敏）
    "member_level": "pro",          // 会员等级：free/basic/pro
    "device_ids": [1, 2, 3],       // 用户绑定的设备ID列表
    "token_type": "access"
  }
}
```

#### Refresh Token（刷新令牌）

```json
{
  "payload": {
    "iss": "https://api.pawtrack.app",
    "sub": "12345",
    "exp": 1724124000,              // 过期时间（30天后）
    "iat": 1721532000,
    "jti": "uuid-yyy",
    "token_family": "fam-001",      // Token 家族（用于批量吊销）
    "token_type": "refresh"
  }
}
```

### 2.3 Token 刷新流程

```
App 请求 API
  │
  ├─ access_token 有效？─── YES ──→ 正常返回数据
  │
  ├─ access_token 过期？─── YES ──→
  │     │
  │     ├─ 用 refresh_token 调用 POST /api/v1/auth/refresh
  │     │     │
  │     │     ├─ 成功 → 返回新的 access_token + refresh_token
  │     │     │     （旧 refresh_token 立刻失效）
  │     │     │
  │     │     └─ refresh_token 也过期 → 返回 401
  │     │           → App 跳转登录页
  │     │
  │     └─ refresh_token 未过期 → 用新 access_token 重试原请求
  │
  └─ access_token 无效（篡改/签名错误）──→ 返回 401
```

### 2.4 Token 传递方式

```
HTTP Header:
  Authorization: Bearer <access_token>

WebSocket 连接：
  URL: wss://api.pawtrack.app/ws/v1?token=<access_token>
  或连接后第一条消息发送：
  { "type": "auth", "token": "<access_token>" }
```

### 2.5 多设备登录策略

| 策略 | 说明 |
|------|------|
| 单设备登录（默认） | 新设备登录 → 旧设备 refresh_token 失效 → 旧设备下次请求时 401 |
| 多设备登录（Pro） | 允许同时 3 台设备在线，超出后踢出最早登录的设备 |
| 强制下线 | `DELETE /api/v1/auth/sessions` 清除所有 refresh_token |

---

## 3. 通用响应格式

### 3.1 成功响应

```json
{
  "code": 0,
  "message": "success",
  "data": { ... },
  "meta": {
    "timestamp": 1721532000,
    "request_id": "req-uuid-xxx"
  }
}
```

### 3.2 分页响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [ ... ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5
    }
  },
  "meta": { ... }
}
```

### 3.3 错误响应

```json
{
  "code": 40101,
  "message": "access_token 已过期，请刷新",
  "errors": [
    { "field": "token", "message": "expired" }
  ],
  "meta": {
    "timestamp": 1721532000,
    "request_id": "req-uuid-xxx"
  }
}
```

---

## 4. 错误码规范

### 4.1 错误码分段

| 段 | 范围 | 说明 |
|----|------|------|
| 1xxxx | 10000-19999 | 认证/授权错误 |
| 2xxxx | 20000-29999 | 用户/宠物/设备资源错误 |
| 3xxxx | 30000-39999 | 定位/围栏错误 |
| 4xxxx | 40000-49999 | 订单/支付错误 |
| 5xxxx | 50000-59999 | 社交/积分错误 |
| 9xxxx | 90000-99999 | 系统错误 |

### 4.2 详细错误码

#### 认证错误（1xxxx）

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|------------|
| 10001 | 未提供 Token | 401 |
| 10002 | Token 格式错误 | 401 |
| 10003 | Token 已过期 | 401 |
| 10004 | Token 无效（签名错误） | 401 |
| 10005 | Token 已被吊销 | 401 |
| 10006 | 无权限访问该资源 | 403 |
| 10007 | Refresh Token 已过期 | 401 |
| 10008 | Refresh Token 无效 | 401 |

#### 资源错误（2xxxx）

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|------------|
| 20001 | 用户不存在 | 404 |
| 20002 | 宠物不存在 | 404 |
| 20003 | 设备不存在 | 404 |
| 20004 | 设备 SN 已被绑定 | 400 |
| 20005 | 设备未绑定到当前用户 | 403 |
| 20006 | 宠物数量已达上限（免费版3只） | 400 |

#### 定位错误（3xxxx）

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|------------|
| 30001 | 设备离线 | 400 |
| 30002 | 围栏未设置 | 400 |
| 30003 | 定位权限未开启 | 403 |

#### 订单/支付错误（4xxxx）

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|------------|
| 40001 | 订单不存在 | 404 |
| 40002 | 订单已支付 | 400 |
| 40003 | 支付失败 | 400 |
| 40004 | 会员已过期 | 400 |

---

## 5. 接口清单

### 5.1 认证模块

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | `/auth/register` | 手机号注册 | 否 |
| POST | `/auth/login` | 手机号/微信/Apple登录 | 否 |
| POST | `/auth/refresh` | 刷新 Token | 否（需 refresh_token） |
| DELETE | `/auth/logout` | 退出登录 | 是 |
| DELETE | `/auth/sessions` | 清除所有会话 | 是 |
| GET | `/auth/.well-known/jwks.json` | 获取公钥 | 否 |

---

### 5.2 用户模块

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | `/users/me` | 获取当前用户信息 | 是 |
| PUT | `/users/me` | 更新用户信息 | 是 |
| PUT | `/users/me/password` | 修改密码 | 是 |
| GET | `/users/me/devices` | 获取我的设备列表 | 是 |
| DELETE | `/users/me` | 注销账号 | 是 |

---

### 5.3 宠物模块

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | `/pets` | 获取宠物列表 | 是 |
| POST | `/pets` | 添加宠物 | 是 |
| GET | `/pets/{pet_id}` | 获取宠物详情 | 是 |
| PUT | `/pets/{pet_id}` | 更新宠物信息 | 是 |
| DELETE | `/pets/{pet_id}` | 删除宠物（软删除） | 是 |
| PUT | `/pets/{pet_id}/fence` | 设置围栏 | 是 |
| GET | `/pets/{pet_id}/fence` | 获取围栏设置 | 是 |

**围栏设置请求示例**：
```json
PUT /api/v1/pets/67890/fence
{
  "fence_enabled": true,
  "fence_center_lat": 31.2304,
  "fence_center_lng": 121.4737,
  "fence_radius": 100
}
```

---

### 5.4 设备模块

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | `/devices/register` | 设备注册（获取 JWT） | 否（需 SN + 激活码） |
| POST | `/devices/bind` | 绑定设备到宠物 | 是 |
| POST | `/devices/unbind` | 解绑设备 | 是 |
| GET | `/devices/{device_id}` | 获取设备详情 | 是 |
| PUT | `/devices/{device_id}/config` | 下发配置到设备 | 是 |
| POST | `/devices/{device_id}/find` | 寻找设备（响铃） | 是 |
| GET | `/devices/{device_id}/status` | 获取设备状态 | 是 |
| POST | `/devices/{device_id}/ota` | 触发固件升级 | 是（后台） |
| GET | `/devices/{device_id}/ota/progress` | 查询升级进度 | 是 |

**设备注册请求示例**：
```json
POST /api/v1/devices/register
{
  "sn": "PAW20260721001",
  "activation_code": "ACT-XXXX-XXXX",
  "hw_type": "dog",
  "fw_version": "1.0.0"
}
→ 返回：{ "token": "jwt...", "mqtt_url": "ssl://mqtt.pawtrack.app:8883" }
```

---

### 5.5 定位模块

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | `/location/realtime/{pet_id}` | 获取实时位置 | 是 |
| GET | `/location/history/{pet_id}` | 获取历史轨迹 | 是（会员） |
| GET | `/location/nearby` | 获取附近宠物 | 是 |
| POST | `/location/upload` | 设备上报定位（内部接口） | 设备 Token |

**历史轨迹请求示例**：
```
GET /api/v1/location/history/67890?start=1721532000&end=1721535600&interval=60
→ start/end: Unix时间戳
→ interval: 轨迹点采样间隔（秒），默认60
```

---

### 5.6 报警模块

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | `/alarms` | 报警列表 | 是 |
| GET | `/alarms/{alarm_id}` | 报警详情 | 是 |
| PUT | `/alarms/{alarm_id}/handle` | 处理报警 | 是 |
| PUT | `/alarms/{alarm_id}/false-positive` | 标记误报 | 是 |
| PUT | `/alarms/settings` | 更新报警设置 | 是 |

---

### 5.7 社交模块

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | `/social/nearby-dogs` | 附近狗狗列表 | 是 |
| POST | `/social/meet` | 发起碰头 | 是 |
| PUT | `/social/meet/{meet_id}/confirm` | 确认碰头 | 是 |
| PUT | `/social/meet/{meet_id}/complete` | 完成碰头 | 是 |
| PUT | `/social/meet/{meet_id}/cancel` | 取消碰头 | 是 |
| GET | `/social/meet/history` | 碰头历史 | 是 |

---

### 5.8 订单/订阅模块

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | `/orders` | 创建订单 | 是 |
| GET | `/orders/{order_no}` | 订单详情 | 是 |
| POST | `/orders/{order_no}/pay` | 发起支付 | 是 |
| GET | `/orders/callback` | 支付回调（微信/支付宝） | 否 |
| GET | `/subscriptions/current` | 当前订阅信息 | 是 |
| POST | `/subscriptions/renew` | 续费 | 是 |
| DELETE | `/subscriptions/cancel` | 取消自动续费 | 是 |

---

### 5.9 积分模块

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | `/points/balance` | 积分余额 | 是 |
| GET | `/points/history` | 积分明细 | 是 |
| POST | `/points/signin` | 每日签到 | 是 |

---

### 5.10 后台管理接口（前缀 `/admin/v1`）

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | `/admin/v1/dashboard` | 数据概览 | 后台 Token |
| GET | `/admin/v1/users` | 用户列表 | 后台 Token |
| PUT | `/admin/v1/users/{id}/ban` | 封禁用户 | 后台 Token |
| GET | `/admin/v1/devices` | 设备列表 | 后台 Token |
| GET | `/admin/v1/alarms` | 报警记录 | 后台 Token |
| PUT | `/admin/v1/alarms/rules` | 报警规则配置 | 后台 Token |
| GET | `/admin/v1/orders` | 订单列表 | 后台 Token |
| PUT | `/admin/v1/orders/{no}/refund` | 退款审批 | 后台 Token |

---

## 6. WebSocket 实时推送协议

### 6.1 连接与认证

```
连接地址：wss://api.pawtrack.app/ws/v1?token=<access_token>

连接成功后，服务端发送：
{ "type": "connected", "server_time": 1721532000 }

Token 无效时，服务端发送：
{ "type": "error", "code": 10003, "message": "token invalid" }
→ 立即关闭连接（code: 4001）
```

### 6.2 消息类型

#### 6.2.1 服务端 → 客户端（推送）

| type | 说明 | 数据 |
|------|------|------|
| `location_update` | 宠物位置更新 | `{ pet_id, lat, lng, ts, source }` |
| `alarm_triggered` | 报警触发 | `{ alarm_id, pet_id, type, lat, lng, ts }` |
| `device_status` | 设备状态变更 | `{ device_id, status, battery }` |
| `meet_request` | 碰头请求 | `{ meet_id, initiator_name, distance }` |
| `meet_update` | 碰头状态更新 | `{ meet_id, status, distance }` |
| `subscription_expiring` | 会员即将到期 | `{ expire_at, days_left }` |

#### 6.2.2 客户端 → 服务端（订阅控制）

```json
// 订阅某宠物的实时位置
{ "type": "subscribe", "pet_ids": [67890, 67891] }

// 取消订阅
{ "type": "unsubscribe", "pet_ids": [67890] }

// 心跳（每30秒）
{ "type": "ping" }
→ 服务端回复：{ "type": "pong", "server_time": 1721532000 }
```

### 6.3 推送示例

```json
// 位置更新推送
{
  "type": "location_update",
  "pet_id": 67890,
  "data": {
    "lat": 31.2304,
    "lng": 121.4737,
    "accuracy": 5.0,
    "source": "gps",
    "battery": 85,
    "ts": 1721532000
  }
}

// 报警推送
{
  "type": "alarm_triggered",
  "pet_id": 67890,
  "data": {
    "alarm_id": 1001,
    "type": "leave_fence",
    "severity": "high",
    "lat": 31.2350,
    "lng": 121.4800,
    "address": "上海市浦东新区张江高科技园区XXX路",
    "ts": 1721532000
  }
}
```

---

## 7. 限流策略

### 7.1 限流规则

| 维度 | 接口 | 限制 | 超限响应 |
|------|------|------|---------|
| 全局 IP | 所有接口 | 100 req/min | 429 Too Many Requests |
| 用户 | `POST /auth/login` | 5 req/min | 429 |
| 用户 | `POST /location/upload` | 30 req/min | 429 |
| 用户 | `GET /api/v1/*` | 300 req/min | 429 |
| 设备 | `POST /location/upload` | 1 req/5s | 429 |
| 设备 | `POST /devices/status` | 1 req/30s | 429 |

### 7.2 限流响应格式

```json
{
  "code": 90001,
  "message": "请求频率超限，请稍后再试",
  "meta": {
    "retry_after": 30,      // 多少秒后可以重试
    "limit": 30,
    "remaining": 0,
    "reset": 1721532060     // 重置时间（Unix时间戳）
  }
}
```

HTTP Header 中同时返回：
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1721532060
Retry-After: 30
```

---

## 8. 接口详细示例

### 8.1 注册登录

#### 手机号注册

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "phone": "13812345678",
  "code": "123456",           // 短信验证码
  "nickname": "张工",
  "invite_code": "PAW001"     // 可选
}

→ 200 OK
{
  "code": 0,
  "data": {
    "user_id": 12345,
    "phone": "138****5678",
    "nickname": "张工",
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "Bearer",
    "expires_in": 7200
  }
}
```

#### 微信登录

```http
POST /api/v1/auth/wechat-login
{
  "code": "wx_auth_code",     // 微信授权码
  "nickname": "张工",
  "avatar": "https://..."
}
```

### 8.2 设备绑定

```http
POST /api/v1/devices/bind
Authorization: Bearer <access_token>
{
  "sn": "PAW20260721001",
  "pet_id": 67890
}

→ 200 OK
{
  "code": 0,
  "data": {
    "device_id": 1,
    "sn": "PAW20260721001",
    "pet_id": 67890,
    "status": "online",
    "battery": 100,
    "bound_at": 1721532000
  }
}
```

### 8.3 创建订单

```http
POST /api/v1/orders
Authorization: Bearer <access_token>
{
  "type": "subscription",
  "plan": "pro",
  "duration": "year",          // month / year
  "pay_channel": "wechat"      // wechat / alipay / apple
}

→ 200 OK
{
  "code": 0,
  "data": {
    "order_no": "ORD20260721001",
    "amount": 299.00,
    "pay_channel": "wechat",
    "pay_params": { ... }     // 支付参数（微信/支付宝 SDK 用）
  }
}
```

---

## 9. Webhook 回调规范

### 9.1 支付回调

```
POST /api/v1/orders/callback/wechat
Content-Type: application/json
X-Signature: sha256=<signature>    // 微信支付签名验证

{
  "order_no": "ORD20260721001",
  "transaction_id": "wx1234567890",
  "amount": 299.00,
  "status": "SUCCESS",              // SUCCESS / FAIL
  "paid_at": 1721532100
}
```

**处理流程**：
1. 验证签名（防止伪造）
2. 查询订单状态（防止重复处理）
3. 更新订单状态
4. 发送 `order.paid` 消息到 RabbitMQ
5. 订阅服务消费消息 → 创建 subscriptions 记录
6. 返回 `{"code": "SUCCESS"}` 给支付平台

---

*本文档与硬件通信协议文档、技术架构方案、数据库设计文档配合使用。*
