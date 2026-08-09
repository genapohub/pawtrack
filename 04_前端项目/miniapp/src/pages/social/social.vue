<template>
  <view class="page">
    <!-- 附近宠物 -->
    <view class="section-title">
      <text>🐾 附近的宠物</text>
      <text class="refresh" @tap="loadNearby">刷新</text>
    </view>

    <view v-if="nearby.length > 0" class="nearby-list">
      <view v-for="p in nearby" :key="p.pet_id || p.id" class="card nearby-card">
        <view class="pet-avatar" :class="p.type === 'cat' ? 'cat-bg' : 'dog-bg'">
          {{ p.type === 'cat' ? '🐱' : '🐶' }}
        </view>
        <view class="pet-info">
          <view class="pet-name">{{ p.name }}</view>
          <view class="pet-detail">
            {{ p.breed || (p.type === 'cat' ? '猫咪' : '狗狗') }} · 距离 {{ p.distance }}m
          </view>
          <view class="pet-detail">{{ p.nickname ? '@' + p.nickname : '' }}</view>
        </view>
        <view class="meet-btn" @tap="startMeet(p)">打招呼</view>
      </view>
    </view>

    <view v-else class="empty-state">
      <view class="empty-icon">🐾</view>
      <view class="empty-text">附近还没有宠物，去遛弯看看吧</view>
    </view>

    <!-- 我的碰头记录 -->
    <view class="section-title"><text>📅 我的碰头记录</text></view>

    <view v-if="meets.length > 0" class="meet-list">
      <view v-for="m in meets" :key="m.id" class="card meet-card">
        <view class="meet-head">
          <view class="meet-emoji">{{ meetEmoji(m.status) }}</view>
          <view class="meet-info">
            <view class="meet-title">{{ meetTitle(m) }}</view>
            <view class="meet-time">{{ formatTime(m.created_at) }}</view>
          </view>
          <view class="meet-status" :class="m.status">{{ meetStatusLabel(m.status) }}</view>
        </view>
        <view v-if="m.points_awarded" class="meet-points">
          +{{ m.points_awarded }} 积分
        </view>
        <!-- 待确认 → 操作按钮 -->
        <view v-if="m.status === 'pending' && m.receiver_pet_id === myPetId" class="meet-actions">
          <view class="act-btn ok" @tap="confirmMeet(m)">✓ 接受</view>
          <view class="act-btn no" @tap="cancelMeet(m)">✗ 拒绝</view>
        </view>
      </view>
    </view>

    <view v-else class="empty-state small">
      <view class="empty-text">还没有碰头记录</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { http } from '@/utils/request'

const nearby = ref<any[]>([])
const meets = ref<any[]>([])
const myPetId = ref(0)

const STATUS_LABEL: Record<string, string> = {
  pending: '待确认',
  confirmed: '已确认',
  success: '已完成',
  failed: '未达成',
  cancelled: '已取消',
}

function meetEmoji(status: string): string {
  return { success: '🎉', confirmed: '🤝', pending: '⏳', failed: '💤', cancelled: '🚫' }[status] || '🤝'
}

function meetStatusLabel(status: string): string {
  return STATUS_LABEL[status] || status
}

function meetTitle(m: any): string {
  return m.pet_name ? `${m.pet_name} 的碰头` : `碰头 #${m.id}`
}

function formatTime(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getMonth() + 1}月${d.getDate()}日 ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

/** 获取我的宠物（用于判断收到的邀请） */
async function loadMyPets() {
  try {
    const pets = await http.get<any[]>('/pets')
    if (pets && pets.length > 0) myPetId.value = pets[0].id
  } catch (e) {
    // 忽略
  }
}

/** 附近宠物 */
async function loadNearby() {
  try {
    const res = await new Promise<any>((resolve) => {
      uni.getLocation({
        type: 'gcj02',
        success: resolve,
        fail: () => resolve({ latitude: 34.7466, longitude: 113.6253 }),
      })
    })
    const lat = res.latitude
    const lng = res.longitude
    const data = await http.get<any[]>(`/social/nearby?lat=${lat}&lng=${lng}&radius=2000`)
    nearby.value = data || []
  } catch (e: any) {
    uni.showToast({ title: e.message || '加载附近宠物失败', icon: 'none' })
  }
}

