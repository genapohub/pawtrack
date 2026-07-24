/**
 * S7 — 会员购买页
 * 套餐列表、当前订阅状态、创建订单+模拟支付、取消续费、订单历史
 */
import React, { useState, useEffect } from 'react'
import { api } from '../api/client'
import { showToast } from '../utils/toast'

interface Plan {
  plan: string
  name: string
  price: number
  level: string
  days: number
}

interface Subscription {
  plan: string
  status: string
  started_at?: string | null
  expire_at?: string | null
  auto_renew?: boolean
}

interface OrderItem {
  id: number
  order_no: string
  type: string
  amount: number
  status: string
  pay_channel: string | null
  paid_at: string | null
  created_at: string
}

const LEVEL_META: Record<string, { label: string; cls: string; icon: string }> = {
  free: { label: '免费版', cls: 'badge-offline', icon: '🆓' },
  basic: { label: '基础版', cls: 'badge-online', icon: '⭐' },
  pro: { label: 'Pro版', cls: 'badge-pro', icon: '💎' }
}

const BENEFITS: { level: string; items: string[] }[] = [
  {
    level: 'free',
    items: ['定位刷新 5 分钟/次', '历史轨迹 7 天', '围栏报警', '1 台设备']
  },
  {
    level: 'basic',
    items: ['定位刷新 5 秒/次', '历史轨迹无限', '围栏报警', '3 台设备', '附近宠物']
  },
  {
    level: 'pro',
    items: ['定位刷新 5 秒/次', '历史轨迹无限', '围栏报警', '10 台设备', '家人共享 5 人', '优先客服']
  }
]

