/**
 * 宠迹 PawTrack admin — API 客户端 token 逻辑测试
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { getToken, getAdminInfo, saveAuth, clearAuth, isLoggedIn } from '../api/client'

describe('Admin auth token storage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('saveAuth 持久化 admin token 与信息', () => {
    saveAuth({ access_token: 'admin-token-abc', username: 'admin', role: 'super_admin' })
    expect(getToken()).toBe('admin-token-abc')
    expect(isLoggedIn()).toBe(true)
    const info = getAdminInfo()
    expect(info).toMatchObject({ username: 'admin', role: 'super_admin' })
  })

  it('clearAuth 清除全部鉴权数据', () => {
    saveAuth({ access_token: 't', username: 'admin', role: 'super_admin' })
    expect(isLoggedIn()).toBe(true)
    clearAuth()
    expect(getToken()).toBeNull()
    expect(getAdminInfo()).toBeNull()
    expect(isLoggedIn()).toBe(false)
  })

  it('未保存 token 时 isLoggedIn 返回 false', () => {
    expect(isLoggedIn()).toBe(false)
    expect(getAdminInfo()).toBeNull()
  })
})
