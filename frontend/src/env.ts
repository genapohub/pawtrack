/**
 * 宠迹 PawTrack — 环境标识工具
 * 通过 vite 构建模式自动区分 dev/prod
 */
export const APP_ENV: 'dev' | 'prod' = import.meta.env.VITE_APP_ENV ?? 'dev'
export const IS_DEV = APP_ENV === 'dev'
export const IS_PROD = APP_ENV === 'prod'
export const API_BASE = import.meta.env.VITE_API_BASE ?? '/api/v1'
