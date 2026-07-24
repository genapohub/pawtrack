# 宠迹 PawTrack — RabbitMQ 队列设计

> 版本：V1.0 | 日期：2026-07-21  
> 状态：待评审

---

## 1. 队列总览

| 队列名 | 用途 | 消费者 | 持久化 | 死信队列 |
|--------|------|--------|--------|---------|
| `location.upload` | 定位数据缓冲写入 | 3个消费者（MongoDB/归档/围栏） | ✅ | ❌ |
| `alarm.notify` | 报警通知推送 | 2个消费者（WebSocket/Push） | ✅ | `alarm.notify.dlx` |
| `meet.timeout` | 碰头超时检测 | 1个消费者 | ✅ | ❌ |
| `order.paid` | 支付成功 → 订阅创建 | 1个消费者 | ✅ | `order.paid.dlx` |
| `order.refunded` | 退款 → 订阅取消 | 1个消费者 | ✅ | ❌ |
| `device.ota.progress` | OTA升级进度 | 1个消费者（后台） | ✅ | ❌ |

---

## 2. 队列详细设计

### 2.1 `location.upload` — 定位数据缓冲

```yaml
queue: location.upload
durable: true
max_priority: 5
message_ttl: 60000   # 消息最大存活 60 秒（超出丢弃）

binding:
  exchange: pawtrack.direct
  routing_key: location.upload

message_format:
  {
    "device_id": 1001,
    "pet_id": 67890,
    "lat": 31.2304,
    "lng": 121.4737,
    "ts": 1721532000
  }

consumer:
  count: 3
  strategy: round-robin
  prefetch: 100   # 每次预取 100 条，批量处理
  retry:
    max_attempts: 3
    backoff: [1s, 5s, 30s]
```

### 2.2 `alarm.notify` — 报警通知

```yaml
queue: alarm.notify
durable: true

message_format:
  {
    "alarm_id": 1001,
    "user_id": 12345,
    "pet_id": 67890,
    "type": "leave_fence",
    "severity": "high",
    "lat": 31.2304,
    "lng": 121.4737,
    "ts": 1721532000
  }

consumer:
  count: 2
  prefetch: 10
  retry:
    max_attempts: 5
    dead_letter_queue: alarm.notify.dlx

dead_letter_queue: alarm.notify.dlx
  # 死信原因：推送失败（用户卸载App、Token失效等）
  # 处理：记录日志，人工排查
```

### 2.3 `meet.timeout` — 碰头超时

```yaml
queue: meet.timeout
durable: true

message_format:
  {
    "meet_id": 5001,
    "initiator_pet_id": 67890,
    "receiver_pet_id": 67891,
    "started_at": 1721532000,
    "timeout_at": 1721532300  # 5分钟后超时
  }

consumer:
  # 使用 RabbitMQ 延迟队列（TTL + Dead Letter）
  # 消息发送时设置 TTL = timeout_at - now()
  # 超时后自动进入队列，消费者处理超时逻辑

delayed_exchange: pawtrack.delayed  # 自定义延迟交换机
```

### 2.4 `order.paid` — 支付成功

```yaml
queue: order.paid
durable: true

message_format:
  {
    "order_no": "ORD20260721001",
    "user_id": 12345,
    "plan": "pro_year",
    "amount": 299.00,
    "paid_at": 1721532100,
    "compensate": false   # 是否补偿消息
  }

consumer:
  count: 1
  idempotent: true   # 消费者内部做幂等检查
  retry:
    max_attempts: 3
    dead_letter_queue: order.paid.dlx
```

---

## 3. Exchange 设计

```yaml
exchanges:
  - name: pawtrack.direct
    type: direct
    durable: true
    bindings:
      - queue: location.upload
        routing_key: location.upload
      - queue: alarm.notify
        routing_key: alarm.notify
      - queue: meet.timeout
        routing_key: meet.timeout
      - queue: order.paid
        routing_key: order.paid
      - queue: order.refunded
        routing_key: order.refunded

  - name: pawtrack.delayed
    type: x-delayed-message   # 需要安装 rabbitmq-delayed-message-exchange 插件
    arguments:
      x-delayed-type: direct
    durable: true
```

---

## 4. 消费者代码示例（Python）

```python
import aio_pika
import json

async def consume_location_upload():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=100)
    queue = await channel.declare_queue('location.upload', durable=True)
    
    async for message in queue:
        async with message.process():  # 自动 ack
            data = json.loads(message.body)
            await process_location(data)

async def consume_order_paid():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue('order.paid', durable=True)
    
    async for message in queue:
        try:
            data = json.loads(message.body)
            await create_subscription(data)
            message.ack()  # 成功，确认消息
        except Exception as e:
            logger.error(f"处理失败: {e}")
            message.nack(requeue=False)  # 不重新排队，进入死信队列
```

---

*本文档需与技术架构方案、API接口设计文档配合使用。*
