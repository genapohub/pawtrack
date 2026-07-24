/**
 * 宠迹 PawTrack 管理后台 — 应用根组件
 */
import { useState } from 'react'
import { message } from 'antd'
import { isLoggedIn, clearAuth } from './api/client'
import LoginPage from './pages/Login'
import MainLayout from './layouts/MainLayout'
import DashboardPage from './pages/Dashboard'
import UsersPage from './pages/Users'
import PetsPage from './pages/Pets'
import DevicesPage from './pages/Devices'
import AlarmsPage from './pages/Alarms'
import OrdersPage from './pages/Orders'

const PAGE_MAP: Record<string, React.ReactNode> = {
  dashboard: <DashboardPage />,
  users: <UsersPage />,
  pets: <PetsPage />,
  devices: <DevicesPage />,
  alarms: <AlarmsPage />,
  orders: <OrdersPage />
}

export default function App() {
  const [authed, setAuthed] = useState(isLoggedIn())
  const [active, setActive] = useState('dashboard')

  if (!authed) {
    return <LoginPage onLoginSuccess={() => setAuthed(true)} />
  }

  const handleLogout = () => {
    clearAuth()
    setAuthed(false)
    message.success('已退出登录')
  }

  return (
    <MainLayout active={active} onNavigate={setActive} onLogout={handleLogout}>
      {PAGE_MAP[active] || <DashboardPage />}
    </MainLayout>
  )
}
