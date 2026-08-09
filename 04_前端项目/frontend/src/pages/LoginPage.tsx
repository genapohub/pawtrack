/**
 * S1 — 注册/登录页
 * 手机号 + 验证码登录（MVP 阶段验证码任意输入）
 */
import React, { useState } from 'react'
import { api, saveAuth } from '../api/client'
import { showToast } from '../utils/toast'

export function LoginPage({ onLoginSuccess }: { onLoginSuccess: () => void }) {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [phone, setPhone] = useState('')
  const [code, setCode] = useState('')
  const [nickname, setNickname] = useState('')
  const [loading, setLoading] = useState(false)
  const [countdown, setCountdown] = useState(0)

  // 发送验证码（MVP：仅 Toast 提示）
  const sendCode = () => {
    if (!/^1[3-9]\d{9}$/.test(phone)) {
      showToast('请输入正确的手机号')
      return
    }
    showToast('验证码已发送（MVP：任意数字即可）')
    setCountdown(60)
    const timer = setInterval(() => {
      setCountdown(c => {
        if (c <= 1) { clearInterval(timer); return 0 }
        return c - 1
      })
    }, 1000)
  }

  // 提交登录/注册
  const handleSubmit = async () => {
    if (!/^1[3-9]\d{9}$/.test(phone)) {
      showToast('请输入正确的手机号')
      return
    }
    if (code.length < 4) {
      showToast('请输入验证码')
      return
    }

    setLoading(true)
    try {
      const resp = mode === 'register'
        ? await api.auth.register(phone, code, nickname || undefined)
        : await api.auth.login(phone, code)

      if (resp.code === 0 && resp.data?.access_token) {
        saveAuth(resp.data)
        showToast(mode === 'register' ? '注册成功！' : '登录成功！')
        onLoginSuccess()
      } else {
        showToast(resp.message || '操作失败')
      }
    } catch (e: any) {
      showToast(e.message || '网络错误')
    } finally {
      setLoading(false)
    }
  }

  // 微信登录
  const handleWechatLogin = async () => {
    setLoading(true)
    try {
      // MVP：模拟微信 code
      const resp = await api.auth.wechatLogin('mock_wx_code_' + Date.now())
      if (resp.code === 0 && resp.data?.access_token) {
        saveAuth(resp.data)
        showToast('微信登录成功！')
        onLoginSuccess()
      }
    } catch (e: any) {
      showToast(e.message || '微信登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="screen" style={{ paddingBottom: 0 }}>
      {/* Logo */}
      <div className="login-logo">
        <div className="login-logo-icon">🐾</div>
        <div className="login-logo-text">宠迹 PawTrack</div>
        <div className="login-logo-desc">宠物智能定位与社交平台</div>
      </div>

      {/* 模式切换 */}
      <div style={{ display: 'flex', padding: '0 16px 20px', gap: 8 }}>
        <button
          onClick={() => setMode('login')}
          style={{
            flex: 1, padding: '10px', borderRadius: 10,
            border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: 15,
            background: mode === 'login' ? 'var(--primary)' : 'var(--border)',
            color: mode === 'login' ? '#FFF' : 'var(--sub)'
          }}
        >登录</button>
        <button
          onClick={() => setMode('register')}
          style={{
            flex: 1, padding: '10px', borderRadius: 10,
            border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: 15,
            background: mode === 'register' ? 'var(--primary)' : 'var(--border)',
            color: mode === 'register' ? '#FFF' : 'var(--sub)'
          }}
        >注册</button>
      </div>

      {/* 表单 */}
      <div style={{ padding: '0 16px' }}>
        {mode === 'register' && (
          <div className="input-group">
            <div className="input-label">昵称（选填）</div>
            <input
              className="input"
              type="text"
              placeholder="给自己起个昵称"
              value={nickname}
              onChange={e => setNickname(e.target.value)}
              maxLength={20}
            />
          </div>
        )}

        <div className="input-group">
          <div className="input-label">手机号</div>
          <input
            className="input"
            type="tel"
            placeholder="请输入手机号"
            value={phone}
            onChange={e => setPhone(e.target.value.replace(/\D/g, '').slice(0, 11))}
            maxLength={11}
          />
        </div>

        <div className="input-group">
          <div className="input-label">验证码</div>
          <div style={{ display: 'flex', gap: 8 }}>
            <input
              className="input"
              type="text"
              placeholder="请输入验证码"
              value={code}
              onChange={e => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
              maxLength={6}
              style={{ flex: 1 }}
            />
            <button
              onClick={sendCode}
              disabled={countdown > 0}
              style={{
                whiteSpace: 'nowrap', padding: '0 20px',
                borderRadius: 12, border: '1.5px solid var(--primary)',
                background: countdown > 0 ? 'var(--border)' : 'transparent',
                color: countdown > 0 ? 'var(--muted)' : 'var(--primary)',
                fontSize: 14, fontWeight: 600, cursor: countdown > 0 ? 'not-allowed' : 'pointer'
              }}
            >
              {countdown > 0 ? `${countdown}s` : '发送'}
            </button>
          </div>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleSubmit}
          disabled={loading}
          style={{ marginTop: 24 }}
        >
          {loading ? '请稍候...' : mode === 'register' ? '注册' : '登录'}
        </button>

        {/* 分割线 */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '28px 0' }}>
          <div style={{ flex: 1, height: 1, background: 'var(--border)' }} />
          <span style={{ fontSize: 12, color: 'var(--muted)' }}>其他登录方式</span>
          <div style={{ flex: 1, height: 1, background: 'var(--border)' }} />
        </div>

        {/* 微信登录 */}
        <div style={{ textAlign: 'center' }}>
          <button
            onClick={handleWechatLogin}
            disabled={loading}
            style={{
              width: 56, height: 56, borderRadius: '50%',
              border: 'none', cursor: 'pointer', fontSize: 28,
              background: '#07C160', color: '#FFF'
            }}
          >💬</button>
          <div style={{ fontSize: 12, color: 'var(--sub)', marginTop: 8 }}>微信登录</div>
        </div>
      </div>

      {/* 协议 */}
      <div style={{ position: 'absolute', bottom: 40, width: '100%', textAlign: 'center', fontSize: 12, color: 'var(--muted)' }}>
        登录即代表同意 <span style={{ color: 'var(--primary)' }}>《用户协议》</span>
        和 <span style={{ color: 'var(--primary)' }}>《隐私政策》</span>
      </div>
    </div>
  )
}
