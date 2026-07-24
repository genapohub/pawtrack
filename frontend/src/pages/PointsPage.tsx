/**
 * S8 — 积分页
 * 积分余额、每日签到、积分明细、积分商城
 */
import React, { useState, useEffect } from 'react'
import { api } from '../api/client'
import { showToast } from '../utils/toast'

interface PointLog {
  id: number
  change: number
  type: string
  related_id: string | null
  balance: number
  created_at: string
}

interface ShopItem {
  id: number
  name: string
  points: number
  image: string
}

const LOG_TYPE_META: Record<string, { label: string; icon: string }> = {
  meet: { label: '碰头奖励', icon: '🤝' },
  invite: { label: '邀请奖励', icon: '🎁' },
  signin: { label: '每日签到', icon: '📅' },
  purchase: { label: '兑换消费', icon: '🛒' },
  expire: { label: '积分过期', icon: '⏰' },
  admin: { label: '后台调整', icon: '⚙️' }
}

export function PointsPage({ onBack }: { onBack: () => void }) {
  const [balance, setBalance] = useState(0)
  const [logs, setLogs] = useState<PointLog[]>([])
  const [shop, setShop] = useState<ShopItem[]>([])
  const [loading, setLoading] = useState(true)
  const [signing, setSigning] = useState(false)
  const [view, setView] = useState<'logs' | 'shop'>('logs')

  const loadAll = async () => {
    setLoading(true)
    try {
      const [balResp, logsResp, shopResp] = await Promise.all([
        api.points.balance(),
        api.points.logs(1, 30),
        api.points.shop()
      ])
      setBalance(balResp.data?.balance || 0)
      setLogs(logsResp.data || [])
      setShop(shopResp.data || [])
    } catch (e: any) {
      showToast(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAll()
  }, [])

  const signin = async () => {
    setSigning(true)
    try {
      const resp = await api.points.signin()
      showToast(`签到成功 +${resp.data?.awarded || 5} 积分 🎉`)
      loadAll()
    } catch (e: any) {
      showToast(e.message)
    } finally {
      setSigning(false)
    }
  }

  const exchange = (item: ShopItem) => {
    if (balance < item.points) {
      showToast('积分不足，继续努力～')
      return
    }
    if (!confirm(`确认用 ${item.points} 积分兑换「${item.name}」？`)) return
    showToast('兑换功能开发中，敬请期待～')
  }

  const formatTime = (iso: string) => {
    if (!iso) return ''
    const d = new Date(iso)
    return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="screen">
      <div className="nav-bar">
        <button className="nav-back" onClick={onBack}>‹</button>
        我的积分
      </div>

      {/* 积分余额 Hero */}
      <div className="points-hero">
        <div className="points-hero-label">当前积分余额</div>
        <div className="points-hero-num">{balance.toLocaleString()}</div>
        <button
          className="btn points-signin-btn"
          onClick={signin}
          disabled={signing}
        >
          {signing ? '签到中...' : '📅 每日签到 +5'}
        </button>
      </div>

      {/* 子视图切换 */}
      <div className="filter-bar">
        <button
          className={`filter-tab ${view === 'logs' ? 'active' : ''}`}
          onClick={() => setView('logs')}
        >
          积分明细
        </button>
        <button
          className={`filter-tab ${view === 'shop' ? 'active' : ''}`}
          onClick={() => setView('shop')}
        >
          积分商城
        </button>
      </div>

      <div style={{ padding: '12px 16px 83px' }}>
        {loading ? (
          <div className="loading"><div className="spinner" /> 加载中...</div>
        ) : view === 'logs' ? (
          <>
            {logs.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">📊</div>
                <div className="empty-state-text">
                  暂无积分记录
                  <br />
                  <span style={{ fontSize: 12, color: 'var(--muted)' }}>
                    每日签到或发起碰头即可获得积分
                  </span>
                </div>
              </div>
            ) : (
              logs.map(log => {
                const meta = LOG_TYPE_META[log.type] || { label: log.type, icon: '💰' }
                const positive = log.change > 0
                return (
                  <div key={log.id} className="log-row">
                    <div className="log-icon">{meta.icon}</div>
                    <div className="log-main">
                      <div className="log-title">{meta.label}</div>
                      <div className="log-time">{formatTime(log.created_at)}</div>
                    </div>
                    <div className="log-amount">
                      <div className={positive ? 'log-change pos' : 'log-change neg'}>
                        {positive ? '+' : ''}{log.change}
                      </div>
                      <div className="log-balance">余额 {log.balance}</div>
                    </div>
                  </div>
                )
              })
            )}
          </>
        ) : (
          <>
            <div className="section-desc" style={{ padding: '0 0 12px' }}>
              用积分兑换宠物好礼，更多商品持续上架中
            </div>
            <div className="shop-grid">
              {shop.map(item => {
                const canAfford = balance >= item.points
                return (
                  <div key={item.id} className="shop-card">
                    <div className="shop-image">{item.image}</div>
                    <div className="shop-name">{item.name}</div>
                    <div className="shop-points">{item.points} 积分</div>
                    <button
                      className={`btn ${canAfford ? 'btn-primary' : 'btn-disabled'} shop-btn`}
                      onClick={() => exchange(item)}
                      disabled={!canAfford}
                    >
                      {canAfford ? '立即兑换' : '积分不足'}
                    </button>
                  </div>
                )
              })}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
