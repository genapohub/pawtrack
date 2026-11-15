<template>
  <view class="page">
    <view class="mock-banner">本地 Mock 预览 · 非真实硬件 / 微信 / 短信 / 地图 / 支付</view>

    <view class="pt-card menu">
      <view class="menu-item">
        <text class="mi-name">位置隐私</text>
        <text class="mi-note" @tap="showPrivacyPicker">{{ privacyLabel }}</text>
      </view>
      <view class="menu-item">
        <text class="mi-name">通知设置</text>
        <text class="mi-note" @tap="goNotify">与报警设置分离</text>
      </view>
      <view class="menu-item last">
        <text class="mi-name">关于宠迹</text>
        <text class="mi-note" @tap="goAbout">本地预览版</text>
      </view>
    </view>

    <view class="privacy-note">位置分享、地图能力均未接入真实服务。本页只保留隐私说明和退出确认。</view>

    <view class="logout" @tap="logout">退出登录</view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { http } from '@/utils/request'
import { getUser, clearTokens } from '@/utils/auth'

const user = ref<any>(getUser() || {})
const privacy = ref({ location: 'friends' })
const privacyLabel = computed(() => {
  return { friends: '仅好友可见', nearby: '附近宠物可见', private: '仅自己可见' }[privacy.value.location] || '仅好友可见'
})

onShow(async () => {
  try {
    const me = await http.get<any>('/users/me')
    if (me) {
      user.value = me
      if (me.privacy_location) privacy.value.location = me.privacy_location
    }
  } catch (e) { /* 静默 */ }
})

function showPrivacyPicker() {
  uni.showActionSheet({
    itemList: ['仅好友可见', '附近宠物可见', '仅自己可见'],
    success: async (res) => {
      const map = ['friends', 'nearby', 'private']
      privacy.value.location = map[res.tapIndex] || 'friends'
      try { await http.put('/users/me', { privacy_location: privacy.value.location }) } catch (e) { /* 静默 */ }
    },
  })
}

function goNotify() { uni.navigateTo({ url: '/pages/notify-settings/notify-settings' }) }
function goAbout() {
  uni.showModal({
    title: '关于宠迹',
    content: '宠迹本地预览版。未接入真实硬件、微信、短信、支付或地图。',
    showCancel: false,
  })
}

function logout() {
  uni.showModal({
    title: '退出登录',
    content: '确定要退出当前账号吗？',
    success: (res) => {
      if (res.confirm) {
        clearTokens()
        uni.reLaunch({ url: '/pages/login/login' })
      }
    },
  })
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--pt-bg); padding-bottom: 80rpx; }
.menu { margin-top: 24rpx; padding: 8rpx 32rpx; }
.menu-item {
  display: flex;
  justify-content: space-between;
  gap: 16rpx;
  padding: 28rpx 0;
  border-bottom: 1rpx solid var(--pt-border);
}
.menu-item.last { border-bottom: none; }
.mi-name { font-size: 30rpx; color: var(--pt-fg); font-weight: 400; }
.mi-note { font-size: 24rpx; color: var(--pt-fg-3); }
.privacy-note {
  margin: 8rpx 40rpx 32rpx;
  font-size: 22rpx;
  color: var(--pt-fg-3);
  line-height: 1.5;
}
.logout {
  margin: 0 32rpx;
  text-align: center;
  padding: 22rpx 0;
  border-radius: 24rpx;
  background: var(--pt-danger-subtle);
  color: var(--pt-danger);
  font-size: 28rpx;
  font-weight: 500;
}
</style>
