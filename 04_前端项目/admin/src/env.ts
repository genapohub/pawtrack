/**
 * 宠迹 PawTrack admin — 环境标识工具
 */
export const APP_ENV: 'dev' | 'prod' = import.meta.env.VITE_APP_ENV ?? 'dev'
export const IS_DEV = APP_ENV === 'dev'
export const IS_PROD = APP_ENV === 'prod'
export const API_BASE = import.meta.env.VITE_API_BASE ?? '/api/v1'
/** 开发默认走本地数据层；对接本地后端时设 VITE_USE_MOCK=false。 */
export const USE_MOCK = (import.meta.env.VITE_USE_MOCK ?? 'true') !== 'false'
