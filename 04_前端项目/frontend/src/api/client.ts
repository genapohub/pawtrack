/**
 * 宠迹 PawTrack — API 客户端
 * 封装所有后端 REST API 调用，自动管理 JWT Token
 */

import { API_BASE as BASE_URL } from '../env'

// ── Token 存储 ─────────────────────────────────

const TOKEN_KEY = 'pawtrack_access_token'
const REFRESH_KEY = 'pawtrack_refresh_token'
const USER_KEY = 'pawtrack_user'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_KEY)
}

export function saveAuth(data: {
  access_token: string
  refresh_token: string
  user_id?: number
  phone?: string
  nickname?: string
  member_level?: string
}) {
  localStorage.setItem(TOKEN_KEY, data.access_token)
  localStorage.setItem(REFRESH_KEY, data.refresh_token)
  localStorage.setItem(USER_KEY, JSON.stringify({
    user_id: data.user_id,
    phone: data.phone,
    nickname: data.nickname,
    member_level: data.member_level
  }))
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_KEY)
  localStorage.removeItem(USER_KEY)
}

export function getUser(): any | null {
  const raw = localStorage.getItem(USER_KEY)
  return raw ? JSON.parse(raw) : null
}

export function isLoggedIn(): boolean {
  return !!getToken()
}

// ── 请求封装 ─────────────────────────────────

async function request<T = any>(
  method: string,
  path: string,
  body?: any,
  retry = true
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  }
  const token = getToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const resp = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined
  })

  // Token 过期，尝试刷新
  if (resp.status === 401 && retry && getRefreshToken()) {
    const refreshed = await tryRefreshToken()
    if (refreshed) {
      return request<T>(method, path, body, false)
    }
    clearAuth()
    throw new Error('登录已过期，请重新登录')
  }

  const data = await resp.json()

  if (!resp.ok) {
    const errMsg = data.detail?.message || data.detail || '请求失败'
    throw new Error(typeof errMsg === 'string' ? errMsg : JSON.stringify(errMsg))
  }

  return data
}

