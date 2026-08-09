<template>
  <view class="home-page">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <view class="nav-title">🐾 宠迹</view>
      <view v-if="isDev" class="dev-badge">DEV</view>
      <view class="nav-right">
        <view class="ws-dot" :class="{ online: wsConnected }"></view>
        <view class="nav-icon" @tap="goAlarms">🔔</view>
      </view>
    </view>

    <!-- 地图区域 -->
    <view class="map-wrap">
      <map
        id="pawMap"
        class="paw-map"
        :latitude="centerLat"
        :longitude="centerLng"
        :scale="15"
        :markers="markers"
        :circles="circles"
        show-location
      ></map>
      <!-- 坐标浮标 -->
      <view class="coord-badge">
        {{ location.lat ? location.lat.toFixed(4) + ', ' + location.lng.toFixed(4) : '等待定位...' }}
      </view>
    </view>

    <!-- 宠物选择栏 -->
    <scroll-view v-if="pets.length > 0" class="pet-bar" scroll-x>
      <view
        v-for="pet in pets"
        :key="pet.id"
        class="pet-chip"
        :class="{ active: selectedPet?.id === pet.id }"
        @tap="selectPet(pet)"
      >
        {{ pet.type === 'cat' ? '🐱' : '🐶' }} {{ pet.name }}
      </view>
    </scroll-view>

    <!-- 位置信息卡片 -->
    <view class="card info-card">
      <template v-if="selectedPet">
        <view class="pet-head" @tap="goPetDetail">
          <view class="pet-avatar" :class="selectedPet.type === 'cat' ? 'cat-bg' : 'dog-bg'">
            {{ selectedPet.type === 'cat' ? '🐱' : '🐶' }}
          </view>
          <view class="pet-meta">
            <view class="pet-name">{{ selectedPet.name }}</view>
            <view class="pet-breed">
              {{ selectedPet.breed || (selectedPet.type === 'cat' ? '猫咪' : '狗狗') }}
            </view>
          </view>
          <view class="status-badge" :class="location.source !== 'none' ? 'online' : 'offline'">
            {{ location.source !== 'none' ? '● 在线' : '○ 离线' }}
          </view>
        </view>

        <view class="loc-row">
          <text class="loc-item">🔋 {{ location.battery }}%</text>
          <text class="loc-item">📡 {{ location.source }}</text>
          <text v-if="location.ts" class="loc-item">🕐 {{ formatTime(location.ts) }}</text>
        </view>

        <view v-if="selectedPet.fence_enabled" class="fence-tip">
          🛡️ 安全围栏已开启 · 半径 {{ selectedPet.fence_radius }}m
        </view>

        <!-- 模拟上报按钮（开发测试） -->
        <view
          class="sim-btn"
          @tap="simulateLocation"
        >
          {{ simulating ? '📍 模拟上报中...' : '📍 模拟定位上报（测试）' }}
        </view>
      </template>

      <template v-else>
        <view class="empty-state">
          <view class="empty-icon">🐾</view>
          <view class="empty-text">还没有添加宠物</view>
          <view class="empty-action" @tap="goAddPet">+ 添加第一只宠物</view>
        </view>
      </template>
    </view>

    <!-- 底部操作栏 -->
    <view v-if="selectedPet" class="bottom-actions">
      <view class="action-btn" @tap="goAddPet">➕ 添加宠物</view>
      <view class="action-btn" @tap="goBindDevice">📡 绑定设备</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { onShow, onHide } from '@dcloudio/uni-app'
import { http } from '@/utils/request'
import { pawSocket } from '@/utils/ws'
import { isLoggedIn } from '@/utils/auth'

const isDev = true

interface PetInfo {
  id: number
  name: string
  type: string
  breed: string | null
  fence_enabled: boolean
  fence_radius: number
}

const pets = ref<PetInfo[]>([])
const selectedPet = ref<PetInfo | null>(null)
const location = ref({
  lat: null as number | null,
  lng: null as number | null,
  battery: 0,
  source: 'none',
  ts: 0,
})
const wsConnected = ref(false)
const simulating = ref(false)
const loaded = ref(false)

// 郑州默认坐标
const DEFAULT_LAT = 34.7466
const DEFAULT_LNG = 113.6253

const centerLat = computed(() => location.value.lat || DEFAULT_LAT)
const centerLng = computed(() => location.value.lng || DEFAULT_LNG)

