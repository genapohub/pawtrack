<template>
  <view class="login-page">
    <!-- Logo -->
    <view class="logo-area">
      <view class="logo-icon">🐾</view>
      <view class="logo-title">宠迹 PawTrack</view>
      <view class="logo-desc">宠物智能定位与社交平台</view>
    </view>

    <!-- 模式切换 -->
    <view class="mode-switch">
      <view
        class="mode-item"
        :class="{ active: mode === 'login' }"
        @tap="mode = 'login'"
      >登录</view>
      <view
        class="mode-item"
        :class="{ active: mode === 'register' }"
        @tap="mode = 'register'"
      >注册</view>
    </view>

    <!-- 表单 -->
    <view class="form-area">
      <!-- 昵称（注册时显示） -->
      <view v-if="mode === 'register'" class="input-group">
        <view class="input-label">昵称（选填）</view>
        <input
          v-model="nickname"
          class="input"
          placeholder="给自己起个昵称"
          maxlength="20"
        />
      </view>

      <!-- 手机号 -->
      <view class="input-group">
        <view class="input-label">手机号</view>
        <input
          v-model="phone"
          class="input"
          type="number"
          placeholder="请输入手机号"
          maxlength="11"
        />
      </view>

      <!-- 验证码 -->
      <view class="input-group">
        <view class="input-label">验证码</view>
        <view class="code-row">
          <input
            v-model="code"
            class="input code-input"
            type="number"
            placeholder="请输入验证码"
            maxlength="6"
          />
          <view
            class="send-code"
            :class="{ disabled: countdown > 0 }"
            @tap="sendCode"
          >
            {{ countdown > 0 ? countdown + 's' : '发送' }}
          </view>
        </view>
      </view>

      <!-- 提交按钮 -->
      <view class="btn-primary submit-btn" :class="{ loading: loading }" @tap="handleSubmit">
        {{ loading ? '请稍候...' : mode === 'register' ? '注册' : '登录' }}
      </view>

      <!-- 分割线 -->
      <view class="divider">
        <view class="divider-line" />
        <view class="divider-text">其他登录方式</view>
        <view class="divider-line" />
      </view>

      <!-- 微信登录 -->
      <view class="wechat-login">
        <view class="wechat-circle" @tap="handleWechatLogin">
          <text class="wechat-icon">💬</text>
        </view>
        <view class="wechat-text">微信登录</view>
      </view>
    </view>

    <!-- 协议 -->
    <view class="agreement">
      登录即代表同意《用户协议》和《隐私政策》
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { http } from '@/utils/request'
import { setTokens, setUser } from '@/utils/auth'

const mode = ref<'login' | 'register'>('login')
const phone = ref('')
const code = ref('')
const nickname = ref('')
const loading = ref(false)
const countdown = ref(0)

/** 发送验证码（MVP：仅提示） */
function sendCode() {
  if (!/^1[3-9]\d{9}$/.test(phone.value)) {
    uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
    return
  }
  uni.showToast({ title: '验证码已发送（MVP：任意数字即可）', icon: 'none' })
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) clearInterval(timer)
  }, 1000)
}

/** 登录/注册提交 */
async function handleSubmit() {
  if (!/^1[3-9]\d{9}$/.test(phone.value)) {
    uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
    return
  }
  if (code.value.length < 4) {
    uni.showToast({ title: '请输入验证码', icon: 'none' })
    return
  }

  loading.value = true
  try {
    const resp = mode.value === 'register'
      ? await http.post<any>('/auth/register', {
          phone: phone.value, code: code.value, nickname: nickname.value || undefined,
        }, false)
      : await http.post<any>('/auth/login', {
          phone: phone.value, code: code.value,
        }, false)

    if (resp.access_token) {
      setTokens(resp.access_token, resp.refresh_token)
      setUser({
        user_id: resp.user_id,
        phone: resp.phone,
        nickname: resp.nickname,
        member_level: resp.member_level,
      })
      uni.showToast({ title: mode.value === 'register' ? '注册成功！' : '登录成功！', icon: 'success' })
      setTimeout(() => uni.switchTab({ url: '/pages/home/home' }), 800)
    }
  } catch (e: any) {
    uni.showToast({ title: e.message || '网络错误', icon: 'none' })
  } finally {
    loading.value = false
  }
}

