<template>
  <view class="page">
    <view class="navbar-sm">
      <view class="back" @tap="goBack">‹</view>
      设备管理
      <view class="plus" @tap="goBind">＋</view>
    </view>

    <!-- 设备列表 -->
    <view v-if="devices.length > 0" class="device-list">
      <view v-for="d in devices" :key="d.id" class="card device-card">
        <view class="dev-head">
          <view class="dev-icon" :class="d.hardware_type === 'cat' ? 'cat' : 'dog'">
            {{ d.hardware_type === 'cat' ? '🐱' : '🐶' }}
          </view>
          <view class="dev-info">
            <view class="dev-name">{{ d.sn }}</view>
            <view class="dev-sub">
              {{ d.hardware_type === 'cat' ? '猫咪定位器' : '狗狗定位器' }}
              · 固件 {{ d.firmware_version || 'v1.0.0' }}
            </view>
          </view>
          <view class="badge" :class="statusClass(d.status)">{{ statusText(d.status) }}</view>
        </view>

        <!-- 电量 -->
        <view class="battery-row">
          <text>🔋 电量</text>
          <view class="battery-bar">
            <view class="battery-fill" :class="batteryClass(d.battery_level)" :style="{ width: (d.battery_level || 0) + '%' }"></view>
          </view>
          <text class="battery-num">{{ d.battery_level || 0 }}%</text>
        </view>

        <!-- 绑定宠物 -->
        <view v-if="d.pet_id" class="bound-row">🐾 已绑定宠物 #{{ d.pet_id }}</view>
        <view v-else class="bound-row gray">未绑定宠物</view>

        <!-- 操作 -->
        <view class="btn-row">
          <view class="outline-btn" @tap="findDevice(d)">🔔 查找设备</view>
          <view class="outline-btn" @tap="checkUpdate(d)">🔄 检查固件</view>
          <view class="outline-btn red" @tap="unbind(d)">解绑</view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view v-else class="empty-state">
      <view class="empty-icon">📡</view>
      <view class="empty-text">还没有绑定设备</view>
      <view class="empty-action" @tap="goBind">+ 绑定新设备</view>
    </view>

    <view class="tip">💡 免费版最多绑定 1 台设备，升级会员可绑定更多</view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { http } from '@/utils/request'

const devices = ref<any[]>([])

onShow(loadDevices)

async function loadDevices() {
  try {
    devices.value = (await http.get<any[]>('/devices')) || []
  } catch (e) {
    uni.showToast({ title: '加载设备失败', icon: 'none' })
  }
}

function statusText(status: string): string {
  return { online: '● 在线', offline: '○ 离线', low_battery: '⚠ 低电量' }[status] || status
}

function statusClass(status: string): string {
  return { online: 'green', offline: 'gray', low_battery: 'orange' }[status] || 'gray'
}

function batteryClass(level: number): string {
  if (level == null) return 'warn'
  if (level < 20) return 'low'
  if (level < 50) return 'warn'
  return 'ok'
}

async function findDevice(d: any) {
  try {
    await http.post(`/devices/${d.id}/find`)
    uni.showToast({ title: '已发送查找指令，设备将响铃', icon: 'none' })
  } catch (e: any) {
    uni.showToast({ title: e.message || '发送失败', icon: 'none' })
  }
}

async function checkUpdate(d: any) {
  try {
    const data = await http.get<any>(`/devices/${d.id}/ota/progress`)
    uni.showModal({
      title: '固件信息',
      content: `当前版本：${d.firmware_version || 'v1.0.0'}\n${data?.latest ? '有可用更新' : '已是最新版本'}`,
      showCancel: !!data?.latest,
      confirmText: data?.latest ? '立即升级' : '知道了',
    })
  } catch (e) {
    uni.showToast({ title: '已是最新版本', icon: 'none' })
  }
}

