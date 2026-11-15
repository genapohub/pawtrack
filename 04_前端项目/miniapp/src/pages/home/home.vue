<template>
  <view class="home-page">
    <view class="status-spacer" />
    <view class="nav">首页</view>
    <view class="mock-banner">本地 Mock 预览 · 非真实硬件 / 微信 / 短信 / 地图 / 支付</view>

    <view class="body">
      <template v-if="pageState === 'loading'">
        <view class="map schematic muted">
          <view class="map-grid" />
          <view class="map-cap">定位中... 当前为本地预览，不模拟真实刷新间隔</view>
        </view>
      </template>

      <template v-else-if="pageState === 'empty'">
        <view class="map schematic muted">
          <view class="map-grid" />
          <view class="map-cap">还没有位置记录，请先添加宠物并绑定设备（当前为本地预览数据）</view>
        </view>
        <view class="pt-card empty-card">
          <view class="empty-title">还没有宠物，先添加一只。</view>
          <view class="empty-desc">添加后可绑定定位器，查看示意位置与围栏。</view>
        </view>
        <view class="btn-primary add-btn" @tap="goAddPet">添加宠物</view>
      </template>

      <template v-else>
        <view class="map schematic" :class="{ unconfigured: mapUnconfigured }" @tap="goFirstPet">
          <view class="map-grid" />
          <view v-if="!mapUnconfigured" class="fence" />
          <view v-if="!mapUnconfigured" class="pin" />
          <view class="map-cap">{{ mapCaption }}</view>
        </view>

        <view v-if="mapUnconfigured" class="warn-box map-warn">
          地图 Key 未接入。页面不会白屏，位置以示意坐标和文案展示。
        </view>

        <view
          v-for="pet in pets"
          :key="pet.id"
          class="pt-card pet-card"
          @tap="goPetDetail(pet.id)"
        >
          <view class="pet-head">
            <view class="avatar-mark" :class="pet.type === 'cat' ? 'avatar-cat' : 'avatar-dog'">
              {{ nameMark(pet.name) }}
            </view>
            <view class="pet-meta">
              <view class="pet-name">{{ pet.name }}</view>
              <view class="pet-sub">{{ petSubtitle(pet) }}</view>
            </view>
            <view class="pet-flags">
              <text class="tag" :class="placeClass(pet)">{{ placeLabel(pet) }}</text>
              <text class="tag tag-success">在线 {{ batteryOf(pet) }}%</text>
            </view>
          </view>
          <view class="pet-loc">{{ lastLocationText(pet) }}</view>
        </view>

        <view class="btn-primary add-btn" @tap="goAddPet">添加宠物</view>
        <view class="foot-note">地图钉与列表均可进入宠物详情。社交页本轮不做必交付，底栏仅保留入口。</view>
      </template>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { http } from '@/utils/request'
import { isLoggedIn } from '@/utils/auth'
import { USE_MOCK, AMAP_KEY } from '@/utils/config'

interface PetInfo {
  id: number
  name: string
  type: string
  breed: string | null
  fence_enabled?: boolean
  fence_radius?: number
}

const SCHEMA_LAT = 31.23
const SCHEMA_LNG = 121.473

const pets = ref<PetInfo[]>([])
const locations = ref<Record<number, { lat: number; lng: number; battery: number; source: string; ts: number }>>({})
const loading = ref(true)
const loaded = ref(false)

const mapUnconfigured = computed(() => !USE_MOCK && !AMAP_KEY)
const pageState = computed(() => {
  if (loading.value && !loaded.value) return 'loading'
  if (!pets.value.length) return 'empty'
  return 'default'
})

const mapCaption = computed(() => {
  if (mapUnconfigured.value) {
    return `地图服务未配置，仅显示示意坐标 ${SCHEMA_LAT.toFixed(3)}, ${SCHEMA_LNG.toFixed(3)}，非实地地图服务`
  }
  return `示意位置，非实地地图服务 · 示意坐标 ${SCHEMA_LAT.toFixed(3)}, ${SCHEMA_LNG.toFixed(3)}`
})

function nameMark(name: string) {
  return (name || '宠').slice(0, 1)
}

function petSubtitle(pet: PetInfo) {
  const kind = pet.type === 'cat' ? '猫' : '狗'
  const breed = pet.breed ? shortBreed(pet.breed) : kind
  const bound = '已绑定定位器'
  return `${breed} · ${kind} · ${bound}`
}

function shortBreed(breed: string) {
  return breed.replace('英国短毛猫', '英短').replace('英国短毛', '英短')
}

function placeLabel(pet: PetInfo) {
  return pet.type === 'cat' ? '宅家' : '户外'
}

function placeClass(pet: PetInfo) {
  return pet.type === 'cat' ? 'tag-muted' : 'tag-warning'
}