async function tryRefreshToken(): Promise<boolean> {
  try {
    const resp = await fetch(`${BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: getRefreshToken() })
    })
    if (!resp.ok) return false
    const data = await resp.json()
    if (data.code === 0 && data.data?.access_token) {
      localStorage.setItem(TOKEN_KEY, data.data.access_token)
      localStorage.setItem(REFRESH_KEY, data.data.refresh_token)
      return true
    }
    return false
  } catch {
    return false
  }
}

// ── 导出 API 方法 ─────────────────────────────────

export const api = {
  get: <T = any>(path: string) => request<T>('GET', path),
  post: <T = any>(path: string, body?: any) => request<T>('POST', path, body),
  put: <T = any>(path: string, body?: any) => request<T>('PUT', path, body),
  delete: <T = any>(path: string) => request<T>('DELETE', path),

  // ── 认证 ─────────────────────────────────
  auth: {
    register: (phone: string, code: string, nickname?: string) =>
      api.post('/auth/register', { phone, code, nickname }),

    login: (phone: string, code: string) =>
      api.post('/auth/login', { phone, code }),

    wechatLogin: (code: string, nickname?: string, avatar?: string) =>
      api.post('/auth/wechat-login', { code, nickname, avatar }),

    logout: () => api.delete('/auth/logout')
  },

  // ── 宠物 ─────────────────────────────────
  pets: {
    list: () => api.get('/pets'),
    create: (data: {
      name: string
      pet_type: 'cat' | 'dog'
      breed?: string
      gender?: 'male' | 'female' | 'unknown'
      birthday?: string
      weight?: number
      fence_enabled?: boolean
      fence_radius?: number
    }) => api.post('/pets', data),
    get: (id: number) => api.get(`/pets/${id}`),
    update: (id: number, data: any) => api.put(`/pets/${id}`, data),
    delete: (id: number) => api.delete(`/pets/${id}`),
    setFence: (id: number, data: {
      fence_enabled: boolean
      fence_center_lat?: number
      fence_center_lng?: number
      fence_radius?: number
    }) => api.put(`/pets/${id}/fence`, data),
    getFence: (id: number) => api.get(`/pets/${id}/fence`)
  },

  // ── 用户 ─────────────────────────────────
  users: {
    me: () => api.get('/users/me'),
    updateMe: (data: { nickname?: string; avatar?: string; privacy_location?: string }) =>
      api.put('/users/me', data),
    changePassword: (old_password: string, new_password: string) =>
      api.put('/users/me/password', { old_password, new_password }),
    myDevices: () => api.get('/users/me/devices'),
    deleteMe: () => api.delete('/users/me')
  },

  // ── 设备 ─────────────────────────────────
  devices: {
    register: (sn: string, activation_code: string, hw_type: 'cat' | 'dog', fw_version?: string) =>
      api.post('/devices/register', { sn, activation_code, hw_type, fw_version }),
    bind: (sn: string, pet_id: number) =>
      api.post('/devices/bind', { sn, pet_id }),
    unbind: (sn: string) => api.post('/devices/unbind', { sn }),
    get: (id: number) => api.get(`/devices/${id}`),
    list: () => api.get('/devices'),
    setConfig: (id: number, data: { report_interval?: number; fence_enabled?: boolean; low_battery_threshold?: number }) =>
      api.put(`/devices/${id}/config`, data),
    find: (id: number) => api.post(`/devices/${id}/find`),
    status: (id: number) => api.get(`/devices/${id}/status`),
    triggerOTA: (id: number, target_version: string) =>
      api.post(`/devices/${id}/ota`, { target_version }),
    otaProgress: (id: number) => api.get(`/devices/${id}/ota/progress`)
  },

  // ── 定位 ─────────────────────────────────
  location: {
    realtime: (petId: number) => api.get(`/location/realtime/${petId}`),
    history: (petId: number, start?: number, end?: number) =>
      api.get(`/location/history/${petId}?${start ? `start=${start}&` : ''}${end ? `end=${end}` : ''}`),
    upload: (data: {
      device_id: number
      lat: number
      lng: number
      accuracy?: number
      battery?: number
      source?: string
      ts: number
    }) => api.post('/location/upload', data)
  },

  // ── 报警 ─────────────────────────────────
  alarms: {
    list: (params?: { pet_id?: number; status?: string; page?: number; size?: number }) => {
      const qs = new URLSearchParams()
      if (params?.pet_id) qs.set('pet_id', String(params.pet_id))
      if (params?.status) qs.set('status', params.status)
      if (params?.page) qs.set('page', String(params.page))
      if (params?.size) qs.set('size', String(params.size))
      const q = qs.toString()
      return api.get(`/alarms${q ? `?${q}` : ''}`)
    },
    get: (id: number) => api.get(`/alarms/${id}`),
    handle: (id: number, status: 'handled' | 'false_positive', note?: string) =>
      api.put(`/alarms/${id}/handle`, { status, note }),
    unreadCount: () => api.get('/alarms/unread/count'),
    getSettings: () => api.get('/alarms/settings'),
    updateSettings: (data: {
      leave_fence_notify?: boolean
      enter_fence_notify?: boolean
      low_battery_threshold?: number
      quiet_hours_start?: string
      quiet_hours_end?: string
    }) => api.put('/alarms/settings', data)
  },

  // ── 社交碰头 ─────────────────────────────────
  social: {
    nearby: (lat: number, lng: number, radius?: number) =>
      api.get(`/social/nearby?lat=${lat}&lng=${lng}${radius ? `&radius=${radius}` : ''}`),
    createMeet: (receiver_pet_id: number, start_lat: number, start_lng: number) =>
      api.post('/social/meets', { receiver_pet_id, start_lat, start_lng }),
    confirmMeet: (meet_id: number, end_lat?: number, end_lng?: number) =>
      api.put(`/social/meets/${meet_id}/confirm`, { end_lat, end_lng }),
    completeMeet: (meet_id: number) => api.put(`/social/meets/${meet_id}/complete`),
    cancelMeet: (meet_id: number) => api.put(`/social/meets/${meet_id}/cancel`),
    listMeets: (status?: string, page?: number, size?: number) => {
      const qs = new URLSearchParams()
      if (status) qs.set('status', status)
      if (page) qs.set('page', String(page))
      if (size) qs.set('size', String(size))
      const q = qs.toString()
      return api.get(`/social/meets${q ? `?${q}` : ''}`)
    }
  },

  // ── 订单与订阅 ─────────────────────────────────
  orders: {
    plans: () => api.get('/orders/plans'),
    create: (plan: string, pay_channel: 'wechat' | 'alipay' | 'apple' = 'wechat') =>
      api.post('/orders', { plan, pay_channel }),
    detail: (order_no: string) => api.get(`/orders/${order_no}`),
    pay: (order_no: string, pay_channel: 'wechat' | 'alipay' | 'apple' = 'wechat') =>
      api.post(`/orders/${order_no}/pay`, { pay_channel }),
    payCallback: (order_no: string, transaction_id: string) =>
      api.post('/orders/pay-callback', { order_no, transaction_id }),
    subscription: () => api.get('/orders/subscription'),
    renew: (pay_channel: 'wechat' | 'alipay' | 'apple' = 'wechat') =>
      api.post('/orders/subscription/renew', { pay_channel }),
    cancelSubscription: (auto_renew = false) =>
      api.put('/orders/subscription/cancel', { auto_renew }),
    history: (page?: number, size?: number) => {
      const qs = new URLSearchParams()
      if (page) qs.set('page', String(page))
      if (size) qs.set('size', String(size))
      const q = qs.toString()
      return api.get(`/orders/history${q ? `?${q}` : ''}`)
    }
  },

  // ── 积分 ─────────────────────────────────
  points: {
    balance: () => api.get('/points/balance'),
    logs: (page?: number, size?: number) => {
      const qs = new URLSearchParams()
      if (page) qs.set('page', String(page))
      if (size) qs.set('size', String(size))
      const q = qs.toString()
      return api.get(`/points/logs${q ? `?${q}` : ''}`)
    },
    signin: () => api.post('/points/signin'),
    shop: () => api.get('/points/shop')
  }
}
