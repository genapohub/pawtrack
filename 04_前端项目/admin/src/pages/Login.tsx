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
        setErrorText('无法连接服务，请确认后端已启动。关闭 Mock 时不写死预览口令。')
      } else {
        setErrorText('账号或密码错误')
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
        }}>本地 Mock · 非验收</span>
        <h1 style={{ margin: 0, fontSize: 28, fontWeight: 600, letterSpacing: '-0.01em', color: PT.fgInv }}>宠迹管理端</h1>
        <p style={{ margin: '16px 0 0', fontSize: 13, lineHeight: 1.7, fontWeight: 400, color: PT.sidebarLink, maxWidth: 360 }}>
          本轮只要求看懂设备与告警信息结构。SN、在线、电量、告警地址均为 Mock。关闭 Mock 且后端未启动时，应提示无法连接服务，而不是写死预览口令。
        </p>
        <p style={{ margin: '16px 0 0', fontSize: 13, lineHeight: 1.7, fontWeight: 400, color: PT.sidebarLink, maxWidth: 360 }}>
          不把 Mock 订单「已支付」写成真实营收。社交审核、退款审批、固件批量推送不是本轮必交付。
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
            必须能看出这是本地预览。非 Mock 时不写死预览口令。
          </p>
          <Form
            onFinish={handleSubmit}
            layout="vertical"
            requiredMark={false}
            initialValues={USE_MOCK ? { username: 'admin.preview' } : undefined}
          >
            <Form.Item name="username" label="账号" rules={[{ required: true, message: '请输入账号' }]}>
              <Input size="large" placeholder={USE_MOCK ? 'admin.preview' : '管理员账号'} autoComplete="username" />
            </Form.Item>
            <Form.Item name="password" label="密码" rules={[{ required: true, message: '请输入密码' }]}>
              <Input.Password size="large" placeholder={USE_MOCK ? '本地预览口令' : '密码'} autoComplete="current-password" />
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