function batteryOf(pet: PetInfo) {
  return locations.value[pet.id]?.battery ?? (pet.type === 'cat' ? 72 : 88)
}

function lastLocationText(pet: PetInfo) {
  if (pet.type === 'dog') {
    return '最后位置（示意）：滨江步道 · 来源 GPS · 刚刚。预览不模拟真实刷新间隔。'
  }
  const source = locations.value[pet.id]?.source === 'gps' ? 'GPS' : 'Wi-Fi'
  return `最后位置（示意）：小区中心点附近 · 来源 ${source} · 2 分钟前`
}

async function loadPets() {
  loading.value = true
  try {
    const list = await http.get<any[]>('/pets')
    pets.value = list || []
    await Promise.all(pets.value.map(async (p) => {
      try {
        const data = await http.get<any>(`/location/realtime/${p.id}`)
        if (data) {
          locations.value = {
            ...locations.value,
            [p.id]: {
              lat: data.lat ?? SCHEMA_LAT,
              lng: data.lng ?? SCHEMA_LNG,
              battery: data.battery || 0,
              source: data.source || 'none',
              ts: data.ts || 0,
            },
          }
        }
      } catch (e) { /* 示意坐标仍可展示 */ }
    }))
  } catch (e) {
    pets.value = []
  } finally {
    loading.value = false
    loaded.value = true
  }
}

function goAddPet() {
  uni.navigateTo({ url: '/pages/pet-add/pet-add' })
}

function goPetDetail(id: number) {
  uni.navigateTo({ url: `/pages/pet-detail/pet-detail?id=${id}` })
}

function goFirstPet() {
  if (pets.value[0]) goPetDetail(pets.value[0].id)
}

onShow(() => {
  if (!isLoggedIn()) {
    uni.reLaunch({ url: '/pages/login/login' })
    return
  }
  loadPets()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: var(--pt-bg);
  padding-bottom: 48rpx;
}

.status-spacer {
  height: var(--status-bar-height, 44px);
  background: var(--pt-surface);
}

.nav {
  height: 88rpx;
  background: var(--pt-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 34rpx;
  font-weight: 600;
  color: var(--pt-fg);
}

.body {
  padding: 24rpx 0 40rpx;
}

.map {
  margin: 0 32rpx 24rpx;
  height: 360rpx;
  border-radius: 28rpx;
  overflow: hidden;
  position: relative;
}

.schematic {
  background: var(--pt-map);
}

.schematic.muted .fence,
.schematic.muted .pin {
  display: none;
}

.map-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(var(--pt-map-line) 1rpx, transparent 1rpx),
    linear-gradient(90deg, var(--pt-map-line) 1rpx, transparent 1rpx);
  background-size: 72rpx 72rpx;
  opacity: 0.7;
}

.fence {
  position: absolute;
  width: 240rpx;
  height: 240rpx;
  border-radius: 50%;
  border: 4rpx dashed var(--pt-accent);
  background: var(--pt-accent-soft);
  left: 50%;
  top: 42%;
  transform: translate(-50%, -50%);
}

.pin {
  position: absolute;
  width: 20rpx;
  height: 20rpx;
  border-radius: 50%;
  background: var(--pt-pin);
  left: 50%;
  top: 42%;
  transform: translate(-50%, -50%);
}

.map-cap {
  position: absolute;
  left: 16rpx;
  right: 16rpx;
  bottom: 16rpx;
  background: var(--pt-fg-scrim);
  color: var(--pt-fg-inv);
  font-size: 22rpx;
  font-weight: 400;
  line-height: 1.4;
  padding: 12rpx 20rpx;
  border-radius: 16rpx;
}

.map-warn {
  margin: 0 32rpx 24rpx;
}

.pet-card {
  margin-bottom: 20rpx;
}

.pet-head {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.pet-meta {
  flex: 1;
  min-width: 0;
}

.pet-name {
  font-size: 32rpx;
  font-weight: 500;
  color: var(--pt-fg);
}

.pet-sub {
  margin-top: 4rpx;
  font-size: 22rpx;
  font-weight: 400;
  color: var(--pt-fg-2);
}

.pet-flags {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8rpx;
}

.pet-loc {
  margin-top: 20rpx;
  font-size: 24rpx;
  font-weight: 400;
  color: var(--pt-fg-2);
  line-height: 1.5;
}

.add-btn {
  margin: 12rpx 32rpx 16rpx;
}

.foot-note,
.empty-desc {
  margin: 0 40rpx;
  font-size: 22rpx;
  font-weight: 400;
  color: var(--pt-fg-3);
  line-height: 1.5;
}

.empty-card {
  text-align: left;
}

.empty-title {
  font-size: 30rpx;
  font-weight: 500;
  color: var(--pt-fg);
  margin-bottom: 8rpx;
}
</style>
