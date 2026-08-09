# 🐾 宠迹 PawTrack — 微信小程序端

基于 **uni-app (Vue 3 + Vite)** 的微信小程序客户端，对应后端 FastAPI（`../05_后端项目/backend`）。

## 技术栈

- **uni-app 3.x**（Vue 3 组合式 API）
- 编译目标：微信小程序（`mp-weixin`），同时支持 H5 调试
- 网络：`uni.request` 封装（JWT 自动刷新）+ `uni.connectSocket` 封装（自动重连 + 心跳）

## 目录结构

```
miniapp/
├── src/
│   ├── pages/
│   │   ├── login/login.vue        # 登录注册（手机号验证码 + 微信一键登录）
│   │   ├── home/home.vue          # 地图首页（实时定位 + WebSocket 推送）
│   │   ├── pet-add/pet-add.vue    # 添加宠物（猫/狗 + 围栏设置）
│   │   ├── device-bind/device-bind.vue  # 绑定设备（SN + 激活码）
│   │   ├── alarms/alarms.vue      # 报警记录（筛选 + 处理/误报）
│   │   ├── social/social.vue      # 宠物社交（附近宠物 + 碰头）
│   │   ├── member/member.vue      # 会员中心（套餐 + 模拟支付）
│   │   └── points/points.vue      # 积分中心（签到 + 明细 + 商城）
│   ├── utils/
│   │   ├── config.ts              # API/WS 地址配置
│   │   ├── request.ts             # 请求封装（JWT 刷新）
│   │   ├── ws.ts                  # WebSocket 封装（重连/心跳/订阅）
│   │   └── auth.ts                # Token 存取
│   ├── static/                    # tabBar 图标 + 地图 marker
│   ├── App.vue                    # 全局样式
│   ├── pages.json                 # 页面路由 + tabBar
│   ├── manifest.json              # 小程序配置（appid/权限）
│   └── main.ts
└── scripts/gen_icons.py           # 图标生成脚本（PIL）
```

## 快速开始

```bash
# 1. 安装依赖
npm install --registry=https://registry.npmmirror.com

# 2. 编译微信小程序（产物输出到 dist/dev/mp-weixin）
npm run dev:mp-weixin

# 3. 用微信开发者工具导入 dist/dev/mp-weixin 目录
```

> 开发调试需：
> 1. 先启动后端（`05_后端项目`，端口 8000）
> 2. 微信开发者工具 → 详情 → 本地设置 → 勾选「不校验合法域名」
> 3. `src/utils/config.ts` 中配置后端地址（默认 `http://localhost:8000`）

## 页面路由

| 页面 | 路由 | 说明 |
|------|------|------|
| 登录注册 | /pages/login/login | 手机号+验证码（MVP 任意码）或微信一键登录 |
| 地图首页 | /pages/home/home（tabBar） | 宠物实时位置、围栏、模拟定位上报 |
| 添加宠物 | /pages/pet-add/pet-add | 猫狗类型差异化围栏 |
| 绑定设备 | /pages/device-bind/device-bind | SN+激活码注册，可选绑定宠物 |
| 报警记录 | /pages/alarms/alarms（tabBar） | 筛选 + 确认/误报 |
| 宠物社交 | /pages/social/social（tabBar） | 附近宠物 + 碰头 |
| 会员中心 | /pages/member/member | 套餐模拟支付 |
| 积分中心 | /pages/points/points（tabBar） | 签到 + 明细 + 商城 |

## 构建生产

```bash
npm run build:mp-weixin   # 产物 dist/build/mp-weixin
```

上线前在 `manifest.json` 填入正式 appid，`src/utils/config.ts` 切换到 HTTPS 正式域名。
