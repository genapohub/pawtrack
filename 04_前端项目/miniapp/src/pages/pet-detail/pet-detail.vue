<template>
  <view class="page">
    <!-- 顶部信息 -->
    <view class="hero" :class="pet?.type === 'cat' ? 'cat-bg' : 'dog-bg'">
      <view class="back" @tap="goBack">‹</view>
      <text class="pro-chip" style="position:absolute;right:24rpx;top:24rpx" @tap="goPro">Pro</text>
      <view class="big-avatar">{{ pet?.type === 'cat' ? '🐱' : '🐶' }}</view>
      <view class="hero-name">{{ pet?.name || '宠物详情' }}</view>
      <view class="hero-sub">{{ breedText }}</view>
      <view class="hero-status">
        <span class="badge" :class="device.online ? 'green' : 'gray'">
          {{ device.online ? '● 在线' : '○ 离线' }}
        </span>
        <span class="badge orange" v-if="device.battery != null">🔋 {{ device.battery }}%</span>
      </view>
    </view>

    <!-- 快捷状态卡 -->
    <view class="card grid-2">
      <view class="cell" @tap="goHistory">
        <div class="cell-icon">🗺️</div>历史轨迹
        <span>{{ location.ts ? '今日有更新' : '暂无数据' }}</span>
      </view>
      <view class="cell" @tap="goAlarmSettings">
        <div class="cell-icon">🛡️</div>安全围栏
        <span>{{ pet?.fence_enabled ? '已开启 · ' + pet?.fence_radius + 'm' : '未开启' }}</span>
      </view>
      <view class="cell" @tap="goDeviceStatus">
        <div class="cell-icon">📡</div>设备状态
        <span>{{ device.sn || '未绑定' }}</span>
      </view>
      <view class="cell" @tap="goMember">
        <div class="cell-icon">💎</div>会员升级
        <span>免费版</span>
      </view>
    </view>

    <!-- 实时位置 -->
    <view class="card">
      <view class="card-title">📍 实时位置</view>
      <view class="map-mini wide">
        <view class="pin-sm me" style="left:50%;top:50%">{{ pet?.type === 'cat' ? '🐱' : '🐶' }}</view>
      </view>
      <view class="loc-row">
        <text>坐标：{{ location.lat ? location.lat.toFixed(5) + ', ' + location.lng.toFixed(5) : '等待定位...' }}</text>
      </view>
      <view class="loc-row" v-if="location.ts">
        <text>更新：{{ formatTime(location.ts) }} · 来源 {{ location.source }}</text>
      </view>
    </view>

    <!-- 操作菜单 -->
    <view class="card menu">
      <view class="menu-item" @tap="goAlarmSettings">🛡️ 报警设置 <span>›</span></view>
      <view class="menu-item" @tap="goHistory">🗺️ 历史轨迹 <span>›</span></view>
      <view class="menu-item" @tap="goDeviceStatus">📡 设备管理 <span>›</span></view>
      <view class="menu-item" @tap="goMember">💎 升级 Pro <span class="pro-tag">对比功能</span><span>›</span></view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { http } from '@/utils/request'
import { pawSocket } from '@/utils/ws'

const petId = ref(0)
const pet = ref<any>(null)
const location = ref<any>({ lat: null, lng: null, battery: 0, source: 'none', ts: 0 })
const device = ref<any>({ online: false, battery: null, sn: '' })

const breedText = computed(() => {
  if (!pet.value) return ''
  return pet.value.breed || (pet.value.type === 'cat' ? '猫咪' : '狗狗')
})

onLoad(async (options: any) => {
  petId.value = Number(options.id || 0)
  await loadPet()
  await loadRealtime()
  await loadDevice()
})

async function loadPet() {
  try {
    pet.value = await http.get(`/pets/${petId.value}`)
  } catch (e) {
    uni.showToast({ title: '加载宠物失败', icon: 'none' })
  }
}