/** 我的碰头记录 */
async function loadMeets() {
  try {
    const data = await http.get<any>(`/social/meets?page=1&size=20`)
    meets.value = data?.items || data || []
  } catch (e) {
    // 忽略
  }
}

/** 发起碰头 */
async function startMeet(p: any) {
  try {
    // 用我的第一只宠物发起
    const pets = await http.get<any[]>('/pets')
    if (!pets || pets.length === 0) {
      uni.showToast({ title: '请先添加宠物', icon: 'none' })
      return
    }
    const res = await new Promise<any>((resolve) => {
      uni.getLocation({
        type: 'gcj02',
        success: resolve,
        fail: () => resolve({ latitude: 34.7466, longitude: 113.6253 }),
      })
    })
    await http.post('/social/meets', {
      receiver_pet_id: p.pet_id || p.id,
      start_lat: res.latitude,
      start_lng: res.longitude,
    })
    uni.showToast({ title: '碰头邀请已发出！', icon: 'success' })
    loadMeets()
  } catch (e: any) {
    uni.showToast({ title: e.message || '发起失败', icon: 'none' })
  }
}

/** 确认碰头 */
async function confirmMeet(m: any) {
  try {
    const res = await new Promise<any>((resolve) => {
      uni.getLocation({
        type: 'gcj02',
        success: resolve,
        fail: () => resolve({ latitude: 34.7466, longitude: 113.6253 }),
      })
    })
    await http.put(`/social/meets/${m.id}/confirm`, {
      end_lat: res.latitude,
      end_lng: res.longitude,
    })
    uni.showToast({ title: '已确认碰头！', icon: 'success' })
    loadMeets()
  } catch (e: any) {
    uni.showToast({ title: e.message || '操作失败', icon: 'none' })
  }
}

/** 取消/拒绝碰头 */
async function cancelMeet(m: any) {
  try {
    await http.put(`/social/meets/${m.id}/cancel`)
    uni.showToast({ title: '已取消', icon: 'none' })
    loadMeets()
  } catch (e: any) {
    uni.showToast({ title: e.message || '操作失败', icon: 'none' })
  }
}

onShow(() => {
  loadMyPets()
  loadNearby()
  loadMeets()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f6f7fb;
  padding: 24rpx 0 60rpx;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 32rpx 8rpx;
  font-size: 30rpx;
  font-weight: 700;
}

.refresh {
  font-size: 24rpx;
  color: #3d6cf5;
  font-weight: 400;
}

/* 附近宠物 */
.nearby-card {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.pet-avatar {
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 44rpx;
}

.cat-bg {
  background: #fff7ed;
}

.dog-bg {
  background: #eff6ff;
}

.pet-info {
  flex: 1;
}

.pet-name {
  font-size: 30rpx;
  font-weight: 700;
}

.pet-detail {
  font-size: 24rpx;
  color: #9aa0a6;
  margin-top: 4rpx;
}

.meet-btn {
  padding: 14rpx 28rpx;
  border-radius: 999rpx;
  background: #3d6cf5;
  color: #fff;
  font-size: 26rpx;
  font-weight: 600;
}

/* 碰头记录 */
.meet-head {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.meet-emoji {
  font-size: 48rpx;
}

.meet-info {
  flex: 1;
}

.meet-title {
  font-size: 28rpx;
  font-weight: 600;
}

.meet-time {
  font-size: 22rpx;
  color: #9aa0a6;
  margin-top: 4rpx;
}

.meet-status {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 999rpx;
  background: #f3f4f6;
  color: #6b7280;
}

.meet-status.success {
  background: #f0fdf4;
  color: #22c55e;
}

.meet-status.pending {
  background: #fffbeb;
  color: #f59e0b;
}

.meet-points {
  margin-top: 16rpx;
  font-size: 24rpx;
  color: #3d6cf5;
  font-weight: 600;
}

.meet-actions {
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

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 0;
}

.empty-state.small {
  padding: 40rpx 0;
}

.empty-icon {
  font-size: 72rpx;
}

.empty-text {
  margin-top: 16rpx;
  color: #9aa0a6;
  font-size: 26rpx;
}
</style>
