/**
 * 宠迹 PawTrack — 请求封装（uni.request + JWT 自动刷新）
 */
import { API_BASE } from './config'
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from './auth'

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  auth?: boolean // 是否需要 token，默认 true
  retry?: boolean // 是否允许 401 后刷新重试
}

/** 后端返回统一结构：{ code, message, data } */
interface ApiResponse {
  code: number
  message?: string
  data?: any
}

/** 刷新 access_token（失败则登出） */
function refreshToken(): Promise<string> {
  const refresh = getRefreshToken()
  if (!refresh) return Promise.reject(new Error('no refresh token'))

  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE}/auth/refresh`,
      method: 'POST',
      data: { refresh_token: refresh },
      success: (res: any) => {
        const body = res.data as ApiResponse
        if (body.code === 0 && body.data?.access_token) {
          setTokens(body.data.access_token, body.data.refresh_token)
          resolve(body.data.access_token)
        } else {
          clearTokens()
          reject(new Error(body.message || '刷新失败'))
        }
      },
      fail: (err) => reject(err),
    })
  })
}

/** 通用请求 */
export function request<T = any>(options: RequestOptions): Promise<T> {
  const {
    url, method = 'GET', data, auth = true, retry = true,
  } = options

  return new Promise<T>((resolve, reject) => {
    const token = auth ? getAccessToken() : ''
    const header: Record<string, string> = { 'Content-Type': 'application/json' }
    if (token) header.Authorization = `Bearer ${token}`

    uni.request({
      url: url.startsWith('http') ? url : `${API_BASE}${url}`,
      method,
      data,
      header,
      success: async (res: any) => {
        const body = res.data as ApiResponse
        // 401 → 刷新 token 后重试一次
        if (res.statusCode === 401 && auth && retry) {
          try {
            await refreshToken()
            const r = await request<T>({ ...options, retry: false })
            resolve(r)
          } catch (e) {
            clearTokens()
            uni.reLaunch({ url: '/pages/login/login' })
            reject(e)
          }
          return
        }
        if (res.statusCode >= 200 && res.statusCode < 300 && body.code === 0) {
          resolve(body.data as T)
        } else {
          const msg = body?.message || `请求失败(${res.statusCode})`
          uni.showToast({ title: msg, icon: 'none' })
          reject(new Error(msg))
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络连接失败', icon: 'none' })
        reject(err)
      },
    })
  })
}

/** 快捷方法 */
export const http = {
  get: <T = any>(url: string, auth = true) => request<T>({ url, method: 'GET', auth }),
  post: <T = any>(url: string, data?: any, auth = true) =>
    request<T>({ url, method: 'POST', data, auth }),
  put: <T = any>(url: string, data?: any, auth = true) =>
    request<T>({ url, method: 'PUT', data, auth }),
  del: <T = any>(url: string, auth = true) => request<T>({ url, method: 'DELETE', auth }),
}
