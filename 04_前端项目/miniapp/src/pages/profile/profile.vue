<template>
  <view class="page">
    <!-- 用户信息卡 -->
    <view class="card profile-card">
      <view class="avatar-lg">🐾</view>
      <view class="profile-info">
        <view class="profile-name">{{ user.nickname || '宠友' }}</view>
        <view class="profile-phone">{{ user.phone || '未绑定手机号' }}</view>
      </view>
      <view class="vip-card" @tap="goMember">{{ user.member_level === 'free' ? '免费版' : (user.member_level === 'pro' ? 'Pro版' : '基础版') }} ›</view>
    </view>

    <!-- 数据统计 -->
    <view class="card stat-row">
      <view class="stat-item">
        <view class="num">{{ stats.pets || 0 }}</view>
        <view class="label">宠物</view>
      </view>
      <view class="stat-item">
        <view class="num">{{ stats.devices || 0 }}</view>
        <view class="label">设备</view>
      </view>
      <view class="stat-item">
        <view class="num">{{ stats.alarms || 0 }}</view>
        <view class="label">报警</view>
      </view>
      <view class="stat-item">
        <view class="num" style="color:#f59e0b">{{ stats.points || 0 }}</view>
        <view class="label">积分</view>
      </view>
    </view>

    <!-- 功能入口 -->
    <view class="card menu">
      <view class="menu-item" @tap="goMember">
        <view class="mi-left"><text class="mi-icon">💎</text>会员中心</view>
        <text class="arrow">›</text>
      </view>
      <view class="menu-item" @tap="goPoints">
        <view class="mi-left"><text class="mi-icon">🪙</text>我的积分</view>
        <view class="mi-right"><text class="badge blue">{{ stats.points || 0 }}</text><text class="arrow">›</text></view>
      </view>
      <view class="menu-item" @tap="goInvite">
        <view class="mi-left"><text class="mi-icon">🎁</text>邀请好友</view>
        <view class="mi-right"><text class="badge orange">+50积分/人</text><text class="arrow">›</text></view>
      </view>
      <view class="menu-item" @tap="goDevices">
        <view class="mi-left"><text class="mi-icon">📡</text>设备管理</view>
        <text class="arrow">›</text>
      </view>
      <view class="menu-item" @tap="goNotify">
        <view class="mi-left"><text class="mi-icon">🔔</text>通知设置</view>
        <text class="arrow">›</text>
      </view>
      <view class="menu-item" @tap="goSettings">
        <view class="mi-left"><text class="mi-icon">⚙️</text>设置</view>
        <text class="arrow">›</text>
      </view>
    </view>

    <!-- 我的宠物 -->
    <view class="card">
      <view class="card-title">我的宠物</view>
      <view v-if="pets.length > 0" class="pet-list">
        <view v-for="p in pets" :key="p.id" class="pet-row" @tap="goPetDetail(p.id)">
          <view class="pet-avatar" :class="p.type === 'cat' ? 'cat' : 'dog'">{{ p.type === 'cat' ? '🐱' : '🐶' }}</view>
          <view class="pet-info">
            <view class="pet-name">{{ p.name }}</view>
            <view class="pet-sub">{{ p.breed || (p.type === 'cat' ? '猫咪' : '狗狗') }}</view>
          </view>
          <text class="arrow">›</text>
        </view>
      </view>
      <view v-else class="empty-tip" @tap="goAddPet">+ 添加第一只宠物</view>
    </view>

    <view class="logout-btn" @tap="logout">退出登录</view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { http } from '@/utils/request'
import { getUser, clearTokens } from '@/utils/auth'

const user = ref<any>(getUser() || {})
const pets = ref<any[]>([])
const stats = ref<any>({})

onShow(async () => {
  await Promise.all([loadUser(), loadPets(), loadStats()])
})

async function loadUser() {
  try {
    const me = await http.get<any>('/users/me')
    if (me) user.value = me
  } catch (e) { /* 静默 */ }
}

async function loadPets() {
  try {
    pets.value = (await http.get<any[]>('/pets')) || []
  } catch (e) { /* 静默 */ }
}