/** 微信一键登录 */
async function handleWechatLogin() {
  loading.value = true
  try {
    // 获取微信登录 code
    const loginRes = await new Promise<any>((resolve, reject) => {
      uni.login({
        provider: 'weixin',
        success: (res) => resolve(res),
        fail: reject,
      })
    })
    const code = loginRes.code || `mock_wx_code_${Date.now()}`
    const resp = await http.post<any>('/auth/wechat-login', { code }, false)
    if (resp.access_token) {
      setTokens(resp.access_token, resp.refresh_token)
      setUser({
        user_id: resp.user_id,
        phone: resp.phone,
        nickname: resp.nickname,
        member_level: resp.member_level,
      })
      uni.showToast({ title: '微信登录成功！', icon: 'success' })
      setTimeout(() => uni.switchTab({ url: '/pages/home/home' }), 800)
    }
  } catch (e: any) {
    uni.showToast({ title: e.message || '微信登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: #f6f7fb;
  display: flex;
  flex-direction: column;
}

.logo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 140rpx;
  padding-bottom: 60rpx;
}

.logo-icon {
  font-size: 100rpx;
}

.logo-title {
  font-size: 44rpx;
  font-weight: 700;
  margin-top: 16rpx;
  color: #1f2329;
}

.logo-desc {
  font-size: 24rpx;
  color: #9aa0a6;
  margin-top: 8rpx;
}

/* 模式切换 */
.mode-switch {
  display: flex;
  margin: 0 40rpx 24rpx;
  background: #eceef2;
  border-radius: 16rpx;
  padding: 6rpx;
}

.mode-item {
  flex: 1;
  text-align: center;
  padding: 16rpx 0;
  border-radius: 12rpx;
  font-size: 28rpx;
  color: #6b7280;
  font-weight: 600;
}

.mode-item.active {
  background: #fff;
  color: #3d6cf5;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
}

/* 表单 */
.form-area {
  padding: 0 40rpx;
}

.input-group {
  margin-bottom: 24rpx;
}

.input-label {
  font-size: 24rpx;
  color: #6b7280;
  margin-bottom: 10rpx;
}

.input {
  background: #fff;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  font-size: 28rpx;
  border: 2rpx solid transparent;
}

.code-row {
  display: flex;
  gap: 16rpx;
  align-items: center;
}

.code-input {
  flex: 1;
}

.send-code {
  white-space: nowrap;
  padding: 20rpx 32rpx;
  border-radius: 16rpx;
  border: 2rpx solid #3d6cf5;
  color: #3d6cf5;
  font-size: 26rpx;
  font-weight: 600;
}

.send-code.disabled {
  border-color: #d1d5db;
  color: #9ca3af;
}

.submit-btn {
  margin-top: 20rpx;
}

.submit-btn.loading {
  opacity: 0.6;
}

/* 分割线 */
.divider {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin: 48rpx 0 32rpx;
}

.divider-line {
  flex: 1;
  height: 2rpx;
  background: #e5e7eb;
}

.divider-text {
  font-size: 24rpx;
  color: #9aa0a6;
}

/* 微信登录 */
.wechat-login {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.wechat-circle {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  background: #07c160;
  display: flex;
  align-items: center;
  justify-content: center;
}

.wechat-icon {
  font-size: 48rpx;
}

.wechat-text {
  font-size: 24rpx;
  color: #6b7280;
  margin-top: 12rpx;
}

/* 协议 */
.agreement {
  position: fixed;
  bottom: 60rpx;
  left: 0;
  width: 100%;
  text-align: center;
  font-size: 22rpx;
  color: #9aa0a6;
}
</style>
