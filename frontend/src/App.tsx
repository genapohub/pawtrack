/**
 * 宠迹 PawTrack — App 主组件
 * 管理页面路由和认证状态
 */
import React, { useState, useEffect } from 'react'
import { isLoggedIn, clearAuth, getUser } from './api/client'
import { wsClient } from './ws/websocket'
import { LoginPage } from './pages/LoginPage'
import { MapHomePage } from './pages/MapHomePage'
import { AddPetPage } from './pages/AddPetPage'
import { BindDevicePage } from './pages/BindDevicePage'
import { AlarmsPage } from './pages/AlarmsPage'
import { SocialPage } from './pages/SocialPage'
import { MembershipPage } from './pages/MembershipPage'
import { PointsPage } from './pages/PointsPage'
import { TabBar, TabKey } from './components/TabBar'

type Page = 'login' | 'home' | 'addPet' | 'bindDevice' | 'petList' | 'me' | 'social' | 'alarms' | 'membership' | 'points'

export default function App() {
  const [authed, setAuthed] = useState(isLoggedIn())
  const [page, setPage] = useState<Page>('home')
  const [tab, setTab] = useState<TabKey>('home')
  const [refreshKey, setRefreshKey] = useState(0)

  // 登录成功回调
  const handleLoginSuccess = () => {
    setAuthed(true)
    setPage('home')
    setTab('home')
    wsClient.connect()
  }

  // 退出登录
  const handleLogout = () => {
    clearAuth()
    wsClient.disconnect()
    setAuthed(false)
  }

  // Tab 切换
  const handleTabChange = (newTab: TabKey) => {
    setTab(newTab)
    switch (newTab) {
      case 'home': setPage('home'); break
      case 'pets': setPage('petList'); break
      case 'social': setPage('social'); break
      case 'device': setPage('bindDevice'); break
      case 'me': setPage('me'); break
    }
  }

  // WebSocket 连接（已登录时）
  useEffect(() => {
    if (authed) {
      wsClient.connect()
    }
    return () => {
      // 组件卸载时不断开，保持连接
    }
  }, [authed])

  // ── 未登录 → 登录页 ─────────────────────────
  if (!authed) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />
  }

  // ── 页面渲染 ────────────────────────────────
  const user = getUser()

  return (
    <>
      {/* 状态栏 */}
      <div className="status-bar">
        <span>9:41</span>
        <span>🐾 宠迹</span>
        <span>100%</span>
      </div>

      {/* 页面内容 */}
      {page === 'home' && (
        <MapHomePage
          key={`home-${refreshKey}`}
          onNavigateAddPet={() => { setPage('addPet'); setTab('pets') }}
          onNavigateBindDevice={() => { setPage('bindDevice'); setTab('device') }}
          onNavigateAlarms={() => setPage('alarms')}
        />
      )}

      {page === 'addPet' && (
        <AddPetPage
          onBack={() => { setPage('petList'); setTab('pets') }}
          onSuccess={() => { setPage('petList'); setTab('pets'); setRefreshKey(k => k + 1) }}
        />
      )}

      {page === 'petList' && (
        <PetListPage
          onAddPet={() => setPage('addPet')}
          onBack={() => { setPage('home'); setTab('home') }}
        />
      )}

      {page === 'bindDevice' && (
        <BindDevicePage
          onBack={() => { setPage('home'); setTab('home') }}
          onSuccess={() => { setPage('home'); setTab('home'); setRefreshKey(k => k + 1) }}
        />
      )}

      {page === 'social' && <SocialPage />}

      {page === 'alarms' && (
        <AlarmsPage onBack={() => { setPage('home'); setTab('home') }} />
      )}

      {page === 'membership' && (
        <MembershipPage onBack={() => setPage('me')} />
      )}

      {page === 'points' && (
        <PointsPage onBack={() => setPage('me')} />
      )}

      {page === 'me' && (
        <MePage
          user={user}
          onLogout={handleLogout}
          onNavigateMembership={() => setPage('membership')}
          onNavigatePoints={() => setPage('points')}
          onNavigateAlarms={() => setPage('alarms')}
          onNavigateSocial={() => { setPage('social'); setTab('social') }}
        />
      )}

      {/* TabBar（登录页、添加宠物、子页面不显示） */}
      {['home', 'petList', 'social', 'bindDevice', 'me'].includes(page) && (
        <TabBar active={tab} onChange={handleTabChange} />
      )}

      {/* 添加宠物 FAB */}
      {page === 'petList' && (
        <button
          className="fab"
          style={{ right: 'calc(50% - 207px + 20px)' }}
          onClick={() => setPage('addPet')}
        >
          +
        </button>
      )}
    </>
  )
}