export function MembershipPage({ onBack }: { onBack: () => void }) {
  const [plans, setPlans] = useState<Plan[]>([])
  const [sub, setSub] = useState<Subscription | null>(null)
  const [orders, setOrders] = useState<OrderItem[]>([])
  const [loading, setLoading] = useState(true)
  const [payingPlan, setPayingPlan] = useState<string | null>(null)
  const [view, setView] = useState<'plans' | 'history'>('plans')

  const loadAll = async () => {
    setLoading(true)
    try {
      const [plansResp, subResp] = await Promise.all([
        api.orders.plans(),
        api.orders.subscription()
      ])
      setPlans(plansResp.data || [])
      setSub(subResp.data || null)
    } catch (e: any) {
      showToast(e.message)
    } finally {
      setLoading(false)
    }
  }

  const loadHistory = async () => {
    try {
      const resp = await api.orders.history(1, 20)
      setOrders(resp.data || [])
    } catch (e: any) {
      showToast(e.message)
    }
  }

  useEffect(() => {
    loadAll()
  }, [])

  useEffect(() => {
    if (view === 'history') loadHistory()
  }, [view])

  const buyPlan = async (plan: Plan) => {
    setPayingPlan(plan.plan)
    try {
      // 1. 创建订单
      const createResp = await api.orders.create(plan.plan, 'wechat')
      const orderNo = createResp.data?.order_no
      if (!orderNo) {
        showToast('订单创建失败')
        return
      }

      // 2. 模拟支付回调（MVP）
      const txnId = `MOCK${Date.now()}${Math.floor(Math.random() * 10000)}`
      await api.orders.payCallback(orderNo, txnId)

      showToast(`🎉 ${plan.name} 开通成功！`)
      loadAll()
    } catch (e: any) {
      showToast(e.message)
    } finally {
      setPayingPlan(null)
    }
  }

  const cancelRenew = async () => {
    if (!confirm('确认关闭自动续费？')) return
    try {
      await api.orders.cancelSubscription(false)
      showToast('已关闭自动续费')
      loadAll()
    } catch (e: any) {
      showToast(e.message)
    }
  }

  const formatExpire = (iso?: string | null) => {
    if (!iso) return '—'
    const d = new Date(iso)
    const now = new Date()
    const days = Math.ceil((d.getTime() - now.getTime()) / 86400000)
    return `${d.toLocaleDateString('zh-CN')}（剩 ${days} 天）`
  }

  const currentLevel = sub?.plan ? (sub.plan.startsWith('basic') ? 'basic' : sub.plan.startsWith('pro') ? 'pro' : 'free') : 'free'
  const currentMeta = LEVEL_META[currentLevel] || LEVEL_META.free

  return (
    <div className="screen">
      <div className="nav-bar">
        <button className="nav-back" onClick={onBack}>‹</button>
        会员订阅
      </div>

      {/* 当前会员状态 */}
      <div className="member-hero" style={{ background: currentLevel === 'pro' ? 'linear-gradient(135deg,#8B5CF6,#6366F1)' : currentLevel === 'basic' ? 'linear-gradient(135deg,#3B82F6,#06B6D4)' : 'linear-gradient(135deg,#94A3B8,#64748B)' }}>
        <div className="member-hero-icon">{currentMeta.icon}</div>
        <div className="member-hero-level">{currentMeta.label}</div>
        {sub && sub.status === 'active' && sub.expire_at ? (
          <div className="member-hero-expire">有效期至 {formatExpire(sub.expire_at)}</div>
        ) : (
          <div className="member-hero-expire">升级会员解锁更多权益</div>
        )}
        {sub?.auto_renew && (
          <button className="member-cancel-btn" onClick={cancelRenew}>关闭自动续费</button>
        )}
      </div>

      {/* 子视图切换 */}
      <div className="filter-bar">
        <button
          className={`filter-tab ${view === 'plans' ? 'active' : ''}`}
          onClick={() => setView('plans')}
        >
          套餐购买
        </button>
        <button
          className={`filter-tab ${view === 'history' ? 'active' : ''}`}
          onClick={() => setView('history')}
        >
          订单记录
        </button>
      </div>

      <div style={{ padding: '0 16px 83px' }}>
        {loading ? (
          <div className="loading"><div className="spinner" /> 加载中...</div>
        ) : view === 'plans' ? (
          <>
            {/* 权益对比 */}
            <div className="card" style={{ marginTop: 12 }}>
              <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 12 }}>📊 权益对比</div>
              {BENEFITS.map(b => {
                const meta = LEVEL_META[b.level]
                const isCurrent = b.level === currentLevel
                return (
                  <div key={b.level} className={`benefit-row ${isCurrent ? 'current' : ''}`}>
                    <div className="benefit-row-head">
                      <span className={`badge ${meta.cls}`}>{meta.icon} {meta.label}</span>
                      {isCurrent && <span style={{ fontSize: 11, color: 'var(--success)' }}>当前</span>}
                    </div>
                    <div className="benefit-items">
                      {b.items.map((it, i) => (
                        <span key={i} className="benefit-tag">{it}</span>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>

            {/* 套餐卡片 */}
            <div className="section-title" style={{ padding: '16px 0 8px' }}>💳 选择套餐</div>
            {plans.map(plan => {
              const planLevel = plan.level
              const meta = LEVEL_META[planLevel] || LEVEL_META.free
              const isCurrent = planLevel === currentLevel
              const isYear = plan.plan.includes('year')
              return (
                <div key={plan.plan} className={`plan-card ${planLevel === 'pro' ? 'plan-pro' : ''}`}>
                  <div className="plan-card-head">
                    <div>
                      <span className="plan-name">{meta.icon} {plan.name}</span>
                      <div className="plan-period">{isYear ? '年卡 · 365 天' : '月卡 · 30 天'}</div>
                    </div>
                    <div className="plan-price">
                      <span className="plan-price-num">¥{plan.price}</span>
                      {isYear && <span className="plan-price-unit">/年</span>}
                    </div>
                  </div>
                  {isYear && (
                    <div className="plan-save">年卡更划算，相当于 ¥{(plan.price / 12).toFixed(1)}/月</div>
                  )}
                  <button
                    className={`btn ${planLevel === 'pro' ? 'btn-pro' : 'btn-primary'}`}
                    onClick={() => buyPlan(plan)}
                    disabled={isCurrent || payingPlan === plan.plan}
                  >
                    {isCurrent ? '当前等级' :
                     payingPlan === plan.plan ? '支付中...' :
                     `开通 ${meta.label}`}
                  </button>
                </div>
              )
            })}
          </>
        ) : (
          <>
            {orders.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">🧾</div>
                <div className="empty-state-text">暂无订单记录</div>
              </div>
            ) : (
              orders.map(order => (
                <div key={order.id} className="alarm-card">
                  <div className="alarm-card-head">
                    <div className="alarm-icon">🧾</div>
                    <div className="alarm-main">
                      <div className="alarm-title">¥{order.amount}</div>
                      <div className="alarm-time">{order.order_no}</div>
                    </div>
                    <span className={`badge ${
                      order.status === 'paid' ? 'badge-online' :
                      order.status === 'pending' ? 'badge-offline' : 'badge-cat'
                    }`}>
                      {order.status === 'paid' ? '已支付' :
                       order.status === 'pending' ? '待支付' :
                       order.status === 'cancelled' ? '已取消' : order.status}
                    </span>
                  </div>
                  <div className="alarm-meta">
                    <span>{order.pay_channel ? `${order.pay_channel} 支付` : ''}</span>
                    {order.paid_at && <span>支付时间 {new Date(order.paid_at).toLocaleString('zh-CN')}</span>}
                  </div>
                  <div className="alarm-meta">
                    <span>下单 {new Date(order.created_at).toLocaleString('zh-CN')}</span>
                  </div>
                </div>
              ))
            )}
          </>
        )}
      </div>
    </div>
  )
}
