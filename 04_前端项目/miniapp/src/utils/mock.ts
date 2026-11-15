/**
 * 小程序本地预览 Mock（非验收）。由 request.ts 在 USE_MOCK 时拦截。
 * 不模拟真实微信登录 / 支付 / 短信 / 地图 / 硬件。
 */

const NOW_ISO = '2026-11-15T12:00:00+08:00'
const NOW_TS = 1763182800
const DEFAULT_LAT = 34.7466
const DEFAULT_LNG = 113.6253

const user = {
  user_id: 1,
  phone: '13800000000',
  nickname: '本地预览用户',
  member_level: 'basic',
  privacy_location: true,
}

const pets = [
  {
    id: 1,
    name: '奶茶',
    type: 'cat',
    breed: '英国短毛猫',
    fence_enabled: true,
    fence_radius: 100,
  },
  {
    id: 2,
    name: '阿黄',
    type: 'dog',
    breed: '柯基',
    fence_enabled: true,
    fence_radius: 300,
  },
]

const devices = [
  { id: 1, sn: 'PT-CAT-MOCK-0001', pet_id: 1, status: 'online', battery: 86, hardware_type: 'cat' },
  { id: 2, sn: 'PT-DOG-MOCK-0002', pet_id: 2, status: 'online', battery: 42, hardware_type: 'dog' },
]

const locations: Record<number, { lat: number; lng: number; battery: number; source: string; ts: number }> = {
  1: { lat: DEFAULT_LAT, lng: DEFAULT_LNG, battery: 86, source: 'wifi', ts: NOW_TS },
  2: { lat: DEFAULT_LAT + 0.001, lng: DEFAULT_LNG + 0.001, battery: 42, source: 'gps', ts: NOW_TS },
}

const alarms = [
  { id: 1, pet_id: 1, type: 'leave_fence_cat', severity: 'high', status: 'active', address: '本地 Mock 地址', lat: DEFAULT_LAT, lng: DEFAULT_LNG, created_at: NOW_ISO },
  { id: 2, pet_id: 2, type: 'low_battery', severity: 'medium', status: 'handled', address: '本地 Mock 地址', lat: DEFAULT_LAT, lng: DEFAULT_LNG, created_at: NOW_ISO },
]

const nearby = [
  { id: 101, name: '豆豆', type: 'dog', distance: 80, lat: DEFAULT_LAT + 0.002, lng: DEFAULT_LNG + 0.001 },
  { id: 102, name: '橘子', type: 'cat', distance: 160, lat: DEFAULT_LAT - 0.001, lng: DEFAULT_LNG + 0.002 },
]

const meets = [
  { id: 1, status: 'success', from_pet: '奶茶', to_pet: '豆豆', created_at: NOW_ISO, points: 10 },
]

const alarmSettings = {
  push_enabled: true,
  sms_enabled: false,
  contacts: [],
}

function pathOf(url: string): { pathname: string; params: URLSearchParams } {
  const raw = url.split('?')[0]
  const pathname = raw.replace(/^https?:\/\/[^/]+/, '')
  const qs = url.includes('?') ? url.split('?')[1] : ''
  return { pathname, params: new URLSearchParams(qs) }
}

function authPayload() {
  return {
    access_token: 'mock-miniapp-access',
    refresh_token: 'mock-miniapp-refresh',
    user_id: user.user_id,
    phone: user.phone,
    nickname: user.nickname,
    member_level: user.member_level,
  }
}

