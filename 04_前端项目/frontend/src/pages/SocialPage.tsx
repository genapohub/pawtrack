/**
 * S6 — 社交碰头页
 * 附近宠物发现、发起碰头、碰头记录管理
 */
import React, { useState, useEffect } from 'react'
import { api } from '../api/client'
import { wsClient, WsMessage } from '../ws/websocket'
import { showToast } from '../utils/toast'

interface NearbyPet {
  device_id: number
  pet_id: number
  pet_name: string
  pet_type: string
  pet_avatar: string | null
  distance: number
  lat: number
  lng: number
}

interface MeetItem {
  id: number
  initiator_pet_id: number
  receiver_pet_id: number
  status: string
  start_lat: number | null
  start_lng: number | null
  end_lat: number | null
  end_lng: number | null
  points_awarded: number
  started_at: string | null
  confirmed_at: string | null
  completed_at: string | null
  created_at: string
}

const MEET_STATUS_META: Record<string, { label: string; cls: string }> = {
  pending: { label: '等待确认', cls: 'badge-offline' },
  confirmed: { label: '进行中', cls: 'badge-online' },
  success: { label: '已完成', cls: 'badge-pro' },
  failed: { label: '已失败', cls: 'badge-cat' },
  cancelled: { label: '已取消', cls: 'badge-offline' }
}

// 郑州坐标（与地图首页模拟上报一致）
const DEFAULT_LAT = 34.7466
const DEFAULT_LNG = 113.6253

