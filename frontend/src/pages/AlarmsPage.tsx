/**
 * S5 — 报警列表页
 * 报警记录列表、按状态筛选、处理/标记误报
 */
import React, { useState, useEffect } from 'react'
import { api } from '../api/client'
import { wsClient, WsMessage } from '../ws/websocket'
import { showToast } from '../utils/toast'

interface AlarmItem {
  id: number
  pet_id: number
  device_id: number | null
  type: string
  severity: string
  lat: number | null
  lng: number | null
  address: string | null
  status: string
  handled_at: string | null
  created_at: string
}

const ALARM_META: Record<string, { icon: string; label: string }> = {
  leave_fence: { icon: '🚪', label: '离开围栏' },
  leave_fence_cat: { icon: '🚪', label: '猫咪离开围栏' },
  enter_fence: { icon: '📍', label: '进入围栏' },
  low_battery: { icon: '🔋', label: '电量偏低' },
  low_battery_critical: { icon: '🪫', label: '电量严重不足' },
  offline_warning: { icon: '📵', label: '设备离线' },
  tamper_detected: { icon: '⚠️', label: '设备拆卸' },
  fall_detected: { icon: '💥', label: '跌落检测' },
  meet_request: { icon: '🤝', label: '碰头请求' }
}

const SEVERITY_META: Record<string, { label: string; cls: string }> = {
  high: { label: '高', cls: 'sev-high' },
  medium: { label: '中', cls: 'sev-medium' },
  low: { label: '低', cls: 'sev-low' }
}

const STATUS_TABS: { key: string; label: string }[] = [
  { key: 'active', label: '待处理' },
  { key: 'handled', label: '已处理' },
  { key: 'false_positive', label: '误报' },
  { key: '', label: '全部' }
]

export function AlarmsPage({ onBack }: { onBack: () => void }) {
  const [alarms, setAlarms] = useState<AlarmItem[]>([])
  const [statusTab, setStatusTab] = useState('active')
  const [loading, setLoading] = useState(true)
  const [unread, setUnread] = useState(0)
  const [handlingId, setHandlingId] = useState<number | null>(null)

  const loadAlarms = async (status: string) => {
    setLoading(true)
    try {
      const resp = await api.alarms.list({ status: status || undefined, page: 1, size: 50 })
      setAlarms(resp.data || [])
    } catch (e: any) {
      showToast(e.message)
    } finally {
      setLoading(false)
    }
  }

  const loadUnread = async () => {
    try {
      const resp = await api.alarms.unreadCount()
      setUnread(resp.data?.count || 0)
    } catch {
      // 静默
    }
  }

  useEffect(() => {
    loadAlarms(statusTab)
    loadUnread()
  }, [statusTab])

  // WebSocket 实时接收新报警
  useEffect(() => {
    const unsub = wsClient.onMessage((msg: WsMessage) => {
      if (msg.type === 'alarm') {
        showToast(`⚠️ 新报警：${ALARM_META[msg.alarm_type]?.label || msg.alarm_type}`)
        loadAlarms(statusTab)
        loadUnread()
      }
    })
    return unsub
  }, [statusTab])

  const handleAlarm = async (id: number, status: 'handled' | 'false_positive') => {
    setHandlingId(id)
    try {
      await api.alarms.handle(id, status)
      showToast(status === 'handled' ? '已确认处理' : '已标记为误报')
      loadAlarms(statusTab)
      loadUnread()
    } catch (e: any) {
      showToast(e.message)
    } finally {
      setHandlingId(null)
    }
  }

  const formatTime = (iso: string) => {
    if (!iso) return ''
    const d = new Date(iso)
    const now = new Date()
    const diff = (now.getTime() - d.getTime()) / 1000
    if (diff < 60) return '刚刚'
    if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
    if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
    return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="screen">
      <div className="nav-bar">
        <button className="nav-back" onClick={onBack}>‹</button>
        报警记录
        {unread > 0 && (
          <span className="nav-badge">{unread > 99 ? '99+' : unread}</span>
        )}
      </div>

      {/* 状态筛选 */}
      <div className="filter-bar">
        {STATUS_TABS.map(t => (
          <button
            key={t.key || 'all'}
            className={`filter-tab ${statusTab === t.key ? 'active' : ''}`}
            onClick={() => setStatusTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* 列表 */}
      <div style={{ padding: '12px 16px 83px' }}>
        {loading ? (
          <div className="loading"><div className="spinner" /> 加载中...</div>
        ) : alarms.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">🔔</div>
            <div className="empty-state-text">
              {statusTab === 'active' ? '暂无待处理报警' : '暂无报警记录'}
            </div>
          </div>
        ) : (
          alarms.map(alarm => {
            const meta = ALARM_META[alarm.type] || { icon: '🔔', label: alarm.type }
            const sev = SEVERITY_META[alarm.severity] || SEVERITY_META.medium
            return (
              <div key={alarm.id} className="alarm-card">
                <div className="alarm-card-head">
                  <div className="alarm-icon">{meta.icon}</div>
                  <div className="alarm-main">
                    <div className="alarm-title">{meta.label}</div>
                    <div className="alarm-time">{formatTime(alarm.created_at)}</div>
                  </div>
                  <span className={`severity ${sev.cls}`}>{sev.label}</span>
                </div>

                {alarm.lat && alarm.lng && (
                  <div className="alarm-meta">
                    <span>📍 {alarm.lat.toFixed(5)}, {alarm.lng.toFixed(5)}</span>
                    {alarm.address && <span className="alarm-addr">{alarm.address}</span>}
                  </div>
                )}

                <div className="alarm-status-row">
                  <span className={`badge ${
                    alarm.status === 'active' ? 'badge-offline' :
                    alarm.status === 'false_positive' ? 'badge-cat' : 'badge-online'
                  }`}>
                    {alarm.status === 'active' ? '待处理' :
                     alarm.status === 'false_positive' ? '误报' : '已处理'}
                  </span>
                </div>

                {alarm.status === 'active' && (
                  <div className="alarm-actions">
                    <button
                      className="btn btn-outline alarm-btn"
                      onClick={() => handleAlarm(alarm.id, 'false_positive')}
                      disabled={handlingId === alarm.id}
                    >
                      误报
                    </button>
                    <button
                      className="btn btn-primary alarm-btn"
                      onClick={() => handleAlarm(alarm.id, 'handled')}
                      disabled={handlingId === alarm.id}
                    >
                      {handlingId === alarm.id ? '处理中...' : '确认处理'}
                    </button>
                  </div>
                )}
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
