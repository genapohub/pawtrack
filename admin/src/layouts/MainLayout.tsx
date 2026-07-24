/**
 * 管理后台 — 主布局（侧边栏 + 顶栏 + 内容区）
 */
import { useState } from 'react'
import { Layout, Menu, theme, Avatar, Dropdown, Space, Tag } from 'antd'
import {
  DashboardOutlined, UserOutlined,
  ApiOutlined, BellOutlined, ShoppingCartOutlined, LogoutOutlined
} from '@ant-design/icons'
import type { MenuProps } from 'antd'
import { getAdminInfo, clearAuth } from '../api/client'
import { IS_DEV, APP_ENV } from '../env'

const { Header, Sider, Content } = Layout

const MENU_ITEMS: { key: string; label: string; icon: React.ReactNode }[] = [
  { key: 'dashboard', label: '数据概览', icon: <DashboardOutlined /> },
  { key: 'users', label: '用户管理', icon: <UserOutlined /> },
  { key: 'pets', label: '宠物管理', icon: <PetIcon /> },
  { key: 'devices', label: '设备管理', icon: <ApiOutlined /> },
  { key: 'alarms', label: '报警管理', icon: <BellOutlined /> },
  { key: 'orders', label: '订单管理', icon: <ShoppingCartOutlined /> }
]

function PetIcon() {
  return <span style={{ fontSize: 14 }}>🐾</span>
}

export default function MainLayout({
  active,
  onNavigate,
  onLogout,
  children
}: {
  active: string
  onNavigate: (key: string) => void
  onLogout: () => void
  children: React.ReactNode
}) {
  const [collapsed, setCollapsed] = useState(false)
  const { token: themeToken } = theme.useToken()
  const admin = getAdminInfo()

  const dropdownItems: MenuProps['items'] = [
    { key: 'logout', label: '退出登录', icon: <LogoutOutlined /> }
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed} theme="light">
        <div style={{
          height: 56, display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: themeToken.colorPrimary, fontWeight: 800, fontSize: collapsed ? 18 : 18,
          borderBottom: `1px solid ${themeToken.colorBorder}`
        }}>
          {collapsed ? '🐾' : '🐾 宠迹后台'}
        </div>
        <Menu
          mode="inline"
          selectedKeys={[active]}
          items={MENU_ITEMS}
          onClick={({ key }) => onNavigate(key)}
          style={{ borderRight: 0 }}
        />
      </Sider>
      <Layout>
        <Header style={{
          background: themeToken.colorBgContainer, padding: '0 24px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          borderBottom: `1px solid ${themeToken.colorBorder}`
        }}>
          <Tag color={IS_DEV ? 'orange' : 'red'} style={{ margin: 0, fontWeight: 600 }}>
            {IS_DEV ? 'DEV 开发环境' : `${APP_ENV.toUpperCase()} 生产环境`}
          </Tag>
          <Dropdown menu={{ items: dropdownItems, onClick: ({ key }) => key === 'logout' && onLogout() }}>
            <Space style={{ cursor: 'pointer' }}>
              <Avatar style={{ backgroundColor: themeToken.colorPrimary }} icon={<UserOutlined />} />
              <span>{admin?.username || 'admin'}</span>
            </Space>
          </Dropdown>
        </Header>
        <Content style={{ margin: 16, padding: 24, background: themeToken.colorBgContainer, borderRadius: 8, overflow: 'auto' }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  )
}