const markers = computed(() => {
  if (!location.value.lat || !location.value.lng || !selectedPet.value) return []
  return [{
    id: 1,
    latitude: location.value.lat,
    longitude: location.value.lng,
    title: selectedPet.value.name,
    iconPath: selectedPet.value.type === 'cat'
      ? '/static/marker-cat.png'
      : '/static/marker-dog.png',
    width: 32,
    height: 32,
  }]
})

const circles = computed(() => {
  if (!selectedPet.value?.fence_enabled || !location.value.lat) return []
  return [{
    latitude: location.value.lat,
    longitude: location.value.lng,
    radius: selectedPet.value.fence_radius,
    color: '#3D6CF533',
    fillColor: '#3D6CF51A',
    strokeWidth: 2,
  }]
})

/** 加载宠物列表 */
async function loadPets() {
  try {
    const list = await http.get<any[]>('/pets')
    pets.value = list || []
    if (list.length > 0) {
      const first = list[0]
      // 保持当前选中的宠物
      const keep = list.find((p) => p.id === selectedPet.value?.id)
      selectPet(keep || first)
    } else {
      selectedPet.value = null
    }
  } catch (e: any) {
    console.error('加载宠物失败', e)
  }
}

/** 获取实时位置 */
async function fetchRealtime(petId: number) {
  try {
    const data = await http.get<any>(`/location/realtime/${petId}`)
    if (data) {
      location.value = {
        lat: data.lat ?? null,
        lng: data.lng ?? null,
        battery: data.battery || 0,
        source: data.source || 'none',
        ts: data.ts || 0,
      }
    }
  } catch (e) {
    // 静默
  }
}

/** 切换宠物 */
function selectPet(pet: PetInfo) {
  selectedPet.value = pet
  fetchRealtime(pet.id)
  pawSocket.subscribe('location', pet.id)
}

/** 模拟定位上报（开发测试） */
async function simulateLocation() {
  if (!selectedPet.value) {
    uni.showToast({ title: '请先添加宠物', icon: 'none' })
    return
  }

  try {
    const devices = await http.get<any[]>('/devices')
    if (!devices || devices.length === 0) {
      uni.showToast({ title: '请先绑定设备', icon: 'none' })
      goBindDevice()
      return
    }

    const device = devices[0]
    simulating.value = true
    let step = 0

    uni.showToast({ title: '开始模拟定位上报...', icon: 'none' })

    const simTimer = setInterval(async () => {
      step++
      const lat = DEFAULT_LAT + (Math.random() - 0.5) * 0.001 * step
      const lng = DEFAULT_LNG + (Math.random() - 0.5) * 0.001 * step

      try {
        await http.post('/location/upload', {
          device_id: device.id,
          lat,
          lng,
          accuracy: 5.0 + Math.random() * 10,
          battery: Math.max(20, 100 - step),
          source: 'gps',
          ts: Math.floor(Date.now() / 1000),
        })
        // 本地更新位置
        location.value = {
          lat, lng,
          battery: Math.max(20, 100 - step),
          source: 'gps',
          ts: Math.floor(Date.now() / 1000),
        }
      } catch (e) {
        // 静默
      }

      if (step >= 20) {
        clearInterval(simTimer)
        simulating.value = false
        uni.showToast({ title: '模拟上报完成', icon: 'success' })
      }
    }, 2000)
  } catch (e: any) {
    uni.showToast({ title: e.message || '模拟失败', icon: 'none' })
    simulating.value = false
  }
}

