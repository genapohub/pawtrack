<template>
  <view class="page">
    <!-- 筛选栏 -->
    <view class="filter-bar">
      <view
        v-for="f in filters"
        :key="f.value"
        class="filter-item"
        :class="{ active: filter === f.value }"
        @tap="filter = f.value"
      >{{ f.label }}</view>
    </view>

    <!-- 报警列表 -->
    <view v-if="alarms.length > 0" class="alarm-list">
      <view v-for="alarm in alarms" :key="alarm.id" class="card alarm-card">
        <view class="alarm-head">
          <view class="alarm-icon" :class="severityClass(alarm.severity)">
            {{ alarmIcon(alarm.type) }}
          </view>
          <view class="alarm-info">
            <view class="alarm-title">{{ alarmTitle(alarm) }}</view>
            <view class="alarm-time">{{ formatTime(alarm.created_at) }}</view>
          </view>
          <view class="alarm-status" :class="alarm.status">
            {{ statusLabel(alarm.status) }}
          </view>
        </view>

        <view v-if="alarm.address" class="alarm-address">📍 {{ alarm.address }}</view>
        <view v-if="alarm.lat" class="alarm-coord">
          {{ alarm.lat.toFixed(5) }}, {{ alarm.lng.toFixed(5) }}
        </view>

        <!-- 操作按钮 -->
        <view v-if="alarm.status === 'active'" class="alarm-actions">
          <view class="act-btn ok" @tap="handleAlarm(alarm, 'handled')">✓ 确认</view>
          <view class="act-btn no" @tap="handleAlarm(alarm, 'false_positive')">✗ 误报</view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view v-else-if="!loading" class="empty-state">
      <view class="empty-icon">🔔</view>
      <view class="empty-text">暂无报警记录</view>
    </view>

    <view v-if="loading" class="loading-text">加载中...</view>
  </view>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { http } from '@/utils/request'

const filters = [
  { label: '全部', value: '' },
  { label: '待处理', value: 'active' },
  { label: '已确认', value: 'handled' },
  { label: '误报', value: 'false_positive' },
]

const filter = ref('')
const alarms = ref<any[]>([])
const loading = ref(false)

const TYPE_MAP: Record<string, string> = {
  leave_fence: '🏃 离开围栏',
  leave_fence_cat: '🏃 猫咪离开围栏',
  enter_fence: '🏠 进入围栏',
  low_battery: '🔋 电量不足',
  low_battery_critical: '🔋 电量严重不足',
  offline_warning: '📡 设备离线',
  tamper_detected: '⚠️ 防拆报警',
  fall_detected: '🆘 跌落检测',
}

const SEVERITY_MAP: Record<string, string> = {
  high: 'high',
  medium: 'medium',
  low: 'low',
}

function alarmIcon(type: string): string {
  return TYPE_MAP[type]?.split(' ')[0] || '🔔'
}

function alarmTitle(alarm: any): string {
  return TYPE_MAP[alarm.type] || alarm.type
}

function severityClass(severity: string): string {
  return SEVERITY_MAP[severity] || 'low'
}

function statusLabel(status: string): string {
  return { active: '待处理', handled: '已确认', false_positive: '误报' }[status] || status
}

function formatTime(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getMonth() + 1}月${d.getDate()}日 ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function loadAlarms() {
  loading.value = true
  try {
    const params: any = { page: 1, size: 50 }
    if (filter.value) params.status = filter.value
    const qs = Object.entries(params)
      .map(([k, v]) => `${k}=${v}`)
      .join('&')
    const data = await http.get<any>(`/alarms?${qs}`)
    alarms.value = (data?.items || data || []).map((a: any) => ({
      ...a,
      lat: a.lat !== null ? Number(a.lat) : null,
      lng: a.lng !== null ? Number(a.lng) : null,
    }))
  } catch (e: any) {
    uni.showToast({ title: e.message || '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

async function handleAlarm(alarm: any, status: string) {
  try {
    await http.put(`/alarms/${alarm.id}/handle`, { status })
    uni.showToast({ title: status === 'handled' ? '已确认处理' : '已标记误报', icon: 'success' })
    loadAlarms()
  } catch (e: any) {
    uni.showToast({ title: e.message || '操作失败', icon: 'none' })
  }
}

watch(filter, loadAlarms)
onShow(loadAlarms)
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f6f7fb;
  padding-bottom: 40rpx;
}

/* 筛选 */
.filter-bar {
  display: flex;
  gap: 16rpx;
  padding: 24rpx;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 10;
}

.filter-item {
  padding: 12rpx 28rpx;
  border-radius: 999rpx;
  background: #f3f4f6;
  font-size: 26rpx;
  color: #6b7280;
}

.filter-item.active {
  background: #3d6cf5;
  color: #fff;
  font-weight: 600;
}

/* 报警卡片 */
.alarm-card {
  margin: 20rpx 24rpx;
}

.alarm-head {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.alarm-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
}

.alarm-icon.high {
  background: #fef2f2;
}

.alarm-icon.medium {
  background: #fffbeb;
}

.alarm-icon.low {
  background: #f0f9ff;
}

.alarm-info {
  flex: 1;
}

.alarm-title {
  font-size: 30rpx;
  font-weight: 700;
}

.alarm-time {
  font-size: 24rpx;
  color: #9aa0a6;
  margin-top: 4rpx;
}

.alarm-status {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 999rpx;
}

.alarm-status.active {
  color: #ef4444;
  background: #fef2f2;
}

.alarm-status.handled {
  color: #22c55e;
  background: #f0fdf4;
}

.alarm-status.false_positive {
  color: #9aa0a6;
  background: #f3f4f6;
}

.alarm-address,
.alarm-coord {
  margin-top: 16rpx;
  font-size: 24rpx;
  color: #6b7280;
}

.alarm-actions {
  display: flex;
  gap: 20rpx;
  margin-top: 20rpx;
}

.act-btn {
  flex: 1;
  text-align: center;
  padding: 14rpx 0;
  border-radius: 12rpx;
  font-size: 26rpx;
  font-weight: 600;
}

.act-btn.ok {
  background: #eef2ff;
  color: #3d6cf5;
}

.act-btn.no {
  background: #f3f4f6;
  color: #6b7280;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 140rpx 0;
}

.empty-icon {
  font-size: 80rpx;
}

.empty-text {
  margin-top: 20rpx;
  color: #9aa0a6;
  font-size: 28rpx;
}

.loading-text {
  text-align: center;
  color: #9aa0a6;
  padding: 40rpx;
  font-size: 26rpx;
}
</style>
