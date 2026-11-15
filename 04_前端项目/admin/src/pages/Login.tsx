/**
 * 管理后台登录 — 对齐画布 202:1 / 203:1 / 204:1
 */
import { useState } from 'react'
import { Form, Input, Button } from 'antd'
import { api, saveAuth } from '../api/client'
import { USE_MOCK } from '../env'
import { PT } from '../styles/tokens'

export default function LoginPage({ onLoginSuccess }: { onLoginSuccess: () => void }) {
  const [loading, setLoading] = useState(false)
  const [errorText, setErrorText] = useState('')

  const handleSubmit = async (values: { username: string; password: string }) => {
    setLoading(true)
    setErrorText('')
    try {
      const resp = await api.login(values.username, values.password)
      if (resp.data?.access_token) {
        saveAuth({
          access_token: resp.data.access_token,
          username: resp.data.username,
          role: resp.data.role
        })
        onLoginSuccess()
      }
    } catch (e: any) {
      const raw = String(e?.message || '')
      if (/连接|启动|Failed to fetch|Network|超时|ECONNREFUSED|无法连接/i.test(raw) && !USE_MOCK) {
        setErrorText('暂时无法连接服务，请稍后重试')
      } else {
        setErrorText('账号或密码错误，请重新输入。')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'grid',
      gridTemplateColumns: 'minmax(280px, 42%) 1fr',
      background: PT.bg,
    }}>
      <aside style={{
        background: PT.accent,
        color: PT.fgInv,
        padding: '48px 40px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
      }}>
        <span style={{
          alignSelf: 'flex-start',
          background: PT.mockBg,
          color: PT.mock,
          border: `1px solid ${PT.mockBorder}`,
          borderRadius: 999,
          fontSize: 12,
          fontWeight: 400,
          padding: '4px 10px',
          marginBottom: 28,
        }}>运营后台</span>
        <h1 style={{ margin: 0, fontSize: 28, fontWeight: 600, letterSpacing: '-0.01em', color: PT.fgInv }}>宠迹管理端</h1>
        <p style={{ margin: '16px 0 0', fontSize: 13, lineHeight: 1.7, fontWeight: 400, color: PT.sidebarLink, maxWidth: 360 }}>
          查看设备在线、电量与最后位置，及时处理围栏与低电告警。支持按 SN 检索。为运营同事准备的管理后台。设备、告警与宠物绑定信息集中在这里查看。请使用运营管理员账号登录。
        </p>
      </aside>

      <main style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 40,
        background: PT.bg,
      }}>
        <div style={{
          width: 400,
          background: PT.surface,
          border: `1px solid ${PT.border}`,
          borderRadius: PT.radiusMd,
          padding: '32px 28px',
        }}>
          <h2 style={{ margin: 0, fontSize: 18, fontWeight: 600, color: PT.fg }}>管理员登录</h2>
          <p style={{ margin: '8px 0 20px', fontSize: 13, color: PT.fg2, lineHeight: 1.55, fontWeight: 400 }}>
            请输入管理员账号和密码
          </p>
          <Form
            onFinish={handleSubmit}
            layout="vertical"
            requiredMark={false}
            initialValues={USE_MOCK ? { username: 'linxiaohe' } : undefined}
          >
            <Form.Item name="username" label="账号" rules={[{ required: true, message: '请输入账号' }]}>
              <Input size="large" placeholder="请输入账号" autoComplete="username" />
            </Form.Item>
            <Form.Item name="password" label="密码" rules={[{ required: true, message: '请输入密码' }]}>
              <Input.Password size="large" placeholder="密码" autoComplete="current-password" />
            </Form.Item>
            {errorText ? (
              <div style={{
                background: PT.dangerSubtle,
                color: PT.danger,
                borderRadius: 12,
                padding: '10px 12px',
                fontSize: 13,
                marginBottom: 16,
                lineHeight: 1.5,
              }}>{errorText}</div>
            ) : null}
            <Form.Item style={{ marginBottom: 0 }}>
              <Button type="primary" htmlType="submit" size="large" block loading={loading}>
                {loading ? '登录中...' : '登录'}
              </Button>
            </Form.Item>
          </Form>
        </div>
      </main>
    </div>
  )
}
