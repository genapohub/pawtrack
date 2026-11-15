/**
 * 管理后台本地预览 Mock（非验收）。
 * 关闭：启动时加 VITE_USE_MOCK=false，将请求打到本地后端。
 */

const NOW = '2026-11-15T12:00:00+08:00'

const store = {
  users: [
    { id: 1, nickname: '林小满', phone: '138****1001', member_level: 'pro', points: 1280, status: 'active', member_expire_at: '2027-01-15T00:00:00+08:00', created_at: '2026-08-01T10:00:00+08:00' },
    { id: 2, nickname: '陈同学', phone: '139****2002', member_level: 'basic', points: 240, status: 'active', member_expire_at: '2026-12-01T00:00:00+08:00', created_at: '2026-09-12T09:00:00+08:00' },
    { id: 3, nickname: '已封禁账号', phone: '137****3003', member_level: 'free', points: 0, status: 'blocked', member_expire_at: null, created_at: '2026-10-03T18:00:00+08:00' },
  ],
  pets: [
    { id: 1, user_id: 1, name: '奶茶', type: 'cat', breed: '英国短毛猫', gender: 'female', fence_enabled: true, fence_radius: 100, status: 'active', created_at: NOW },
    { id: 2, user_id: 1, name: '阿黄', type: 'dog', breed: '柯基', gender: 'male', fence_enabled: true, fence_radius: 300, status: 'active', created_at: NOW },
  ],
  devices: [
    { id: 1, sn: 'PT-CAT-MOCK-0001', user_id: 1, pet_id: 1, hardware_type: 'cat', firmware_version: '0.1.0', battery_level: 86, status: 'online', last_online_at: NOW },
    { id: 2, sn: 'PT-DOG-MOCK-0002', user_id: 1, pet_id: 2, hardware_type: 'dog', firmware_version: '0.1.0', battery_level: 42, status: 'online', last_online_at: NOW },
  ],
  alarms: [
    { id: 1, pet_id: 1, user_id: 1, type: 'leave_fence_cat', severity: 'high', status: 'active', address: '本地 Mock 地址', created_at: NOW },
    { id: 2, pet_id: 2, user_id: 1, type: 'low_battery', severity: 'medium', status: 'handled', address: '本地 Mock 地址', created_at: NOW },
  ],
  orders: [
    { id: 1, order_no: 'PT-MOCK-20261115001', user_id: 1, type: 'subscription', product_id: 'pro_month', amount: 29.9, pay_channel: 'mock', status: 'paid', paid_at: NOW, created_at: NOW },
  ],
  meets: [
    { id: 1, created_at: NOW, from_pet: '奶茶', to_pet: '阿黄', distance: 12, points: 10, abnormal: '', color: 'green', status: 'success' },
    { id: 2, created_at: NOW, from_pet: '阿黄', to_pet: '豆豆', distance: 8, points: 0, abnormal: '距离异常（Mock）', color: 'red', status: 'pending' },
  ],
}

function paginate(list: any[], page = 1, size = 10) {
  const p = Number(page) || 1
  const s = Number(size) || 10
  const start = (p - 1) * s
  return { data: list.slice(start, start + s), pagination: { total: list.length, page: p, size: s } }
}

function parsePath(path: string) {
  const i = path.indexOf('?')
  if (i < 0) return { pathname: path, params: new URLSearchParams() }
  return { pathname: path.slice(0, i), params: new URLSearchParams(path.slice(i + 1)) }
}

