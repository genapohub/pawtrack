/**
 * S4 — 绑定设备页
 */
import React, { useState, useEffect } from 'react'
import { api } from '../api/client'
import { showToast } from '../utils/toast'

export function BindDevicePage({
  onBack,
  onSuccess
}: {
  onBack: () => void
  onSuccess: () => void
}) {
  const [mode, setMode] = useState<'bind' | 'register'>('bind')
  const [sn, setSn] = useState('')
  const [activationCode, setActivationCode] = useState('')
  const [hwType, setHwType] = useState<'cat' | 'dog'>('dog')
  const [selectedPetId, setSelectedPetId] = useState<number | null>(null)
  const [pets, setPets] = useState<any[]>([])
  const [devices, setDevices] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  // 加载宠物和设备列表
  useEffect(() => {
    loadPets()
    loadDevices()
  }, [])

  const loadPets = async () => {
    try {
      const resp = await api.pets.list()
      const list = resp.data || []
      setPets(list)
      if (list.length > 0) setSelectedPetId(list[0].id)
    } catch (e) {
      // 静默
    }
  }

  const loadDevices = async () => {
    try {
      const resp = await api.devices.list()
      setDevices(resp.data || [])
    } catch (e) {
      // 静默
    }
  }

  // 注册新设备
  const handleRegister = async () => {
    if (sn.length < 8) {
      showToast('设备序列号至少 8 位')
      return
    }
    if (activationCode.length < 8) {
      showToast('激活码至少 8 位')
      return
    }

    setLoading(true)
    try {
      const resp = await api.devices.register(sn, activationCode, hwType)
      if (resp.code === 0) {
        showToast('设备注册成功！')
        // 切换到绑定模式
        setMode('bind')
        loadDevices()
      }
    } catch (e: any) {
      showToast(e.message || '注册失败')
    } finally {
      setLoading(false)
    }
  }

  // 绑定设备到宠物
  const handleBind = async () => {
    if (!sn.trim()) {
      showToast('请输入设备序列号')
      return
    }
    if (!selectedPetId) {
      showToast('请先添加宠物')
      return
    }

    setLoading(true)
    try {
      const resp = await api.devices.bind(sn.trim(), selectedPetId)
      if (resp.code === 0) {
        showToast('绑定成功！')
        onSuccess()
      }
    } catch (e: any) {
      showToast(e.message || '绑定失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="screen" style={{ paddingBottom: 0 }}>
      <div className="nav-bar">
        <button className="nav-back" onClick={onBack}>‹</button>
        设备管理
      </div>

      {/* 已绑定设备列表 */}
      {devices.length > 0 && (
        <>
          <div className="section-title">已绑定设备</div>
          <div style={{ padding: '0 16px' }}>
            {devices.map(d => (
              <div key={d.id} className="pet-card">
                <div className="pet-avatar" style={{
                  background: d.hardware_type === 'cat' ? '#FFF7ED' : '#EFF6FF'
                }}>
                  📡
                </div>
                <div className="pet-info">
                  <div className="pet-name">{d.sn}</div>
                  <div className="pet-status">
                    {d.hardware_type === 'cat' ? '猫咪版' : '狗狗版'} ·
                    🔋 {d.battery_level ?? 100}% ·
                    {d.status === 'online' ? ' ● 在线' : ' ○ 离线'}
                  </div>
                </div>
                <span className={`badge ${d.status === 'online' ? 'badge-online' : 'badge-offline'}`}>
                  {d.status === 'online' ? '在线' : '离线'}
                </span>
              </div>
            ))}
          </div>
        </>
      )}

      {/* 模式切换 */}
      <div style={{ display: 'flex', padding: '16px 16px 0', gap: 8 }}>
        <button
          onClick={() => setMode('bind')}
          style={{
            flex: 1, padding: '10px', borderRadius: 10,
            border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: 14,
            background: mode === 'bind' ? 'var(--primary)' : 'var(--border)',
            color: mode === 'bind' ? '#FFF' : 'var(--sub)'
          }}
        >绑定已有设备</button>
        <button
          onClick={() => setMode('register')}
          style={{
            flex: 1, padding: '10px', borderRadius: 10,
            border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: 14,
            background: mode === 'register' ? 'var(--primary)' : 'var(--border)',
            color: mode === 'register' ? '#FFF' : 'var(--sub)'
          }}
        >注册新设备</button>
      </div>

      <div style={{ padding: '20px 16px' }}>
        {mode === 'register' ? (
          <>
            {/* 注册新设备 */}
            <div className="input-group">
              <div className="input-label">设备序列号 (SN) *</div>
              <input
                className="input"
                type="text"
                placeholder="设备背面 SN 码"
                value={sn}
                onChange={e => setSn(e.target.value)}
                maxLength={32}
              />
            </div>

            <div className="input-group">
              <div className="input-label">激活码 *</div>
              <input
                className="input"
                type="text"
                placeholder="包装盒内激活码"
                value={activationCode}
                onChange={e => setActivationCode(e.target.value)}
                maxLength={32}
              />
            </div>

            <div className="input-group">
              <div className="input-label">设备类型</div>
              <div className="type-selector">
                <div
                  className={`type-option ${hwType === 'dog' ? 'selected' : ''}`}
                  onClick={() => setHwType('dog')}
                >
                  <div className="type-option-icon">🐶</div>
                  <div className="type-option-label">狗狗版</div>
                  <div style={{ fontSize: 10, color: 'var(--sub)', marginTop: 4 }}>GPS+4G</div>
                </div>
                <div
                  className={`type-option ${hwType === 'cat' ? 'selected' : ''}`}
                  onClick={() => setHwType('cat')}
                >
                  <div className="type-option-icon">🐱</div>
                  <div className="type-option-label">猫咪版</div>
                  <div style={{ fontSize: 10, color: 'var(--sub)', marginTop: 4 }}>BLE+WiFi</div>
                </div>
              </div>
            </div>

            <button
              className="btn btn-primary"
              onClick={handleRegister}
              disabled={loading}
              style={{ marginTop: 20 }}
            >
              {loading ? '注册中...' : '注册设备'}
            </button>

            <div style={{ marginTop: 16, padding: 12, background: '#FEF3C7', borderRadius: 12, fontSize: 12, color: '#92400E' }}>
              💡 提示：注册后设备将获得专用 JWT Token，用于 MQTT 连接上报定位数据
            </div>
          </>
        ) : (
          <>
            {/* 绑定已有设备 */}
            <div className="input-group">
              <div className="input-label">设备序列号 (SN) *</div>
              <input
                className="input"
                type="text"
                placeholder="输入已注册的设备 SN"
                value={sn}
                onChange={e => setSn(e.target.value)}
                maxLength={32}
              />
            </div>

            <div className="input-group">
              <div className="input-label">绑定到宠物 *</div>
              {pets.length === 0 ? (
                <div style={{
                  padding: '20px', textAlign: 'center',
                  background: 'var(--bg)', borderRadius: 12,
                  color: 'var(--muted)', fontSize: 13
                }}>
                  还没有宠物，请先添加宠物
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {pets.map(pet => (
                    <div
                      key={pet.id}
                      onClick={() => setSelectedPetId(pet.id)}
                      style={{
                        display: 'flex', alignItems: 'center', gap: 10,
                        padding: 12, borderRadius: 12, cursor: 'pointer',
                        border: `2px solid ${selectedPetId === pet.id ? 'var(--primary)' : 'var(--border)'}`,
                        background: selectedPetId === pet.id ? '#EFF6FF' : 'var(--card)'
                      }}
                    >
                      <div className="pet-avatar" style={{
                        width: 36, height: 36, fontSize: 18,
                        background: pet.type === 'cat' ? '#FFF7ED' : '#EFF6FF'
                      }}>
                        {pet.type === 'cat' ? '🐱' : '🐶'}
                      </div>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: 15 }}>{pet.name}</div>
                        <div style={{ fontSize: 12, color: 'var(--sub)' }}>{pet.breed || '未设置品种'}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <button
              className="btn btn-primary"
              onClick={handleBind}
              disabled={loading || !selectedPetId}
              style={{ marginTop: 20 }}
            >
              {loading ? '绑定中...' : '确认绑定'}
            </button>

            <div style={{ marginTop: 16, padding: 12, background: '#EFF6FF', borderRadius: 12, fontSize: 12, color: '#1E40AF' }}>
              💡 绑定后，设备上报的定位数据将关联到此宠物，App 首页可实时查看位置
            </div>
          </>
        )}
      </div>
    </div>
  )
}
