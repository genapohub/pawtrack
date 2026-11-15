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

        <view class="alarm-address">{{ alarmLine(alarm) }}</view>

        <!-- 操作按钮 -->
        <view v-if="alarm.status === 'active'" class="alarm-actions">
          <view class="act-btn ok" @tap="handleAlarm(alarm, 'handled')"> 确认</view>
          <view class="act-btn no" @tap="handleAlarm(alarm, 'false_positive')"> 误报</view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view v-else-if="!loading" class="empty-state">
      <view class="empty-icon"></view>
      <view class="empty-text">还没有围栏告警。宠物离开围栏后会显示在这里。</view>
    </view>

    <view v-if="loading" class="loading-text">加载中...</view>
    <view v-if="!loading" class="footer-note">处理或标记误报后，告警状态会更新。</view>
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
  leave_fence: '离开围栏',
  leave_fence_cat: '离开围栏',
  enter_fence: '进入围栏',
  low_battery: '低电量',
  low_battery_critical: '低电量',
  offline_warning: '设备离线',
  tamper_detected: '设备拆卸',
  fall_detected: '跌落检测',
}

const SEVERITY_MAP: Record<string, string> = {
  high: 'high',
  medium: 'medium',
  low: 'low',
}

function alarmIcon(_type: string): string {
  return ''
}

function alarmLine(alarm: any): string {
  const parts: string[] = []
  if (alarm.address) parts.push(`地址：${alarm.address}`)
  if (alarm.type === 'low_battery' || alarm.type === 'low_battery_critical') {
    const bat = alarm.battery ?? alarm.battery_level
    if (bat != null) parts.push(`电量 ${bat}%`)
    parts.push('优先级低于离线告警')
  }
  return parts.join(' · ')
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
  const hm = `${pad(d.getHours())}:${pad(d.getMinutes())}`
  const today = new Date()
  const startToday = new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime()
  const startThat = new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime()
  const diff = Math.round((startToday - startThat) / 86400000)
  if (diff === 0) return `今天 ${hm}`
  if (diff === 1) return `昨天 ${hm}`
  return `${d.getMonth() + 1}月${d.getDate()}日 ${hm}`
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
  background: var(--pt-bg);
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
  background: var(--pt-bg-muted);
  font-size: 26rpx;
  color: var(--pt-fg-2);
}

.filter-item.active {
  background: var(--pt-accent);
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
  background: var(--pt-danger-subtle);
}

.alarm-icon.medium {
  background: var(--pt-warning-subtle);
}

.alarm-icon.low {
  background: var(--pt-accent-subtle);
}

.alarm-info {
  flex: 1;
}

.alarm-title {
  font-size: 30rpx;
  font-weight: 600;
}

.alarm-time {
  font-size: 24rpx;
  color: var(--pt-fg-3);
  margin-top: 4rpx;
}

.alarm-status {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 999rpx;
}

.alarm-status.active {
  color: var(--pt-danger);
  background: var(--pt-danger-subtle);
}

.alarm-status.handled {
  color: var(--pt-success);
  background: var(--pt-success-subtle);
}

.alarm-status.false_positive {
  color: var(--pt-fg-3);
  background: var(--pt-bg-muted);
}

.alarm-address,
.alarm-coord {
  margin-top: 16rpx;
  font-size: 24rpx;
  color: var(--pt-fg-2);
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
  background: var(--pt-accent-subtle);
  color: var(--pt-accent);
}

.act-btn.no {
  background: var(--pt-bg-muted);
  color: var(--pt-fg-2);
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
  color: var(--pt-fg-3);
  font-size: 28rpx;
}

.loading-text {
  text-align: center;
  color: var(--pt-fg-3);
  padding: 40rpx;
  font-size: 26rpx;
}
.footer-note { margin: 24rpx 40rpx 0; font-size: 22rpx; color: var(--pt-fg-3); line-height: 1.5; }
</style>
