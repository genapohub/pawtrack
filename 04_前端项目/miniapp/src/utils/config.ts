/**
 * 宠迹 PawTrack — 环境配置（小程序）
 *
 * 开发环境默认走本地 Mock（不接真实微信登录/支付/短信/地图/硬件）。
 * 对接本地 FastAPI 时把 USE_MOCK 改为 false，并确认后端地址。
 * Mock 不等于验收通过。
 */
export const IS_DEV: boolean = true // 上线前改为 false

/** 本地预览默认走 Mock；对接本地后端时改为 false */
export const USE_MOCK: boolean = true

/** 后端 REST API 地址（微信开发者工具需勾选「不校验合法域名」） */
export const API_BASE: string = 'http://localhost:8000/api/v1'

/** WebSocket 地址（与后端 /ws/v1 对应；Mock 模式下不会连接） */
export const WS_BASE: string = 'ws://localhost:8000/ws/v1'

/** 高德地图 Web 服务 key（围栏/逆地理，可选；本轮保持空，不接真实地图） */
export const AMAP_KEY: string = ''
