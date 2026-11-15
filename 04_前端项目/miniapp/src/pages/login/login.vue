<template>
  <view class="login-page">
    <view class="brand">
      <view class="mark">迹</view>
      <view class="name">宠迹</view>
      <view class="sub">宠物定位与围栏告警</view>
    </view>

    <view class="form">
      <view class="label">手机号</view>
      <input
        v-model="phone"
        class="input"
        type="number"
        maxlength="11"
        placeholder="请输入手机号"
      />

      <view class="label">验证码</view>
      <view class="code-row">
        <input
          v-model="code"
          class="input code-input"
          type="number"
          maxlength="6"
          placeholder="请输入验证码"
        />
        <view
          class="btn-ghost sms-btn"
          :class="{ disabled: countdown > 0 }"
          @tap="sendCode"
        >
          {{ countdown > 0 ? countdown + 's' : '获取验证码' }}
        </view>
      </view>

      <view v-if="errorText" class="err-box">{{ errorText }}</view>

      <view
        class="btn-primary submit"
        :class="{ loading }"
        @tap="handleLogin"
      >
        {{ loading ? '登录中...' : '登录' }}
      </view>

      <view class="btn-ghost wechat-btn" @tap="handleWechatLogin">微信登录</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { http } from '@/utils/request'
import { setTokens, setUser } from '@/utils/auth'
import { USE_MOCK } from '@/utils/config'

const phone = ref('')
const code = ref('')
const loading = ref(false)
const countdown = ref(0)
const errorText = ref('')

function applyAuth(resp: any) {
  if (!resp?.access_token) return
  setTokens(resp.access_token, resp.refresh_token)
  setUser({
    user_id: resp.user_id,
    phone: resp.phone,
    nickname: resp.nickname,
    member_level: resp.member_level,
  })
  uni.switchTab({ url: '/pages/home/home' })
}

function sendCode() {
  if (countdown.value > 0) return
  if (!phone.value.trim()) {
    errorText.value = '请先输入手机号'
    return
  }
  errorText.value = ''
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) clearInterval(timer)
  }, 1000)
}

async function handleLogin() {
  if (!phone.value.trim()) {
    errorText.value = '请先输入手机号'
    return
  }
  if (!code.value.trim()) {
    errorText.value = '请先输入手机号'
    return
  }
  errorText.value = ''
  loading.value = true
  try {
    const resp = await http.post<any>('/auth/login', {
      phone: phone.value.trim(),
      code: code.value.trim(),
    }, false)
    applyAuth(resp)
  } catch (e: any) {
    const raw = String(e?.message || '')
    if (/凭证|验证码|不正确|错误/.test(raw)) {
      errorText.value = '验证码不正确，请重新输入'
    } else {
      errorText.value = '暂时无法连接服务，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

async function handleWechatLogin() {
  if (loading.value) return
  errorText.value = ''
  loading.value = true
  try {
    const wxCode = USE_MOCK
      ? `wx_${Date.now()}`
      : (await new Promise<any>((resolve, reject) => {
          uni.login({
            provider: 'weixin',
            success: (res) => resolve(res),
            fail: reject,
          })
        })).code
    const resp = await http.post<any>('/auth/wechat-login', { code: wxCode }, false)
    applyAuth(resp)
  } catch (e) {
    errorText.value = '暂时无法使用微信登录，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: var(--pt-bg);
  padding-bottom: 80rpx;
}

.brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 40rpx 48rpx;
}

.mark {
  width: 112rpx;
  height: 112rpx;
  border-radius: 28rpx;
  background: var(--pt-accent);
  color: #fff;
  font-size: 44rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.name {
  margin-top: 28rpx;
  font-size: 44rpx;
  font-weight: 600;
  color: var(--pt-fg);
  letter-spacing: -0.01em;
}

.sub {
  margin-top: 10rpx;
  font-size: 24rpx;
  font-weight: 400;
  color: var(--pt-fg-2);
}

.form {
  margin: 0 32rpx;
  background: var(--pt-surface);
  border: 1rpx solid var(--pt-border);
  border-radius: 28rpx;
  padding: 32rpx;
}

.label {
  font-size: 26rpx;
  font-weight: 400;
  color: var(--pt-fg-2);
  margin: 8rpx 0 12rpx;
}

.input {
  background: var(--pt-bg-muted);
  border-radius: 24rpx;
  padding: 22rpx 28rpx;
  font-size: 30rpx;
  color: var(--pt-fg);
  font-weight: 400;
}

.code-row {
  display: flex;
  gap: 16rpx;
  align-items: stretch;
}

.code-input {
  flex: 1;
}

.sms-btn {
  width: 220rpx;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
}

.sms-btn.disabled {
  opacity: 0.55;
}

.submit {
  margin-top: 8rpx;
}

.wechat-btn {
  width: 100%;
  margin-top: 20rpx;
}
</style>