export function SocialPage() {
  const [view, setView] = useState<'nearby' | 'meets'>('nearby')
  const [nearby, setNearby] = useState<NearbyPet[]>([])
  const [meets, setMeets] = useState<MeetItem[]>([])
  const [loading, setLoading] = useState(true)
  const [actingId, setActingId] = useState<number | null>(null)
  const [myPetName, setMyPetName] = useState<string>('')

  const loadNearby = async () => {
    setLoading(true)
    try {
      const resp = await api.social.nearby(DEFAULT_LAT, DEFAULT_LNG, 2000)
      setNearby(resp.data || [])
    } catch (e: any) {
      showToast(e.message)
    } finally {
      setLoading(false)
    }
  }

  const loadMeets = async () => {
    setLoading(true)
    try {
      const resp = await api.social.listMeets()
      setMeets(resp.data || [])
    } catch (e: any) {
      showToast(e.message)
    } finally {
      setLoading(false)
    }
  }

  const loadMyPet = async () => {
    try {
      const resp = await api.pets.list()
      const list = resp.data || []
      if (list.length > 0) setMyPetName(list[0].name)
    } catch {
      // 静默
    }
  }

  useEffect(() => {
    loadMyPet()
    if (view === 'nearby') loadNearby()
    else loadMeets()
  }, [view])

  // WebSocket 接收碰头请求推送
  useEffect(() => {
    const unsub = wsClient.onMessage((msg: WsMessage) => {
      if (msg.type === 'alarm' && (msg as any).alarm_type === 'meet_request') {
        showToast('🤝 收到新的碰头邀请！')
        if (view === 'meets') loadMeets()
      }
    })
    return unsub
  }, [view])

  const startMeet = async (pet: NearbyPet) => {
    setActingId(pet.pet_id)
    try {
      await api.social.createMeet(pet.pet_id, DEFAULT_LAT, DEFAULT_LNG)
      showToast(`已向 ${pet.pet_name} 发起碰头邀请`)
      setView('meets')
    } catch (e: any) {
      showToast(e.message)
    } finally {
      setActingId(null)
    }
  }

  const confirmMeet = async (id: number) => {
    setActingId(id)
    try {
      await api.social.confirmMeet(id)
      showToast('已确认碰头')
      loadMeets()
    } catch (e: any) {
      showToast(e.message)
    } finally {
      setActingId(null)
    }
  }

  const completeMeet = async (id: number) => {
    setActingId(id)
    try {
      const resp = await api.social.completeMeet(id)
      showToast(`碰头完成！获得 ${resp.data?.points_awarded || 0} 积分 🎉`)
      loadMeets()
    } catch (e: any) {
      showToast(e.message)
    } finally {
      setActingId(null)
    }
  }

  const cancelMeet = async (id: number) => {
    setActingId(id)
    try {
      await api.social.cancelMeet(id)
      showToast('已取消碰头')
      loadMeets()
    } catch (e: any) {
      showToast(e.message)
    } finally {
      setActingId(null)
    }
  }

  const formatTime = (iso: string) => {
    if (!iso) return ''
    const d = new Date(iso)
    return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="screen">
      <div className="nav-bar">🤝 好朋狗碰头</div>

      {/* 子视图切换 */}
      <div className="filter-bar">
        <button
          className={`filter-tab ${view === 'nearby' ? 'active' : ''}`}
          onClick={() => setView('nearby')}
        >
          附近宠物
        </button>
        <button
          className={`filter-tab ${view === 'meets' ? 'active' : ''}`}
          onClick={() => setView('meets')}
        >
          碰头记录
        </button>
      </div>

      <div style={{ padding: '12px 16px 83px' }}>
        {loading ? (
          <div className="loading"><div className="spinner" /> 加载中...</div>
        ) : view === 'nearby' ? (
          <>
            <div className="section-desc" style={{ padding: '0 0 12px' }}>
              {myPetName ? `以「${myPetName}」的身份发现附近伙伴` : '请先添加宠物后再发起碰头'} · 搜索半径 2km
            </div>
            {nearby.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">🐶</div>
                <div className="empty-state-text">
                  附近暂无在线宠物
                  <br />
                  <span style={{ fontSize: 12, color: 'var(--muted)' }}>
                    可在首页「模拟定位上报」后再次刷新
                  </span>
                </div>
              </div>
            ) : (
              nearby.map(pet => (
                <div key={pet.pet_id} className="nearby-card">
                  <div className="pet-avatar" style={{
                    background: pet.pet_type === 'cat' ? '#FFF7ED' : '#EFF6FF'
                  }}>
                    {pet.pet_type === 'cat' ? '🐱' : '🐶'}
                  </div>
                  <div className="nearby-info">
                    <div className="nearby-name">
                      {pet.pet_name}
                      <span className={`badge ${pet.pet_type === 'cat' ? 'badge-cat' : 'badge-dog'}`} style={{ marginLeft: 8 }}>
                        {pet.pet_type === 'cat' ? '猫' : '狗'}
                      </span>
                    </div>
                    <div className="nearby-distance">距离 {pet.distance} 米</div>
                  </div>
                  <button
                    className="btn btn-primary nearby-btn"
                    onClick={() => startMeet(pet)}
                    disabled={actingId === pet.pet_id}
                  >
                    {actingId === pet.pet_id ? '...' : '发起碰头'}
                  </button>
                </div>
              ))
            )}
            <button
              className="btn btn-outline"
              style={{ marginTop: 16 }}
              onClick={loadNearby}
              disabled={loading}
            >
              🔄 刷新附近列表
            </button>
          </>
        ) : (
          <>
            {meets.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">🤝</div>
                <div className="empty-state-text">
                  暂无碰头记录
                  <br />
                  <span style={{ fontSize: 12, color: 'var(--muted)' }}>
                    去附近宠物列表发起第一次碰头吧
                  </span>
                </div>
              </div>
            ) : (
              meets.map(meet => {
                const meta = MEET_STATUS_META[meet.status] || MEET_STATUS_META.pending
                const isInitiator = true // 简化：当前用户视角
                return (
                  <div key={meet.id} className="alarm-card">
                    <div className="alarm-card-head">
                      <div className="alarm-icon">🤝</div>
                      <div className="alarm-main">
                        <div className="alarm-title">碰头 #{meet.id}</div>
                        <div className="alarm-time">{formatTime(meet.created_at)}</div>
                      </div>
                      <span className={`badge ${meta.cls}`}>{meta.label}</span>
                    </div>

                    <div className="alarm-meta">
                      <span>🎁 奖励 {meet.points_awarded} 积分</span>
                      {meet.confirmed_at && <span>✅ 已确认 {formatTime(meet.confirmed_at)}</span>}
                      {meet.completed_at && <span>🏁 完成 {formatTime(meet.completed_at)}</span>}
                    </div>

                    {meet.status === 'pending' && !isInitiator && (
                      <div className="alarm-actions">
                        <button
                          className="btn btn-outline alarm-btn"
                          onClick={() => cancelMeet(meet.id)}
                          disabled={actingId === meet.id}
                        >
                          拒绝
                        </button>
                        <button
                          className="btn btn-primary alarm-btn"
                          onClick={() => confirmMeet(meet.id)}
                          disabled={actingId === meet.id}
                        >
                          {actingId === meet.id ? '...' : '确认碰头'}
                        </button>
                      </div>
                    )}

                    {meet.status === 'confirmed' && (
                      <div className="alarm-actions">
                        <button
                          className="btn btn-outline alarm-btn"
                          onClick={() => cancelMeet(meet.id)}
                          disabled={actingId === meet.id}
                        >
                          取消
                        </button>
                        <button
                          className="btn btn-primary alarm-btn"
                          onClick={() => completeMeet(meet.id)}
                          disabled={actingId === meet.id}
                        >
                          {actingId === meet.id ? '...' : '完成碰头领积分'}
                        </button>
                      </div>
                    )}
                  </div>
                )
              })
            )}
          </>
        )}
      </div>
    </div>
  )
}