async function loadRealtime() {
  try {
    const data = await http.get(`/location/realtime/${petId.value}`)
    if (data) location.value = data
  } catch (e) { /* 静默 */ }
}

async function loadDevice() {
  try {
    const devices = await http.get<any[]>('/devices')
    const bound = (devices || []).find((d: any) => d.pet_id === petId.value)
    if (bound) {
      device.value = {
        online: bound.status === 'online',
        battery: bound.battery,
        sn: bound.sn,
      }
    }
  } catch (e) { /* 静默 */ }
}

function formatTime(ts: number): string {
  const d = new Date(ts * 1000)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function goPro() { uni.navigateTo({ url: "/pages/member/member" }) }
function goBack() { uni.navigateBack() }
function goHistory() { uni.navigateTo({ url: '/pages/history/history?id=' + petId.value }) }
function goAlarmSettings() { uni.navigateTo({ url: '/pages/alarm-settings/alarm-settings?id=' + petId.value }) }
function goDeviceStatus() { uni.navigateTo({ url: '/pages/device-bind/device-bind' }) }
function goMember() { uni.navigateTo({ url: '/pages/member/member' }) }
</script>

<style scoped>
.page { min-height: 100vh; background: #f6f7fb; padding-bottom: 40rpx; }
.hero { text-align: center; padding: 30rpx 16rpx 40rpx; border-radius: 0 0 32rpx 32rpx; position: relative; }
.dog-bg { background: linear-gradient(180deg, #eff6ff, #f6f7fb); }
.cat-bg { background: linear-gradient(180deg, #fff7ed, #f6f7fb); }
.back { position: absolute; left: 24rpx; top: 12rpx; font-size: 44rpx; color: #333; }
.big-avatar { font-size: 80rpx; }
.hero-name { font-size: 36rpx; font-weight: 700; margin-top: 8rpx; }
.hero-sub { font-size: 24rpx; color: #9aa0a6; margin-top: 4rpx; }
.hero-status { margin-top: 16rpx; display: flex; gap: 12rpx; justify-content: center; }
.badge { font-size: 22rpx; padding: 6rpx 18rpx; border-radius: 999rpx; }
.badge.green { background: #f0fdf4; color: #22c55e; }
.badge.orange { background: #fff7ed; color: #f59e0b; }
.badge.gray { background: #f3f4f6; color: #9ca3af; }
.card { background: #fff; border-radius: 20rpx; padding: 28rpx; margin: 20rpx 24rpx; box-shadow: 0 4rpx 16rpx rgba(0,0,0,.04); }
.card-title { font-size: 30rpx; font-weight: 700; margin-bottom: 16rpx; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24rpx; }
.cell { font-size: 26rpx; font-weight: 600; }
.cell-icon { font-size: 36rpx; margin-bottom: 8rpx; }
.cell span { display: block; font-size: 22rpx; color: #9aa0a6; font-weight: 400; margin-top: 4rpx; }
.map-mini { position: relative; height: 220rpx; background: #eaf2ea; border-radius: 16rpx; margin-bottom: 14rpx; overflow: hidden; }
.map-mini.wide { height: 200rpx; }
.pin-sm { position: absolute; transform: translate(-50%,-100%); font-size: 44rpx; }
.loc-row { font-size: 24rpx; color: #6b7280; margin-top: 8rpx; }
.menu { padding: 8rpx 28rpx; }
.menu-item { display: flex; align-items: center; justify-content: space-between; padding: 24rpx 0; border-bottom: 1px solid #f3f4f6; font-size: 28rpx; font-weight: 600; }
.menu-item:last-child { border-bottom: none; }
.pro-tag { font-size: 20rpx; color: #f59e0b; background: #fffbeb; padding: 4rpx 12rpx; border-radius: 999rpx; }
.pro-chip{font-size:20rpx;background:#3d6cf5;color:#fff;padding:4rpx 14rpx;border-radius:999rpx;font-weight:600;vertical-align:middle}
.pro-chip.right{position:absolute;right:24rpx;top:24rpx}
</style>
