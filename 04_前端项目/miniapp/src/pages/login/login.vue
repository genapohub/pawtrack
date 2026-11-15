<template>
  <view class="login-page">
    <view class="mock-banner">本地 Mock 预览 · 不接真实微信 / 短信 · 非验收</view>

    <view class="brand">
      <view class="mark">迹</view>
      <view class="name">宠迹</view>
      <view class="sub">宠物定位与围栏告警 · 本地预览</view>
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
        <view class="btn-ghost sms-btn" @tap="onSmsUnused">短信未接入</view>
      </view>

      <view v-if="errorText" class="err-box">{{ errorText }}</view>

      <view
        class="btn-primary submit"
        :class="{ loading }"
        @tap="enterPreview"
      >
        {{ loading ? '登录中...' : '进入本地预览' }}
      </view>

      <view class="hint">默认以本地 Mock 进入，不调用真实微信、短信或 Apple 登录。</view>

      <view class="btn-ghost wechat-btn" @tap="onWechatUnused">微信登录未接入</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { http } from '@/utils/request'
import { setTokens, setUser } from '@/utils/auth'
import { USE_MOCK } from '@/utils/config'

const phone = ref(USE_MOCK ? '13800000000' : '')
const code = ref(USE_MOCK ? '123456' : '')
const loading = ref(false)
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

function onSmsUnused() {
  uni.showToast({ title: '短信未接入', icon: 'none' })
}

function onWechatUnused() {
  uni.showToast({ title: '微信登录未接入', icon: 'none' })
}

async function enterPreview() {
  if (!phone.value.trim() || !code.value.trim()) {
    errorText.value = '请先输入手机号后再进入预览'
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
      errorText.value = '预览凭证不正确，请核对后重试。本页仍是本地示意，未调用真实短信。'
    } else if (/连接|启动|network|fail|Failed|超时|无法/.test(raw) || !USE_MOCK) {
      errorText.value = '无法连接服务，请确认后端已启动。当前未接入生产登录。'
    } else {
      errorText.value = raw || '无法连接服务，请确认后端已启动。当前未接入生产登录。'
    }
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

.submit {
  margin-top: 8rpx;
}

.hint {
  margin: 20rpx 0 28rpx;
  font-size: 22rpx;
  font-weight: 400;
  color: var(--pt-fg-3);
  line-height: 1.5;
}

.wechat-btn {
  width: 100%;
}
</style>