/** 与真实 API 客户端相同的返回形态；失败抛 Error。 */
export function mockRequest(method: string, path: string, body?: any): any {
  const { pathname, params } = parsePath(path)
  const m = method.toUpperCase()
  const page = Number(params.get('page') || 1)
  const size = Number(params.get('size') || 10)

  if (m === 'POST' && pathname === '/admin/login') {
    const username = String(body?.username || '')
    const password = String(body?.password || '')
    if (username === 'admin' && password === 'mock') {
      return { data: { access_token: 'mock-admin-token', username: 'admin', role: 'super_admin' } }
    }
    throw new Error('Mock 登录失败：请用 admin / mock')
  }

  if (m === 'GET' && pathname === '/admin/dashboard') {
    return {
      data: {
        users: store.users.length,
        pets: store.pets.length,
        devices: store.devices.length,
        online_devices: store.devices.filter((d) => d.status === 'online').length,
        active_alarms: store.alarms.filter((a) => a.status === 'active').length,
        today_alarms: store.alarms.length,
        paid_orders: store.orders.filter((o) => o.status === 'paid').length,
        revenue: store.orders.filter((o) => o.status === 'paid').reduce((sum, o) => sum + o.amount, 0),
        meets: store.meets.length,
        success_meets: store.meets.filter((x) => x.status === 'success').length,
        active_subs: 1,
      },
    }
  }

  if (m === 'GET' && pathname === '/admin/users') {
    let list = [...store.users]
    const keyword = params.get('keyword')
    const status = params.get('status')
    if (keyword) list = list.filter((u) => `${u.nickname}${u.phone}`.includes(keyword))
    if (status) list = list.filter((u) => u.status === status)
    return paginate(list, page, size)
  }

  const ban = pathname.match(/^\/admin\/users\/(\d+)\/ban$/)
  if (m === 'PUT' && ban) {
    const user = store.users.find((u) => u.id === Number(ban[1]))
    if (!user) throw new Error('用户不存在')
    user.status = params.get('action') === 'unban' ? 'active' : 'blocked'
    return { data: { ok: true } }
  }

  const edit = pathname.match(/^\/admin\/users\/(\d+)$/)
  if (m === 'PUT' && edit) {
    const user = store.users.find((u) => u.id === Number(edit[1]))
    if (!user) throw new Error('用户不存在')
    Object.assign(user, body || {})
    return { data: { ok: true } }
  }

  if (m === 'GET' && pathname === '/admin/pets') {
    return paginate(store.pets, page, size)
  }

  if (m === 'GET' && pathname === '/admin/devices') {
    let list = [...store.devices]
    const keyword = params.get('keyword')
    const status = params.get('status')
    if (keyword) list = list.filter((d) => d.sn.includes(keyword))
    if (status) list = list.filter((d) => d.status === status)
    return paginate(list, page, size)
  }

  if (m === 'GET' && pathname === '/admin/alarms') {
    let list = [...store.alarms]
    const status = params.get('status')
    if (status) list = list.filter((a) => a.status === status)
    return paginate(list, page, size)
  }

  if (m === 'PUT' && pathname === '/admin/alarms/handle') {
    const ids: number[] = body?.ids || []
    const status = body?.status
    store.alarms.forEach((a) => {
      if (ids.includes(a.id)) a.status = status
    })
    return { data: { ok: true } }
  }

  if (m === 'GET' && pathname === '/admin/orders') {
    let list = [...store.orders]
    const status = params.get('status')
    if (status) list = list.filter((o) => o.status === status)
    return paginate(list, page, size)
  }

  const refund = pathname.match(/^\/admin\/orders\/([^/]+)\/refund$/)
  if (m === 'PUT' && refund) {
    const order = store.orders.find((o) => o.order_no === decodeURIComponent(refund[1]))
    if (!order) throw new Error('订单不存在')
    order.status = 'refunded'
    return { data: { ok: true } }
  }

  if (m === 'GET' && pathname === '/admin/meets') {
    let list = [...store.meets]
    const status = params.get('status')
    if (status) list = list.filter((x) => x.status === status)
    return { data: { items: list }, pagination: { total: list.length, page, size } }
  }

  const audit = pathname.match(/^\/admin\/meets\/(\d+)\/audit$/)
  if (m === 'PUT' && audit) {
    const meet = store.meets.find((x) => x.id === Number(audit[1]))
    if (!meet) throw new Error('记录不存在')
    meet.status = params.get('action') === 'reject' ? 'failed' : 'success'
    if (params.get('action') === 'reject') meet.points = 0
    return { data: { ok: true } }
  }

  throw new Error(`Mock 未覆盖该接口：${m} ${pathname}`)
}