function unbind(d: any) {
  uni.showModal({
    title: '解绑设备',
    content: `确定解绑 ${d.sn} 吗？解绑后将无法接收该设备的定位数据。`,
    confirmColor: '#EF4444',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await http.post('/devices/unbind', { sn: d.sn })
        uni.showToast({ title: '已解绑', icon: 'success' })
        loadDevices()
      } catch (e: any) {
        uni.showToast({ title: e.message || '解绑失败', icon: 'none' })
      }
    },
  })
}

function goBind() { uni.navigateTo({ url: '/pages/device-bind/device-bind' }) }
function goBack() { uni.navigateBack() }
</script>

<style scoped>
.page { min-height: 100vh; background: #f6f7fb; padding-bottom: 60rpx; }
.navbar-sm { display: flex; align-items: center; justify-content: space-between; padding: 20rpx 24rpx; font-size: 32rpx; font-weight: 700; }
.back { font-size: 44rpx; font-weight: 400; color: #333; }
.placeholder { width: 44rpx; }
.plus { width: 56rpx; height: 56rpx; background: #3d6cf5; color: #fff; border-radius: 16rpx; display: flex; align-items: center; justify-content: center; font-size: 36rpx; font-weight: 400; }
.card { background: #fff; border-radius: 20rpx; padding: 28rpx; margin: 0 24rpx 20rpx; box-shadow: 0 4rpx 16rpx rgba(0,0,0,.04); }
.dev-head { display: flex; align-items: center; gap: 16rpx; }
.dev-icon { width: 72rpx; height: 72rpx; border-radius: 16rpx; background: #eef2ff; display: flex; align-items: center; justify-content: center; font-size: 36rpx; }
.dev-icon.cat { background: #fff7ed; }
.dev-icon.dog { background: #eff6ff; }
.dev-info { flex: 1; }
.dev-name { font-size: 28rpx; font-weight: 700; }
.dev-sub { font-size: 22rpx; color: #9aa0a6; margin-top: 4rpx; }
.badge { font-size: 20rpx; padding: 6rpx 14rpx; border-radius: 999rpx; }
.badge.green { background: #f0fdf4; color: #22c55e; }
.badge.orange { background: #fff7ed; color: #f59e0b; }
.badge.gray { background: #f3f4f6; color: #9ca3af; }
.battery-row { display: flex; align-items: center; gap: 12rpx; margin-top: 20rpx; font-size: 24rpx; color: #6b7280; }
.battery-bar { flex: 1; height: 14rpx; background: #f0f1f5; border-radius: 999rpx; overflow: hidden; }
.battery-fill { height: 100%; border-radius: 999rpx; }
.battery-fill.ok { background: #22c55e; }
.battery-fill.warn { background: #f59e0b; }
.battery-fill.low { background: #ef4444; }
.battery-num { font-size: 24rpx; font-weight: 700; color: #1f2329; }
.bound-row { margin-top: 16rpx; font-size: 24rpx; color: #3d6cf5; background: #eef2ff; border-radius: 12rpx; padding: 12rpx 16rpx; }
.bound-row.gray { color: #9ca3af; background: #f6f7fb; }
.btn-row { display: flex; gap: 12rpx; margin-top: 20rpx; }
.outline-btn { flex: 1; border: 2rpx solid #3d6cf5; color: #3d6cf5; background: #fff; border-radius: 14rpx; padding: 16rpx 0; font-size: 24rpx; font-weight: 600; text-align: center; }
.outline-btn.red { border-color: #ef4444; color: #ef4444; }
.empty-state { display: flex; flex-direction: column; align-items: center; padding: 120rpx 0; }
.empty-icon { font-size: 80rpx; }
.empty-text { margin-top: 16rpx; color: #9aa0a6; font-size: 28rpx; }
.empty-action { margin-top: 20rpx; color: #3d6cf5; font-weight: 600; font-size: 28rpx; }
.tip { text-align: center; font-size: 22rpx; color: #aaa; padding: 8rpx 24rpx; }
</style>
