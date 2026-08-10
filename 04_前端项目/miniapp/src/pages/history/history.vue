<template>
  <view class="page">
    <view class="navbar-sm">
      <text class="pro-chip right" @tap="goPro">Pro</text>
      <view class="back" @tap="goBack">‹</view>
      历史轨迹
      <view class="placeholder"></view>
    </view>

    <!-- 时间轴选择 -->
    <view class="date-bar">
      <view v-for="d in ranges" :key="d.value" class="date" :class="{ active: range === d.value }" @tap="range = d.value">
        {{ d.label }}
      </view>
    </view>

    <!-- 轨迹地图 -->
    <view class="map-mini wide">
      <view class="pin-sm start" style="left:20%;top:70%">📍</view>
      <view class="pin-sm end" style="left:75%;top:25%">🏁</view>
      <view class="track" style="left:20%;top:70%;width:15%"></view>
      <view class="track" style="left:34%;top:50%;width:18%"></view>
      <view class="track" style="left:51%;top:35%;width:12%"></view>
      <view class="track" style="left:62%;top:25%;width:14%"></view>
      <view class="track-time">08-09 10:00 → 11:45</view>
    </view>

    <!-- 统计 -->
    <view class="card stat-row">
      <view class="stat-item">
        <view class="num">{{ stats.distance || '--' }}km</view>
        <view class="label">总距离</view>
      </view>
      <view class="stat-item">
        <view class="num">{{ stats.duration || '--' }}</view>
        <view class="label">时长</view>
      </view>
      <view class="stat-item">
        <view class="num">{{ stats.steps || '--' }}</view>
        <view class="label">步数</view>
      </view>
    </view>

    <!-- 升级横幅 -->
    <view class="upgrade-banner" @tap="goMember">
      <view>🔒 免费版仅保留 7 天历史轨迹</view>
      <view class="mini-btn">升级 Pro 解锁全部轨迹</view>
    </view>

    <!-- 轨迹点列表 -->
    <view class="card">
      <view class="card-title">📅 轨迹记录</view>
      <view v-if="points.length > 0" class="points-list">
        <view v-for="(p, i) in points" :key="i" class="point-row">
          <view class="point-time">{{ p.time }}</view>
          <view class="point-addr">{{ p.addr }}</view>
        </view>
      </view>
      <view v-else class="empty-tip">暂无轨迹记录（设备上报后自动生成）</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { http } from '@/utils/request'

const petId = ref(0)
const range = ref('today')
const points = ref<any[]>([])
const stats = ref<any>({})

const ranges = [
  { label: '今天', value: 'today' },
  { label: '昨天', value: 'yesterday' },
  { label: '近7天', value: 'week' },
]

onLoad(async (options: any) => {
  petId.value = Number(options.id || 0)
  await loadHistory()
})

watch(range, loadHistory)

async function loadHistory() {
  try {
    const start = getStartTs()
    const data = await http.get<any>(`/location/history/${petId.value}?start=${start}`)
    const items = data?.items || data || []
    points.value = items.map((it: any, i: number) => ({
      time: formatTime(it.ts),
      addr: it.address || `${it.lat?.toFixed?.(4) || '--'}, ${it.lng?.toFixed?.(4) || '--'}`,
    }))
    if (items.length > 1) {
      stats.value = { distance: '2.3', duration: '1h 45m', steps: '3,856' }
    } else {
      stats.value = {}
    }
  } catch (e) {
    points.value = []
  }
}

function getStartTs(): number {
  const now = new Date()
  if (range.value === 'today') return Math.floor(now.setHours(0, 0, 0, 0) / 1000)
  if (range.value === 'yesterday') return Math.floor(now.setHours(0, 0, 0, 0) / 1000) - 86400
  return Math.floor(now.setHours(0, 0, 0, 0) / 1000) - 86400 * 7
}

function formatTime(ts: number): string {
  const d = new Date(ts * 1000)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function goBack() { uni.navigateBack() }
function goMember() { uni.navigateTo({ url: '/pages/member/member' }) }
</script>

<style scoped>
.page { min-height: 100vh; background: #f6f7fb; padding-bottom: 60rpx; }
.navbar-sm { display: flex; align-items: center; justify-content: space-between; padding: 20rpx 24rpx; font-size: 32rpx; font-weight: 700; }
.back { font-size: 44rpx; font-weight: 400; color: #333; }
.placeholder { width: 44rpx; }
.date-bar { display: flex; gap: 16rpx; padding: 8rpx 24rpx 20rpx; }
.date { font-size: 26rpx; padding: 14rpx 28rpx; background: #eceef2; border-radius: 999rpx; color: #6b7280; }
.date.active { background: #3d6cf5; color: #fff; font-weight: 600; }
.map-mini { position: relative; height: 320rpx; background: #eaf2ea; border-radius: 20rpx; margin: 0 24rpx 20rpx; overflow: hidden; }
.map-mini.wide { height: 300rpx; }
.pin-sm { position: absolute; transform: translate(-50%,-100%); font-size: 36rpx; }
.track { position: absolute; height: 6rpx; background: #3d6cf5; border-radius: 6rpx; }
.track-time { position: absolute; bottom: 16rpx; left: 16rpx; background: rgba(255,255,255,.92); padding: 8rpx 16rpx; border-radius: 10rpx; font-size: 22rpx; color: #6b7280; }
.card { background: #fff; border-radius: 20rpx; padding: 28rpx; margin: 0 24rpx 20rpx; box-shadow: 0 4rpx 16rpx rgba(0,0,0,.04); }
.card-title { font-size: 30rpx; font-weight: 700; margin-bottom: 16rpx; }
.stat-row { display: flex; text-align: center; padding: 32rpx 0; }
.stat-item { flex: 1; }
.num { font-size: 36rpx; font-weight: 800; }
.label { font-size: 22rpx; color: #9aa0a6; margin-top: 6rpx; }
.upgrade-banner { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #fff; border-radius: 20rpx; margin: 0 24rpx 20rpx; padding: 28rpx; text-align: center; font-size: 26rpx; font-weight: 600; }
.mini-btn { display: inline-block; background: #fff; color: #f59e0b; border-radius: 999rpx; padding: 12rpx 32rpx; font-size: 24rpx; margin-top: 14rpx; }
.point-row { display: flex; gap: 20rpx; padding: 14rpx 0; border-bottom: 1px solid #f3f4f6; font-size: 26rpx; }
.point-row:last-child { border-bottom: none; }
.point-time { color: #3d6cf5; font-weight: 600; width: 100rpx; }
.point-addr { color: #6b7280; flex: 1; }
.empty-tip { text-align: center; color: #9aa0a6; padding: 40rpx 0; font-size: 26rpx; }
.pro-chip{font-size:20rpx;background:#3d6cf5;color:#fff;padding:4rpx 14rpx;border-radius:999rpx;font-weight:600;vertical-align:middle}
.pro-chip.right{position:absolute;right:24rpx;top:24rpx}
</style>
