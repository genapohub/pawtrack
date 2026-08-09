/**
 * 宠迹 PawTrack mobile — API 客户端 token 逻辑测试
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { getToken, getRefreshToken, saveAuth, clearAuth, getUser, isLoggedIn } from '../api/client'

describe('Auth token storage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('saveAuth 持久化 access/refresh token 与用户信息', () => {
    saveAuth({
      access_token: 'access-abc',
      refresh_token: 'refresh-xyz',
      user_id: 123,
      phone: '138****8888',
      nickname: '张工',
      member_level: 'pro'
    })
    expect(getToken()).toBe('access-abc')
    expect(getRefreshToken()).toBe('refresh-xyz')
    expect(isLoggedIn()).toBe(true)
    const user = getUser()
    expect(user).toMatchObject({
      user_id: 123,
      phone: '138****8888',
      nickname: '张工',
      member_level: 'pro'
    })
  })

  it('clearAuth 清除全部鉴权数据', () => {
    saveAuth({ access_token: 'a', refresh_token: 'r' })
    expect(isLoggedIn()).toBe(true)
    clearAuth()
    expect(getToken()).toBeNull()
    expect(getRefreshToken()).toBeNull()
    expect(getUser()).toBeNull()
    expect(isLoggedIn()).toBe(false)
  })

  it('未保存 token 时 isLoggedIn 返回 false', () => {
    expect(isLoggedIn()).toBe(false)
    expect(getToken()).toBeNull()
  })

  it('saveAuth 缺省字段时用户信息仍可读取', () => {
    saveAuth({ access_token: 'a', refresh_token: 'r' })
    const user = getUser()
    expect(user).not.toBeNull()
    expect(user.user_id).toBeUndefined()
    expect(user.member_level).toBeUndefined()
  })
})