function formatTime(ts: number): string {
  const d = new Date(ts * 1000)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function goAddPet() {
  uni.navigateTo({ url: '/pages/pet-add/pet-add' })
}

function goPetDetail() {
  if (!selectedPet.value) return
  uni.navigateTo({ url: `/pages/pet-detail/pet-detail?id=${selectedPet.value.id}` })
}

function goBindDevice() {
  uni.navigateTo({ url: '/pages/device-bind/device-bind' })
}

function goAlarms() {
  uni.switchTab({ url: '/pages/alarms/alarms' })
}

onShow(() => {
  // 未登录跳登录页
  if (!isLoggedIn()) {
    uni.reLaunch({ url: '/pages/login/login' })
    return
  }
  if (!loaded.value) {
    loadPets()
    loaded.value = true
  } else {
    loadPets() // 刷新（从添加页返回）
  }
})

onHide(() => {
  // 不主动断开，保持后台接收
})

onMounted(() => {
  // WebSocket 消息监听
  pawSocket.on('connected', () => {
    wsConnected.value = true
    if (selectedPet.value) pawSocket.subscribe('location', selectedPet.value.id)
    pawSocket.subscribe('alarm')
  })
  pawSocket.on('location', (msg: any) => {
    if (selectedPet.value && msg.pet_id === selectedPet.value.id) {
      location.value = {
        lat: msg.lat,
        lng: msg.lng,
        battery: msg.battery,
        source: msg.source,
        ts: msg.ts,
      }
    }
  })
  pawSocket.on('alarm', (msg: any) => {
    uni.showToast({ title: `⚠️ 报警：${msg.alarm_type}`, icon: 'none' })
  })
  pawSocket.connect()
})

onUnmounted(() => {
  pawSocket.close()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f6f7fb;
  padding-bottom: 140rpx;
}

/* 导航栏 */
.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 88rpx 32rpx 20rpx;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 10;
}

.nav-title {
  font-size: 36rpx;
  font-weight: 700;
}

.dev-badge {
  background: #f59e0b;
  color: #fff;
  font-size: 20rpx;
  font-weight: 600;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  letter-spacing: 2rpx;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.ws-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: #d1d5db;
}

.ws-dot.online {
  background: #22c55e;
}

.nav-icon {
  font-size: 40rpx;
}

/* 地图 */
.map-wrap {
  position: relative;
  height: 420rpx;
  margin: 16rpx 24rpx;
  border-radius: 24rpx;
  overflow: hidden;
}

.paw-map {
  width: 100%;
  height: 100%;
}

.coord-badge {
  position: absolute;
  left: 16rpx;
  bottom: 16rpx;
  background: rgba(255, 255, 255, 0.92);
  padding: 8rpx 16rpx;
  border-radius: 12rpx;
  font-size: 22rpx;
  color: #6b7280;
}

/* 宠物选择栏 */
.pet-bar {
  display: flex;
  white-space: nowrap;
  padding: 8rpx 24rpx;
  background: #fff;
}

.pet-chip {
  display: inline-block;
  margin-right: 16rpx;
  padding: 12rpx 28rpx;
  border-radius: 999rpx;
  background: #f3f4f6;
  font-size: 26rpx;
  font-weight: 600;
  color: #1f2329;
}

.pet-chip.active {
  background: #3d6cf5;
  color: #fff;
}

/* 信息卡片 */
.info-card {
  margin: 20rpx 24rpx;
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
}

.pet-head {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.pet-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
}

.cat-bg {
  background: #fff7ed;
}

.dog-bg {
  background: #eff6ff;
}

.pet-meta {
  flex: 1;
}

.pet-name {
  font-size: 32rpx;
  font-weight: 700;
}

.pet-breed {
  font-size: 24rpx;
  color: #9aa0a6;
}

.status-badge {
  font-size: 24rpx;
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
}

.status-badge.online {
  color: #22c55e;
  background: #f0fdf4;
}

.status-badge.offline {
  color: #9aa0a6;
  background: #f3f4f6;
}

.loc-row {
  display: flex;
  gap: 28rpx;
  margin-top: 24rpx;
  font-size: 26rpx;
  color: #6b7280;
}

.fence-tip {
  margin-top: 16rpx;
  font-size: 24rpx;
  color: #22c55e;
}

.sim-btn {
  margin-top: 24rpx;
  text-align: center;
  padding: 20rpx;
  border-radius: 16rpx;
  border: 2rpx solid #3d6cf5;
  color: #3d6cf5;
  font-size: 26rpx;
  font-weight: 600;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 0;
}

.empty-icon {
  font-size: 80rpx;
}

.empty-text {
  margin-top: 16rpx;
  color: #9aa0a6;
  font-size: 28rpx;
}

.empty-action {
  margin-top: 20rpx;
  color: #3d6cf5;
  font-weight: 600;
  font-size: 28rpx;
}

/* 底部操作 */
.bottom-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  gap: 20rpx;
  padding: 20rpx 32rpx calc(20rpx + env(safe-area-inset-bottom));
  background: #fff;
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.04);
}

.action-btn {
  flex: 1;
  text-align: center;
  padding: 20rpx;
  border-radius: 44rpx;
  background: #f3f4f6;
  font-size: 28rpx;
  font-weight: 600;
}

.action-btn:first-child {
  background: #3d6cf5;
  color: #fff;
}
</style>
