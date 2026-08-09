/**
 * 宠迹 PawTrack — Token 管理（uni.storage 封装）
 */
const ACCESS_KEY = 'pawtrack_access_token'
const REFRESH_KEY = 'pawtrack_refresh_token'
const USER_KEY = 'pawtrack_user'

export function getAccessToken(): string {
  return uni.getStorageSync(ACCESS_KEY) || ''
}

export function getRefreshToken(): string {
  return uni.getStorageSync(REFRESH_KEY) || ''
}

export function setTokens(access: string, refresh: string): void {
  uni.setStorageSync(ACCESS_KEY, access)
  uni.setStorageSync(REFRESH_KEY, refresh)
}

export function clearTokens(): void {
  uni.removeStorageSync(ACCESS_KEY)
  uni.removeStorageSync(REFRESH_KEY)
  uni.removeStorageSync(USER_KEY)
}

export function isLoggedIn(): boolean {
  return !!getAccessToken()
}

export function setUser(user: any): void {
  uni.setStorageSync(USER_KEY, user)
}

export function getUser(): any {
  return uni.getStorageSync(USER_KEY) || null
}
