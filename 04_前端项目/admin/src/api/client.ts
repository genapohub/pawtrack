/**
 * 宠迹 PawTrack 管理后台 — API 客户端
 */

import { API_BASE as BASE_URL } from '../env'

const TOKEN_KEY = 'pawtrack_admin_token'
const ADMIN_KEY = 'pawtrack_admin_info'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function getAdminInfo(): any | null {
  const raw = localStorage.getItem(ADMIN_KEY)
  return raw ? JSON.parse(raw) : null
}

export function saveAuth(data: { access_token: string; username: string; role: string }) {
  localStorage.setItem(TOKEN_KEY, data.access_token)
  localStorage.setItem(ADMIN_KEY, JSON.stringify({ username: data.username, role: data.role }))
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(ADMIN_KEY)
}

export function isLoggedIn(): boolean {
  return !!getToken()
}

async function request<T = any>(method: string, path: string, body?: any): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`

  const resp = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined
  })

  if (resp.status === 401) {
    clearAuth()
    window.location.href = '/login'
    throw new Error('登录已过期，请重新登录')
  }

  const data = await resp.json()
  if (!resp.ok) {
    const msg = data.detail?.message || data.detail || '请求失败'
    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg))
  }
  return data
}

export const api = {
  login: (username: string, password: string) =>
    request<{ data: { access_token: string; username: string; role: string } }>('POST', '/admin/login', { username, password }),

  dashboard: () => request<{ data: any }>('GET', '/admin/dashboard'),

  users: {
    list: (params: { keyword?: string; status?: string; page: number; size: number }) => {
      const qs = new URLSearchParams()
      if (params.keyword) qs.set('keyword', params.keyword)
      if (params.status) qs.set('status', params.status)
      qs.set('page', String(params.page))
      qs.set('size', String(params.size))
      return request('GET', `/admin/users?${qs.toString()}`)
    },
    ban: (userId: number, action: 'ban' | 'unban') =>
      request('PUT', `/admin/users/${userId}/ban?action=${action}`),
    edit: (userId: number, data: { nickname?: string; member_level?: string; points?: number; status?: string }) =>
      request('PUT', `/admin/users/${userId}`, data)
  },

  pets: {
    list: (page: number, size: number) =>
      request('GET', `/admin/pets?page=${page}&size=${size}`)
  },

  devices: {
    list: (params: { keyword?: string; status?: string; page: number; size: number }) => {
      const qs = new URLSearchParams()
      if (params.keyword) qs.set('keyword', params.keyword)
      if (params.status) qs.set('status', params.status)
      qs.set('page', String(params.page))
      qs.set('size', String(params.size))
      return request('GET', `/admin/devices?${qs.toString()}`)
    }
  },

  alarms: {
    list: (params: { status?: string; page: number; size: number }) => {
      const qs = new URLSearchParams()
      if (params.status) qs.set('status', params.status)
      qs.set('page', String(params.page))
      qs.set('size', String(params.size))
      return request('GET', `/admin/alarms?${qs.toString()}`)
    },
    handle: (ids: number[], status: 'handled' | 'false_positive') =>
      request('PUT', '/admin/alarms/handle', { ids, status })
  },

  orders: {
    list: (params: { status?: string; page: number; size: number }) => {
      const qs = new URLSearchParams()
      if (params.status) qs.set('status', params.status)
      qs.set('page', String(params.page))
      qs.set('size', String(params.size))
      return request('GET', `/admin/orders?${qs.toString()}`)
    },
    refund: (orderNo: string) => request('PUT', `/admin/orders/${orderNo}/refund`)
  }
}
