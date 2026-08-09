# 📋 02_技术文档 — 目录索引

> 本目录存放宠迹项目的技术设计文档。各文件主题独立，呈"总纲 → 专题"分层结构。
> **2026-08-09 已全面更新**：对齐 PRD V2.1 完整版与代码实现（PostGIS→Haversine、React Native→uni-app、新增 event_outbox 表）。

## 文档矩阵（含实现状态）

| 文件 | 定位 | 实现状态 |
|------|------|---------|
| `宠迹_技术架构选型方案.md` | **总纲**：技术栈选型 / 三层架构 / 数据流 / Sprint 交付物 | ✅ V2.0 已同步 |
| `宠迹_数据库设计文档.md` | 专题：10 张表（含 event_outbox）+ Redis 结构 | ✅ 已落地 |
| `宠迹_API接口设计文档.md` | 专题：RESTful 规范 / JWT 双 Token / 74 端点清单 | ✅ 已落地 |
| `宠迹_硬件通信协议文档.md` | 专题：MQTT Topic / QoS / 设备鉴权 / BLE 协议 | ⚠️ 设计稿 |
| `宠迹_定位数据缓冲层方案.md` | 专题：Redis Stream 缓冲 → GEO + Pub/Sub | ✅ 已落地 |
| `宠迹_围栏检测服务端实现.md` | 专题：Haversine 围栏检测（猫狗差异化） | ✅ 已落地 |
| `宠迹_支付订阅最终一致性方案.md` | 专题：Outbox Pattern + event_outbox 表 | ✅ 已落地 |
| `宠迹_RabbitMQ队列设计.md` | 专题：4 队列拓扑 + 死信（V2 演进） | ⚠️ 设计稿 |
| `硬件文档/` | 硬件选型：猫（BLE+WiFi）/ 狗（GPS+4G） | ⚠️ 选型完成 |

## 实现状态图例

- ✅ 已落地 = 代码已实现且与文档一致（05_后端项目/backend）
- ⚠️ 设计稿 = 文档完成，MVP 阶段未接入（硬件原型 / RabbitMQ 由 Redis 替代）

## 2026-08-09 更新摘要

1. **前端技术栈**：React Native → uni-app (Vue3) 微信小程序（`04_前端项目/miniapp`）
2. **围栏检测**：PostGIS ST_DWithin → 纯 Python Haversine（DECIMAL 存储，无空间库依赖）
3. **数据库**：补 `event_outbox` 表（Outbox Pattern 已落地）；坐标字段改为 DECIMAL(10,7)
4. **架构总览**：微服务 → FastAPI 单体模块化（MVP）；RabbitMQ/ES/MongoDB 标注 V2 演进
5. **API 文档**：补充 wechat-login，逐端点标注实现状态

## 阅读顺序

```
总纲 → 技术架构选型方案
专题 → 数据库 → API → 围栏 → 缓冲层 → 支付 → 队列 → 硬件
评审 → 按"实现状态"区分已落地与规划项
```

---
*更新：2026-08-09 | 与 PRD V2.1 / UI原型 V2.1 / 代码实现三方对齐*
