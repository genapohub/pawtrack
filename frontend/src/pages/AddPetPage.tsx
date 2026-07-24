/**
 * S3 — 添加宠物页
 */
import React, { useState } from 'react'
import { api } from '../api/client'
import { showToast } from '../utils/toast'

export function AddPetPage({
  onBack,
  onSuccess
}: {
  onBack: () => void
  onSuccess: () => void
}) {
  const [petType, setPetType] = useState<'cat' | 'dog'>('dog')
  const [name, setName] = useState('')
  const [breed, setBreed] = useState('')
  const [gender, setGender] = useState<'male' | 'female' | 'unknown'>('unknown')
  const [birthday, setBirthday] = useState('')
  const [weight, setWeight] = useState('')
  const [fenceEnabled, setFenceEnabled] = useState(true)
  const [loading, setLoading] = useState(false)

  // 品种选项
  const breeds = petType === 'cat'
    ? ['中华田园猫', '英短', '美短', '布偶', '暹罗', '橘猫', '狸花猫', '其他']
    : ['中华田园犬', '金毛', '拉布拉多', '哈士奇', '柯基', '泰迪', '边牧', '其他']

  const handleSubmit = async () => {
    if (!name.trim()) {
      showToast('请输入宠物名字')
      return
    }

    setLoading(true)
    try {
      const resp = await api.pets.create({
        name: name.trim(),
        pet_type: petType,
        breed: breed || undefined,
        gender,
        birthday: birthday || undefined,
        weight: weight ? parseFloat(weight) : undefined,
        fence_enabled: fenceEnabled,
        fence_radius: petType === 'cat' ? 100 : 300
      })

      if (resp.code === 0) {
        showToast('添加成功！')
        onSuccess()
      }
    } catch (e: any) {
      showToast(e.message || '添加失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="screen" style={{ paddingBottom: 0 }}>
      <div className="nav-bar">
        <button className="nav-back" onClick={onBack}>‹</button>
        添加宠物
        <button className="nav-right" onClick={handleSubmit} disabled={loading}>
          {loading ? '...' : '完成'}
        </button>
      </div>

      {/* 类型选择 */}
      <div style={{ padding: '20px 16px 0' }}>
        <div className="input-label" style={{ marginBottom: 12 }}>选择宠物类型</div>
        <div className="type-selector">
          <div
            className={`type-option ${petType === 'dog' ? 'selected' : ''}`}
            onClick={() => setPetType('dog')}
          >
            <div className="type-option-icon">🐶</div>
            <div className="type-option-label">狗狗</div>
          </div>
          <div
            className={`type-option ${petType === 'cat' ? 'selected' : ''}`}
            onClick={() => setPetType('cat')}
          >
            <div className="type-option-icon">🐱</div>
            <div className="type-option-label">猫咪</div>
          </div>
        </div>
      </div>

      <div style={{ padding: '0 16px' }}>
        {/* 名字 */}
        <div className="input-group">
          <div className="input-label">宠物名字 *</div>
          <input
            className="input"
            type="text"
            placeholder="给TA起个名字"
            value={name}
            onChange={e => setName(e.target.value)}
            maxLength={20}
          />
        </div>

        {/* 品种 */}
        <div className="input-group">
          <div className="input-label">品种</div>
          <select
            className="input"
            value={breed}
            onChange={e => setBreed(e.target.value)}
            style={{ appearance: 'none', cursor: 'pointer' }}
          >
            <option value="">请选择品种</option>
            {breeds.map(b => <option key={b} value={b}>{b}</option>)}
          </select>
        </div>

        {/* 性别 */}
        <div className="input-group">
          <div className="input-label">性别</div>
          <div style={{ display: 'flex', gap: 8 }}>
            {[
              { val: 'male', label: '♂ 公', icon: '👦' },
              { val: 'female', label: '♀ 母', icon: '👧' },
              { val: 'unknown', label: '? 未知', icon: '❓' }
            ].map(g => (
              <button
                key={g.val}
                onClick={() => setGender(g.val as any)}
                style={{
                  flex: 1, padding: '12px', borderRadius: 12, border: 'none',
                  cursor: 'pointer', fontSize: 14, fontWeight: 600,
                  background: gender === g.val ? 'var(--primary)' : 'var(--bg)',
                  color: gender === g.val ? '#FFF' : 'var(--sub)'
                }}
              >
                {g.label}
              </button>
            ))}
          </div>
        </div>

        {/* 生日 */}
        <div className="input-group">
          <div className="input-label">生日</div>
          <input
            className="input"
            type="date"
            value={birthday}
            onChange={e => setBirthday(e.target.value)}
          />
        </div>

        {/* 体重 */}
        <div className="input-group">
          <div className="input-label">体重 (kg)</div>
          <input
            className="input"
            type="number"
            placeholder="如 5.5"
            value={weight}
            onChange={e => setWeight(e.target.value)}
            step="0.1"
            min="0"
            max="100"
          />
        </div>

        {/* 围栏开关 */}
        <div className="card" style={{ margin: '12px 0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontWeight: 600, fontSize: 15 }}>🛡️ 安全围栏</div>
            <div style={{ fontSize: 12, color: 'var(--sub)', marginTop: 4 }}>
              {petType === 'cat' ? '猫咪默认 100m' : '狗狗默认 300m'} · 离开范围时报警
            </div>
          </div>
          <button
            className={`toggle ${fenceEnabled ? 'on' : ''}`}
            onClick={() => setFenceEnabled(!fenceEnabled)}
          >
            <div className="toggle-dot" />
          </button>
        </div>

        {/* 提示 */}
        <div style={{ padding: '16px 0', fontSize: 12, color: 'var(--muted)', textAlign: 'center' }}>
          添加宠物后可在设备页绑定定位器
        </div>
      </div>
    </div>
  )
}
