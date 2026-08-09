/**
 * S2 — 地图首页
 * 展示宠物实时位置，WebSocket 实时更新
 */
import React, { useState, useEffect, useRef } from 'react'
import { api } from '../api/client'
import { wsClient, WsMessage } from '../ws/websocket'
import { showToast } from '../utils/toast'
import { IS_DEV } from '../env'

interface PetInfo {
  id: number
  name: string
  type: string
  breed: string | null
  fence_enabled: boolean
  fence_radius: number
}

interface LocationData {
  lat: number | null
  lng: number | null
  battery: number
  source: string
  ts: number
}

export function MapHomePage({
  onNavigateAddPet,
  onNavigateBindDevice,
  onNavigateAlarms
}: {
  onNavigateAddPet: () => void
  onNavigateBindDevice: () => void
  onNavigateAlarms: () => void
}) {
  const [pets, setPets] = useState<PetInfo[]>([])
  const [selectedPet, setSelectedPet] = useState<PetInfo | null>(null)
  const [location, setLocation] = useState<LocationData>({ lat: null, lng: null, battery: 0, source: 'none', ts: 0 })
  const [loading, setLoading] = useState(true)
  const [wsConnected, setWsConnected] = useState(false)
  const [simulating, setSimulating] = useState(false)
  const mapRef = useRef<HTMLDivElement>(null)

  // 加载宠物列表
  const loadPets = async () => {
    try {
      const resp = await api.pets.list()
      const list = resp.data || []
      setPets(list)
      if (list.length > 0 && !selectedPet) {
        setSelectedPet(list[0])
      }
    } catch (e: any) {
      showToast(e.message)
    } finally {
      setLoading(false)
    }
  }

  // 获取实时位置
  const fetchRealtime = async (petId: number) => {
    try {
      const resp = await api.location.realtime(petId)
      if (resp.code === 0 && resp.data) {
        setLocation({
          lat: resp.data.lat,
          lng: resp.data.lng,
          battery: resp.data.battery || 0,
          source: resp.data.source || 'none',
          ts: resp.data.ts || 0
        })
      }
    } catch (e) {
      // 静默处理
    }
  }

  useEffect(() => {
    loadPets()
  }, [])

  // 选中宠物时：获取位置 + WebSocket 订阅
  useEffect(() => {
    if (!selectedPet) return

    // 获取初始位置
    fetchRealtime(selectedPet.id)

    // WebSocket 订阅位置更新
    wsClient.subscribeLocation(selectedPet.id)

    // 定时轮询兜底（每 30 秒）
    const timer = setInterval(() => fetchRealtime(selectedPet.id), 30_000)

    return () => clearInterval(timer)
  }, [selectedPet])

  // WebSocket 消息监听
  useEffect(() => {
    const unsub = wsClient.onMessage((msg: WsMessage) => {
      if (msg.type === 'connected') {
        setWsConnected(true)
        // 重新订阅当前宠物
        if (selectedPet) wsClient.subscribeLocation(selectedPet.id)
        wsClient.subscribeAlarm()
      } else if (msg.type === 'location' && selectedPet && msg.pet_id === selectedPet.id) {
        setLocation({
          lat: msg.lat,
          lng: msg.lng,
          battery: msg.battery,
          source: msg.source,
          ts: msg.ts
        })
      } else if (msg.type === 'alarm') {
        showToast(`⚠️ 报警：${msg.alarm_type}`)
      }
    })
    return unsub
  }, [selectedPet])

  // ── 模拟定位上报（开发测试用）────────────────────
  const simulateLocation = async () => {
    if (!selectedPet) {
      showToast('请先添加宠物')
      return
    }

    // 获取设备
    try {
      const deviceResp = await api.devices.list()
      const devices = deviceResp.data || []
      if (devices.length === 0) {
        showToast('请先绑定设备')
        onNavigateBindDevice()
        return
      }

      const device = devices[0]
      setSimulating(true)

      // 模拟郑州附近坐标移动
      const baseLat = 34.7466
      const baseLng = 113.6253
      let step = 0

      showToast('开始模拟定位上报...')

      const simTimer = setInterval(async () => {
        step++
        const lat = baseLat + (Math.random() - 0.5) * 0.001 * step
        const lng = baseLng + (Math.random() - 0.5) * 0.001 * step

        try {
          await api.location.upload({
            device_id: device.id,
            lat,
            lng,
            accuracy: 5.0 + Math.random() * 10,
            battery: Math.max(20, 100 - step),
            source: 'gps',
            ts: Math.floor(Date.now() / 1000)
          })
        } catch (e) {
          // 静默
        }

        if (step >= 20) {
          clearInterval(simTimer)
          setSimulating(false)
          showToast('模拟上报完成')
        }
      }, 2000)
    } catch (e: any) {
      showToast(e.message)
      setSimulating(false)
    }
  }

  // ── 渲染 ────────────────────────────────
  if (loading) {
    return (
      <div className="screen">
        <div className="nav-bar">🐾 宠迹</div>
        <div className="loading"><div className="spinner" /> 加载中...</div>
      </div>
    )
  }

  return (
    <div className="screen" style={{ paddingBottom: 83 }}>
      {/* 导航栏 */}
      <div className="nav-bar">
        🐾 宠迹
        {IS_DEV && (
          <span style={{
            position: 'absolute', left: 72, fontSize: 10, fontWeight: 600,
            color: '#fff', background: '#f59e0b', padding: '2px 6px', borderRadius: 4,
            letterSpacing: 1
          }}>
            DEV
          </span>
        )}
        <button
          onClick={onNavigateAlarms}
          style={{
            position: 'absolute', right: 16, background: 'none', border: 'none',
            fontSize: 20, cursor: 'pointer', padding: 0, lineHeight: 1
          }}
          title="报警记录"
        >
          🔔
        </button>
        <span style={{ position: 'absolute', right: 44, fontSize: 12, color: wsConnected ? 'var(--success)' : 'var(--muted)' }}>
          {wsConnected ? '●' : '○'}
        </span>
      </div>

      {/* 地图区域 */}
      <div className="map-container" ref={mapRef} style={{ height: 'calc(100vh - 83px - 200px - 56px)', minHeight: 300 }}>
        <MapCanvas lat={location.lat} lng={location.lng} petType={selectedPet?.type || 'dog'} />
      </div>

      {/* 宠物选择栏 */}
      {pets.length > 0 ? (
        <div style={{
          display: 'flex', gap: 8, padding: '12px 16px',
          overflowX: 'auto', background: 'var(--card)',
          borderBottom: '1px solid var(--border)'
        }}>
          {pets.map(pet => (
            <button
              key={pet.id}
              onClick={() => setSelectedPet(pet)}
              style={{
                display: 'flex', alignItems: 'center', gap: 6,
                padding: '8px 14px', borderRadius: 20, border: 'none',
                cursor: 'pointer', whiteSpace: 'nowrap', fontSize: 13, fontWeight: 600,
                background: selectedPet?.id === pet.id ? 'var(--primary)' : 'var(--bg)',
                color: selectedPet?.id === pet.id ? '#FFF' : 'var(--text)'
              }}
            >
              {pet.type === 'cat' ? '🐱' : '🐶'} {pet.name}
            </button>
          ))}
        </div>
      ) : null}

      {/* 位置信息卡片 */}
      <div className="card" style={{ margin: '12px 16px' }}>
        {selectedPet ? (
          <>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div className="pet-avatar" style={{
                  width: 40, height: 40, fontSize: 20,
                  background: selectedPet.type === 'cat' ? '#FFF7ED' : '#EFF6FF'
                }}>
                  {selectedPet.type === 'cat' ? '🐱' : '🐶'}
                </div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 16 }}>{selectedPet.name}</div>
                  <div style={{ fontSize: 12, color: 'var(--sub)' }}>
                    {selectedPet.breed || (selectedPet.type === 'cat' ? '猫咪' : '狗狗')}
                  </div>
                </div>
              </div>
              <span className={`badge ${location.source !== 'none' ? 'badge-online' : 'badge-offline'}`}>
                {location.source !== 'none' ? '● 在线' : '○ 离线'}
              </span>
            </div>

            <div style={{ display: 'flex', gap: 16, fontSize: 13, color: 'var(--sub)' }}>
              <div>
                <span style={{ color: 'var(--text)', fontWeight: 600 }}>
                  {location.lat ? location.lat.toFixed(6) : '--'}
                </span>
                , 
                <span style={{ color: 'var(--text)', fontWeight: 600 }}>
                  {location.lng ? location.lng.toFixed(6) : '--'}
                </span>
              </div>
              <div>🔋 {location.battery}%</div>
              <div>📡 {location.source}</div>
            </div>

            {selectedPet.fence_enabled && (
              <div style={{ marginTop: 8, fontSize: 12, color: 'var(--success)' }}>
                🛡️ 安全围栏已开启 · 半径 {selectedPet.fence_radius}m
              </div>
            )}

            {/* 模拟上报按钮（开发测试） */}
            <button
              className="btn btn-outline"
              onClick={simulateLocation}
              disabled={simulating}
              style={{ marginTop: 12, fontSize: 14, padding: '10px' }}
            >
              {simulating ? '📍 模拟上报中...' : '📍 模拟定位上报（测试）'}
            </button>
          </>
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">🐾</div>
            <div className="empty-state-text">
              还没有添加宠物
              <br />
              <button
                onClick={onNavigateAddPet}
                style={{
                  color: 'var(--primary)', border: 'none', background: 'none',
                  fontSize: 14, cursor: 'pointer', marginTop: 8, fontWeight: 600
                }}
              >+ 添加第一只宠物</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// ── 地图画布组件（纯 CSS 模拟） ─────────────────────────

function MapCanvas({ lat, lng, petType }: { lat: number | null; lng: number | null; petType: string }) {
  const [pinPos, setPinPos] = useState({ x: 50, y: 50 })

  useEffect(() => {
    if (lat && lng) {
      // 根据经纬度微调 Pin 位置（模拟移动效果）
      setPinPos({
        x: 50 + ((lng * 1000) % 30) - 15,
        y: 50 + ((lat * 1000) % 30) - 15
      })
    }
  }, [lat, lng])

  return (
    <div className="map-placeholder">
      <div className="map-grid" />
      {/* 中心圆圈表示围栏 */}
      <div style={{
        position: 'absolute',
        left: '50%', top: '50%',
        transform: 'translate(-50%, -50%)',
        width: 120, height: 120,
        borderRadius: '50%',
        border: '2px dashed rgba(59,130,246,0.3)',
        background: 'rgba(59,130,246,0.05)'
      }} />
      {/* 宠物位置 Pin */}
      {lat && lng && (
        <div
          className="map-pin"
          style={{
            left: `${pinPos.x}%`,
            top: `${pinPos.y}%`,
            background: petType === 'cat' ? 'var(--cat)' : 'var(--dog)',
            width: 16, height: 16,
            transform: 'translate(-50%, -50%)',
            transition: 'all 1s ease'
          }}
        />
      )}
      {/* 坐标显示 */}
      <div style={{
        position: 'absolute', bottom: 12, left: 12,
        background: 'rgba(255,255,255,0.9)', padding: '6px 12px',
        borderRadius: 8, fontSize: 12, color: 'var(--sub)'
      }}>
        {lat && lng ? `${lat.toFixed(4)}, ${lng.toFixed(4)}` : '等待定位...'}
      </div>
    </div>
  )
}
