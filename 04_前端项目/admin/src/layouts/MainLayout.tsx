/**
 * 管理后台壳 — 对齐画布 205:1 侧栏与顶栏 Mock 口径
 */
import { Layout, Menu } from 'antd'
import {
  DashboardOutlined, UserOutlined, ApiOutlined, BellOutlined,
  TeamOutlined, ShoppingCartOutlined, SettingOutlined, AuditOutlined,
  AccountBookOutlined, GiftOutlined, FileTextOutlined
} from '@ant-design/icons'
import { getAdminInfo } from '../api/client'
import { USE_MOCK } from '../env'
import { PT } from '../styles/tokens'
import type { ReactNode } from 'react'

const { Header, Sider, Content } = Layout

const MENU_ITEMS = [
  { key: 'dashboard', label: '数据概览', icon: <DashboardOutlined /> },
  { key: 'devices', label: '设备', icon: <ApiOutlined /> },
  { key: 'alarms', label: '报警', icon: <BellOutlined /> },
  { key: 'users', label: '用户', icon: <UserOutlined /> },
  { key: 'pets', label: '宠物', icon: <TeamOutlined /> },
  { key: 'social', label: '社交审核', icon: <AuditOutlined /> },
  { key: 'pointsRule', label: '积分规则', icon: <GiftOutlined /> },
  { key: 'plans', label: '套餐', icon: <ShoppingCartOutlined /> },
  { key: 'orders', label: '订单', icon: <FileTextOutlined /> },
  { key: 'revenue', label: '收入', icon: <AccountBookOutlined /> },
  { key: 'content', label: '内容', icon: <FileTextOutlined /> },
  { key: 'system', label: '系统设置', icon: <SettingOutlined /> },
]

export default function MainLayout({
  active,
  onNavigate,
  onLogout,
  children
}: {
  active: string
  onNavigate: (key: string) => void
  onLogout: () => void
  children: ReactNode
}) {
  const admin = getAdminInfo()
  const siderSelected = ['userDetail'].includes(active) ? 'users'
    : ['deviceDetail'].includes(active) ? 'devices'
    : ['alarmRules'].includes(active) ? 'alarms'
    : active

  return (
    <Layout style={{ minHeight: '100vh', background: PT.bg }}>
      <Sider width={220} theme="dark" style={{
        background: PT.sidebar,
        borderRight: `1px solid ${PT.sidebarLine}`,
      }}>
        <div style={{
          padding: '20px 16px 16px',
          borderBottom: `1px solid ${PT.sidebarLine}`,
          display: 'flex',
          gap: 10,
          alignItems: 'center',
        }}>
          <div style={{
            width: 32, height: 32, borderRadius: 10,
            background: PT.accent, color: '#fff',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontWeight: 600, fontSize: 15, flexShrink: 0,
          }}>迹</div>
          <div>
            <div style={{ color: PT.fgInv, fontWeight: 600, fontSize: 14, lineHeight: 1.3 }}>宠迹管理端</div>
            <div style={{ color: PT.sidebarMuted, fontSize: 11, fontWeight: 400, marginTop: 2 }}>本地 Mock · 非验收</div>
          </div>
        </div>
        <Menu
          mode="inline"
          theme="dark"
          selectedKeys={[siderSelected]}
          items={MENU_ITEMS}
          onClick={({ key }) => onNavigate(key)}
          style={{ background: 'transparent', borderInlineEnd: 0, padding: '12px 8px' }}
        />
        <div style={{
          position: 'absolute', left: 16, right: 16, bottom: 20,
          color: PT.sidebarOff, fontSize: 11, lineHeight: 1.55, fontWeight: 400,
        }}>
          <div style={{ marginBottom: 8 }}>{admin?.username || '预览管理员'}</div>
          <div>社交审核、退款、固件推送本轮不做必交付。</div>
          <div>不得把 Mock 订单写成真实营收。</div>
          <button
            type="button"
            onClick={onLogout}
            style={{
              marginTop: 12, background: 'transparent', border: 0,
              color: PT.sidebarLink, cursor: 'pointer', padding: 0, fontSize: 12,
            }}
          >退出登录</button>
        </div>
      </Sider>
      <Layout style={{ background: PT.bg }}>
        <Header style={{
          background: PT.surface,
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: `1px solid ${PT.border}`,
          height: 56,
          lineHeight: '56px',
        }}>
          <div style={{ fontSize: 18, fontWeight: 600, color: PT.fg }}>
            {MENU_ITEMS.find(i => i.key === siderSelected)?.label || '数据概览'}
          </div>
          {USE_MOCK ? (
            <span style={{
              color: PT.mock, fontSize: 12, fontWeight: 400,
              background: PT.mockBg, border: `1px solid ${PT.mockBorder}`,
              borderRadius: 999, padding: '4px 10px', lineHeight: 1.4,
            }}>本地 Mock 可预览 · 非真实硬件与第三方 · 待复核</span>
          ) : (
            <span style={{ color: PT.fg3, fontSize: 12 }}>已关闭 Mock，请求将打到本地后端</span>
          )}
        </Header>
        <Content style={{ margin: 0, padding: 24, background: PT.bg, overflow: 'auto' }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  )
}