async function loadStats() {
  try {
    const [bal] = await Promise.all([
      http.get<any>('/points/balance').catch(() => null),
    ])
    stats.value = {
      pets: pets.value.length,
      devices: 0,
      alarms: 0,
      points: bal?.balance || 0,
    }
  } catch (e) { /* 静默 */ }
}

function goMember() { uni.navigateTo({ url: '/pages/member/member' }) }
function goPoints() { uni.switchTab({ url: '/pages/points/points' }) }
function goInvite() { uni.showToast({ title: '邀请功能开发中', icon: 'none' }) }
function goDevices() { uni.navigateTo({ url: '/pages/device-bind/device-bind' }) }
function goNotify() { uni.showToast({ title: '通知设置开发中', icon: 'none' }) }
function goSettings() { uni.showToast({ title: '设置开发中', icon: 'none' }) }
function goPetDetail(id: number) { uni.navigateTo({ url: '/pages/pet-detail/pet-detail?id=' + id }) }
function goAddPet() { uni.navigateTo({ url: '/pages/pet-add/pet-add' }) }

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
.page { min-height: 100vh; background: #f6f7fb; padding-bottom: 60rpx; }
.card { background: #fff; border-radius: 20rpx; padding: 28rpx; margin: 20rpx 24rpx; box-shadow: 0 4rpx 16rpx rgba(0,0,0,.04); }
.profile-card { display: flex; align-items: center; gap: 20rpx; }
.avatar-lg { width: 96rpx; height: 96rpx; border-radius: 50%; background: #eef2ff; display: flex; align-items: center; justify-content: center; font-size: 44rpx; }
.profile-info { flex: 1; }
.profile-name { font-size: 32rpx; font-weight: 700; }
.profile-phone { font-size: 24rpx; color: #9aa0a6; margin-top: 4rpx; }
.vip-card { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #fff; font-size: 22rpx; font-weight: 600; padding: 12rpx 24rpx; border-radius: 999rpx; }
.stat-row { display: flex; text-align: center; padding: 24rpx 0; }
.stat-item { flex: 1; }
.num { font-size: 36rpx; font-weight: 800; }
.label { font-size: 22rpx; color: #9aa0a6; margin-top: 4rpx; }
.menu { padding: 8rpx 28rpx; }
.menu-item { display: flex; align-items: center; justify-content: space-between; padding: 24rpx 0; border-bottom: 1px solid #f3f4f6; font-size: 28rpx; font-weight: 600; }
.menu-item:last-child { border-bottom: none; }
.mi-left { display: flex; align-items: center; gap: 16rpx; }
.mi-icon { font-size: 32rpx; }
.mi-right { display: flex; align-items: center; gap: 12rpx; }
.arrow { color: #c0c4cc; font-size: 32rpx; font-weight: 400; }
.badge { font-size: 20rpx; padding: 6rpx 14rpx; border-radius: 999rpx; }
.badge.blue { background: #eef2ff; color: #3d6cf5; }
.badge.orange { background: #fffbeb; color: #f59e0b; }
.card-title { font-size: 30rpx; font-weight: 700; margin-bottom: 12rpx; }
.pet-row { display: flex; align-items: center; gap: 16rpx; padding: 14rpx 0; }
.pet-avatar { width: 72rpx; height: 72rpx; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 36rpx; }
.pet-avatar.dog { background: #eff6ff; }
.pet-avatar.cat { background: #fff7ed; }
.pet-info { flex: 1; }
.pet-name { font-size: 28rpx; font-weight: 600; }
.pet-sub { font-size: 22rpx; color: #9aa0a6; margin-top: 2rpx; }
.empty-tip { text-align: center; color: #3d6cf5; padding: 30rpx 0; font-size: 26rpx; font-weight: 600; }
.logout-btn { margin: 30rpx 24rpx; text-align: center; background: #fef2f2; color: #ef4444; border-radius: 999rpx; padding: 22rpx 0; font-size: 28rpx; font-weight: 600; }
</style>
