# 宠迹 PawTrack — 项目记忆库

> 本目录为技能体系记忆库（`.skills-memory/`），WorkBuddy 系统日志仍写入 `.workbuddy/memory/`，两处互为同步副本。
> 结构：`MEMORY.md`（热记忆）+ `YYYY-MM-DD.md`（每日日志）+ `archive/`（冷归档）。

## 项目状态

- **产品**：宠迹智能宠物定位与社交平台（猫狗分区：猫=BLE+WiFi，狗=GPS+4G）
- **版本**：v0.4.0（Sprint 3 完成）
- **技术栈**：FastAPI + PostgreSQL16(PostGIS 移除→DECIMAL+Haversine) + Redis + uni-app 小程序
- **目录结构**（2026-08-09 确认）：01_产品文档 / 02_技术文档 / 03_设计文档 / 04_前端项目{frontend,admin,miniapp} / 05_后端项目{backend,docker,Makefile,compose*}

## 关键决策记录

- 坐标存储：PostGIS GEOGRAPHY → 因本地无 Docker 改用 DECIMAL(10,7) 双字段 + Haversine 围栏
- 前端重构：React Web → uni-app (Vue3+Vite) 微信小程序，位于 04_前端项目/miniapp/
- 认证：RS256 JWT 双 Token（access 2h + refresh 30d）+ admin 独立 scope
- 实时链路：设备→MQTT→Redis Stream→MongoDB + Redis GEO→Pub/Sub→WebSocket
- 支付一致性：Outbox Pattern + RabbitMQ 最终一致性
- 开发环境：Homebrew PostgreSQL16 + Redis（无 Docker），JWT 密钥在根目录 keys/

## 环境约定

- npm 必须用 npmmirror 镜像（官方源超时）：`--registry=https://registry.npmmirror.com`
- 后端启动：`05_后端项目/backend` 下 uvicorn（venv: /Users/macos/.workbuddy/binaries/python/envs/pawtrack）
- 后端 .env 已配置本地 JWT 密钥路径与 DB 连接（勿提交，已在 .gitignore）
- 微信小程序：`04_前端项目/miniapp`，`npm run dev:mp-weixin` 编译，H5 预览 localhost:5173

## 用户偏好（重要）

- **不要生成 README 目录索引**：01/02 文档目录的 README 索引已删除（2026-08-09 用户明确要求），后续整理文档不再创建索引类 README（miniapp/README.md 属项目说明保留）
- 文档统一 Markdown 纯文本格式（docx 已全量转换），树形结构用缩进列表，不依赖 Mermaid
- 外部工具（Cursor）会频繁改动工作区文件，git add -A 前先 git status 检查，丢失文件用 git checkout 恢复
