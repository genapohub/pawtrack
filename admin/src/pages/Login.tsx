/**
 * 管理后台 — 登录页
 */
import { useState } from 'react'
import { Card, Form, Input, Button, message } from 'antd'
import { LockOutlined, UserOutlined } from '@ant-design/icons'
import { api, saveAuth } from '../api/client'

export default function LoginPage({ onLoginSuccess }: { onLoginSuccess: () => void }) {
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (values: { username: string; password: string }) => {
    setLoading(true)
    try {
      const resp = await api.login(values.username, values.password)
      if (resp.data?.access_token) {
        saveAuth({
          access_token: resp.data.access_token,
          username: resp.data.username,
          role: resp.data.role
        })
        message.success('登录成功')
        onLoginSuccess()
      }
    } catch (e: any) {
      message.error(e.message || '登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'linear-gradient(135deg, #1E293B 0%, #334155 100%)'
    }}>
      <Card style={{ width: 380, boxShadow: '0 12px 40px rgba(0,0,0,0.2)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{ fontSize: 40 }}>🐾</div>
          <h2 style={{ margin: '8px 0 4px' }}>宠迹 PawTrack</h2>
          <div style={{ color: '#94A3B8', fontSize: 13 }}>管理后台</div>
        </div>
        <Form onFinish={handleSubmit} layout="vertical" initialValues={{ username: 'admin' }}>
          <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input size="large" prefix={<UserOutlined />} placeholder="管理员账号" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password size="large" prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" size="large" block loading={loading}>
              登录
            </Button>
          </Form.Item>
        </Form>
        <div style={{ textAlign: 'center', fontSize: 12, color: '#94A3B8' }}>
          默认账号 admin / pawtrack_admin_2026
        </div>
      </Card>
    </div>
  )
}