// ── 宠物列表页（内联） ─────────────────────────
import { api } from './api/client'
import { showToast } from './utils/toast'

function PetListPage({ onAddPet, onBack }: { onAddPet: () => void; onBack: () => void }) {
  const [pets, setPets] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const loadPets = async () => {
    try {
      const resp = await api.pets.list()
      setPets(resp.data || [])
    } catch (e: any) {
      showToast(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadPets() }, [])

  return (
    <div className="screen">
      <div className="nav-bar">
        <button className="nav-back" onClick={onBack}>‹</button>
        我的宠物
      </div>
      <div style={{ padding: '16px' }}>
        {loading ? (
          <div className="loading"><div className="spinner" /> 加载中...</div>
        ) : pets.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">🐾</div>
            <div className="empty-state-text">还没有添加宠物<br/>点击右下角 + 添加</div>
          </div>
        ) : (
          pets.map(pet => (
            <div key={pet.id} className="pet-card">
              <div className="pet-avatar" style={{
                background: pet.type === 'cat' ? '#FFF7ED' : '#EFF6FF'
              }}>
                {pet.type === 'cat' ? '🐱' : '🐶'}
              </div>
              <div className="pet-info">
                <div className="pet-name">{pet.name}</div>
                <div className="pet-status">
                  {pet.breed || (pet.type === 'cat' ? '猫咪' : '狗狗')} ·
                  围栏{pet.fence_enabled ? '已开启' : '已关闭'}
                </div>
              </div>
              <span className={`badge ${pet.type === 'cat' ? 'badge-cat' : 'badge-dog'}`}>
                {pet.type === 'cat' ? '猫' : '狗'}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

// ── 我的页面（内联） ─────────────────────────
function MePage({
  user,
  onLogout,
  onNavigateMembership,
  onNavigatePoints,
  onNavigateAlarms,
  onNavigateSocial
}: {
  user: any
  onLogout: () => void
  onNavigateMembership: () => void
  onNavigatePoints: () => void
  onNavigateAlarms: () => void
  onNavigateSocial: () => void
}) {
  return (
    <div className="screen">
      <div className="nav-bar">我的</div>
      <div style={{ padding: '20px 16px', textAlign: 'center' }}>
        <div style={{
          width: 80, height: 80, borderRadius: '50%',
          background: '#EFF6FF', margin: '0 auto 12px',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 40
        }}>👤</div>
        <div style={{ fontSize: 20, fontWeight: 700 }}>
          {user?.nickname || '用户'}
        </div>
        <div style={{ fontSize: 14, color: 'var(--sub)', marginTop: 4 }}>
          {user?.phone || '未绑定手机号'}
        </div>
        <span className={`badge ${user?.member_level === 'pro' ? 'badge-pro' : 'badge-offline'}`} style={{ marginTop: 8 }}>
          {user?.member_level === 'free' ? '免费版' : user?.member_level === 'basic' ? '基础版' : 'Pro版'}
        </span>
      </div>

      <div className="card">
        <div className="me-row" onClick={onNavigateAlarms}>
          <span>🔔 报警记录</span>
          <span style={{ color: 'var(--muted)' }}>›</span>
        </div>
        <div className="me-row" onClick={onNavigateSocial}>
          <span>🤝 社交碰头</span>
          <span style={{ color: 'var(--muted)' }}>›</span>
        </div>
        <div className="me-row" onClick={onNavigateMembership}>
          <span>💎 会员订阅</span>
          <span style={{ color: 'var(--muted)' }}>›</span>
        </div>
        <div className="me-row" onClick={onNavigatePoints}>
          <span>🎁 我的积分</span>
          <span style={{ color: 'var(--muted)' }}>›</span>
        </div>
        <div className="me-row" style={{ borderBottom: 'none' }}>
          <span>⚙️ 设置</span>
          <span style={{ color: 'var(--muted)' }}>›</span>
        </div>
      </div>

      <div style={{ padding: '16px' }}>
        <button className="btn btn-outline" onClick={onLogout}>退出登录</button>
      </div>
    </div>
  )
}
