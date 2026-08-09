/**
 * 宠迹 PawTrack — 环境配置（小程序）
 *
 * 开发环境：连接本地 FastAPI 后端
 * 生产环境：通过 manifest.json 或环境变量注入正式域名
 */
export const IS_DEV: boolean = true // 上线前改为 false

/** 后端 REST API 地址（微信开发者工具需勾选「不校验合法域名」） */
export const API_BASE: string = 'http://localhost:8000/api/v1'

/** WebSocket 地址（与后端 /ws/v1 对应） */
export const WS_BASE: string = 'ws://localhost:8000/ws/v1'

/** 高德地图 Web 服务 key（围栏/逆地理，可选） */
export const AMAP_KEY: string = ''