/** 返回已解包的 data，失败抛 Error。 */
export function mockRequest(method: string, url: string, data?: any): any {
  const { pathname, params } = pathOf(url)
  const path = pathname.replace(/^\/api\/v1/, '') || pathname
  const m = method.toUpperCase()

  if (m === 'POST' && (path === '/auth/login' || path === '/auth/register' || path === '/auth/wechat-login')) {
    return authPayload()
  }
  if (m === 'POST' && path === '/auth/refresh') {
    return { access_token: 'mock-miniapp-access', refresh_token: 'mock-miniapp-refresh' }
  }

  if (m === 'GET' && path === '/users/me') return { ...user }
  if (m === 'PUT' && path === '/users/me') {
    Object.assign(user, data || {})
    return { ...user }
  }
  if (m === 'GET' && path === '/users/me/contacts') return []
  if (m === 'PUT' && path === '/users/me/contacts') return { ok: true }
  if (m === 'GET' && path === '/invites') return { items: [] }

  if (m === 'GET' && path === '/pets') return pets.map((p) => ({ ...p }))
  const petOne = path.match(/^\/pets\/(\d+)$/)
  if (m === 'GET' && petOne) {
    const pet = pets.find((p) => p.id === Number(petOne[1]))
    if (!pet) throw new Error('宠物不存在')
    return { ...pet }
  }
  if (m === 'POST' && path === '/pets') {
    const created = { id: Date.now(), fence_enabled: true, fence_radius: data?.type === 'cat' ? 100 : 300, ...data }
    pets.push(created)
    return created
  }
  const fence = path.match(/^\/pets\/(\d+)\/fence$/)
  if (m === 'PUT' && fence) {
    const pet = pets.find((p) => p.id === Number(fence[1]))
    if (pet) Object.assign(pet, data || {})
    return { ok: true }
  }

  if (m === 'GET' && path === '/devices') return devices.map((d) => ({ ...d }))
  if (m === 'POST' && path === '/devices/register') {
    const created = { id: Date.now(), sn: data?.sn || 'PT-MOCK-NEW', pet_id: data?.pet_id || null, status: 'online', battery: 100, hardware_type: 'dog' }
    devices.push(created)
    return created
  }
  if (m === 'POST' && path === '/devices/bind') return { ok: true }
  if (m === 'POST' && path === '/devices/unbind') return { ok: true }
  const findDev = path.match(/^\/devices\/(\d+)\/find$/)
  if (m === 'POST' && findDev) return { ok: true }
  const ota = path.match(/^\/devices\/(\d+)\/ota\/progress$/)
  if (m === 'GET' && ota) return { progress: 0, status: 'idle' }

  const realtime = path.match(/^\/location\/realtime\/(\d+)$/)
  if (m === 'GET' && realtime) {
    return locations[Number(realtime[1])] || { lat: DEFAULT_LAT, lng: DEFAULT_LNG, battery: 80, source: 'mock', ts: NOW_TS }
  }
  const history = path.match(/^\/location\/history\/(\d+)$/)
  if (m === 'GET' && history) {
    return { items: [locations[Number(history[1])] || { lat: DEFAULT_LAT, lng: DEFAULT_LNG, battery: 80, source: 'mock', ts: NOW_TS }] }
  }
  if (m === 'POST' && path === '/location/upload') {
    const pet = devices.find((d) => d.id === data?.device_id)
    const petId = pet?.pet_id || 1
    locations[petId] = {
      lat: data?.lat ?? DEFAULT_LAT,
      lng: data?.lng ?? DEFAULT_LNG,
      battery: data?.battery ?? 80,
      source: data?.source || 'mock',
      ts: data?.ts || Math.floor(Date.now() / 1000),
    }
    return { ok: true }
  }

  if (m === 'GET' && path === '/alarms') {
    const status = params.get('status')
    const items = status ? alarms.filter((a) => a.status === status) : alarms
    return { items }
  }
  const handle = path.match(/^\/alarms\/(\d+)\/handle$/)
  if (m === 'PUT' && handle) {
    const alarm = alarms.find((a) => a.id === Number(handle[1]))
    if (alarm) alarm.status = data?.status || 'handled'
    return { ok: true }
  }
  if (m === 'GET' && path === '/alarms/settings') return { ...alarmSettings }
  if (m === 'PUT' && path === '/alarms/settings') {
    Object.assign(alarmSettings, data || {})
    return { ok: true }
  }

  if (m === 'GET' && path === '/social/nearby') return nearby
  if (m === 'GET' && path === '/social/meets') return { items: meets }
  if (m === 'POST' && path === '/social/meets') {
    const created = { id: Date.now(), status: 'pending', from_pet: '奶茶', to_pet: data?.to_pet || '豆豆', created_at: NOW_ISO, points: 0 }
    meets.push(created)
    return created
  }
  const meetDist = path.match(/^\/social\/meets\/(\d+)\/distance$/)
  if (m === 'GET' && meetDist) return { distance: 12 }
  const meetAct = path.match(/^\/social\/meets\/(\d+)\/(confirm|complete|cancel)$/)
  if (m === 'PUT' && meetAct) return { ok: true }

  if (m === 'GET' && path === '/points/balance') return { balance: 128 }
  if (m === 'GET' && path === '/points/logs') return { items: [] }
  if (m === 'GET' && path === '/points/shop') return { items: [] }
  if (m === 'POST' && path === '/points/signin') return { points: 5, balance: 133 }

  if (m === 'GET' && path === '/orders/plans') {
    return [
      { plan: 'basic_month', name: '基础月卡', price: 9.9 },
      { plan: 'pro_month', name: 'Pro 月卡', price: 29.9 },
    ]
  }
  if (m === 'GET' && path === '/orders/subscription') return { plan: 'basic', status: 'active' }
  if (m === 'GET' && path === '/orders/history') return { items: [] }
  if (m === 'POST' && path === '/orders') return { order_no: 'PT-MOCK-ORDER', status: 'pending' }
  if (m === 'POST' && path === '/orders/pay-callback') return { ok: true, note: 'Mock 回调，非真实支付' }

  throw new Error(`Mock 未覆盖该接口：${m} ${path}`)
}
