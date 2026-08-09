<template>
  <view class="page">
    <view class="navbar-sm">
      <view class="back" @tap="goBack">‹</view>
      设置
      <view class="placeholder"></view>
    </view>

    <!-- 账号 -->
    <view class="card">
      <view class="card-title">账号</view>
      <view class="menu-item">
        <view class="mi-left"><text class="mi-icon">📱</text>手机号</view>
        <view class="mi-right"><text class="mi-value">{{ user.phone || '未绑定' }}</text><text class="arrow">›</text></view>
      </view>
      <view class="menu-item">
        <view class="mi-left"><text class="mi-icon">👤</text>昵称</view>
        <view class="mi-right"><text class="mi-value">{{ user.nickname || '未设置' }}</text><text class="arrow">›</text></view>
      </view>
    </view>

    <!-- 隐私 -->
    <view class="card">
      <view class="card-title">隐私</view>
      <view class="menu-item" @tap="showPrivacyPicker">
        <view class="mi-left"><text class="mi-icon">📍</text>位置可见性</view>
        <view class="mi-right"><text class="mi-value">{{ privacyLabel }}</text><text class="arrow">›</text></view>
      </view>
      <view class="switch-row">
        <view class="switch-info">
          <view class="switch-title">附近宠物展示</view>
          <view class="switch-sub">在附近宠物中展示我的宠物</view>
        </view>
        <view class="switch" :class="{ on: privacy.nearby }" @tap="privacy.nearby = !privacy.nearby; savePrivacy()"></view>
      </view>
      <view class="switch-row">
        <view class="switch-info">
          <view class="switch-title">碰头匹配</view>
          <view class="switch-sub">参与好朋狗碰头匹配</view>
        </view>
        <view class="switch" :class="{ on: privacy.meet }" @tap="privacy.meet = !privacy.meet; savePrivacy()"></view>
      </view>
    </view>

    <!-- 通用 -->
    <view class="card">
      <view class="card-title">通用</view>
      <view class="menu-item" @tap="goNotify">
        <view class="mi-left"><text class="mi-icon">🔔</text>通知设置</view>
        <text class="arrow">›</text>
      </view>
      <view class="menu-item" @tap="goDevices">
        <view class="mi-left"><text class="mi-icon">📡</text>设备管理</view>
        <text class="arrow">›</text>
      </view>
      <view class="menu-item" @tap="goAbout">
        <view class="mi-left"><text class="mi-icon">ℹ️</text>关于宠迹</view>
        <view class="mi-right"><text class="mi-value">v0.4.0</text><text class="arrow">›</text></view>
      </view>
    </view>

    <!-- 协议 -->
    <view class="card">
      <view class="card-title">法律</view>
      <view class="menu-item">
        <view class="mi-left"><text class="mi-icon">📄</text>用户协议</view>
        <text class="arrow">›</text>
      </view>
      <view class="menu-item">
        <view class="mi-left"><text class="mi-icon">🔒</text>隐私政策</view>
        <text class="arrow">›</text>
      </view>
    </view>

    <view class="logout-btn" @tap="logout">退出登录</view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { http } from '@/utils/request'
import { getUser, clearTokens } from '@/utils/auth'

const user = ref<any>(getUser() || {})
const privacy = ref({ nearby: true, meet: true, location: 'friends' })

const privacyLabel = computed(() => {
  return { friends: '仅好友可见', nearby: '附近宠物可见', private: '仅自己可见' }[privacy.value.location] || '仅好友可见'
})

onShow(async () => {
  await loadUser()
})

async function loadUser() {
  try {
    const me = await http.get<any>('/users/me')
    if (me) {
      user.value = me
      if (me.privacy_location) privacy.value.location = me.privacy_location
    }
  } catch (e) { /* 静默 */ }
}

function showPrivacyPicker() {
  uni.showActionSheet({
    itemList: ['仅好友可见', '附近宠物可见', '仅自己可见'],
    success: async (res) => {
      const map = ['friends', 'nearby', 'private']
      privacy.value.location = map[res.tapIndex] || 'friends'
      await savePrivacy()
    },
  })
}

async function savePrivacy() {
  try {
    await http.put('/users/me', { privacy_location: privacy.value.location })
  } catch (e) { /* 静默 */ }
}

function goNotify() { uni.navigateTo({ url: '/pages/notify-settings/notify-settings' }) }
function goDevices() { uni.navigateTo({ url: '/pages/device-manage/device-manage' }) }
function goAbout() {
  uni.showModal({
    title: '关于宠迹',
    content: '宠迹 PawTrack v0.4.0\n宠物智能定位与社交平台\n© 2026 宠迹团队',
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

function goBack() { uni.navigateBack() }
</script>

<style scoped>
.page { min-height: 100vh; background: #f6f7fb; padding-bottom: 60rpx; }
.navbar-sm { display: flex; align-items: center; justify-content: space-between; padding: 20rpx 24rpx; font-size: 32rpx; font-weight: 700; }
.back { font-size: 44rpx; font-weight: 400; color: #333; }
.placeholder { width: 44rpx; }
.card { background: #fff; border-radius: 20rpx; padding: 12rpx 28rpx; margin: 0 24rpx 20rpx; box-shadow: 0 4rpx 16rpx rgba(0,0,0,.04); }
.card-title { font-size: 26rpx; font-weight: 700; color: #9aa0a6; padding: 16rpx 0 4rpx; }
.menu-item { display: flex; align-items: center; justify-content: space-between; padding: 24rpx 0; border-bottom: 1px solid #f3f4f6; font-size: 28rpx; font-weight: 600; }
.menu-item:last-child { border-bottom: none; }
.mi-left { display: flex; align-items: center; gap: 16rpx; }
.mi-icon { font-size: 32rpx; }
.mi-right { display: flex; align-items: center; gap: 12rpx; }
.mi-value { font-size: 24rpx; color: #9aa0a6; font-weight: 400; }
.arrow { color: #c0c4cc; font-size: 32rpx; font-weight: 400; }
.switch-row { display: flex; align-items: center; justify-content: space-between; padding: 24rpx 0; border-bottom: 1px solid #f3f4f6; }
.switch-row:last-child { border-bottom: none; }
.switch-info { flex: 1; }
.switch-title { font-size: 28rpx; font-weight: 600; }
.switch-sub { font-size: 22rpx; color: #9aa0a6; margin-top: 4rpx; }
.switch { width: 88rpx; height: 48rpx; border-radius: 999rpx; background: #d1d5db; position: relative; transition: .2s; }
.switch::after { content: ''; position: absolute; width: 40rpx; height: 40rpx; border-radius: 50%; background: #fff; top: 4rpx; left: 4rpx; transition: .2s; }
.switch.on { background: #3d6cf5; }
.switch.on::after { left: 44rpx; }
.logout-btn { margin: 30rpx 24rpx; text-align: center; background: #fef2f2; color: #ef4444; border-radius: 999rpx; padding: 24rpx 0; font-size: 28rpx; font-weight: 600; }
</style>
