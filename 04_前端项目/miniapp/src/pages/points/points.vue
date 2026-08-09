<template>
  <view class="page">
    <!-- 积分余额 Hero -->
    <view class="points-hero">
      <view class="hero-label">我的积分</view>
      <view class="hero-balance">{{ balance }}</view>
      <view class="sign-btn" :class="{ signed: signedToday }" @tap="signin">
        {{ signing ? '签到中...' : signedToday ? '今日已签到 ✓' : '📅 每日签到' }}
      </view>
    </view>

    <!-- 积分明细 -->
    <view class="card">
      <view class="card-title">积分明细</view>
      <view v-if="logs.length > 0" class="log-list">
        <view v-for="log in logs" :key="log.id" class="log-row">
          <view class="log-icon">{{ logIcon(log.type) }}</view>
          <view class="log-info">
            <view class="log-name">{{ logName(log.type) }}</view>
            <view class="log-time">{{ formatTime(log.created_at) }}</view>
          </view>
          <view class="log-change" :class="log.change > 0 ? 'plus' : 'minus'">
            {{ log.change > 0 ? '+' : '' }}{{ log.change }}
          </view>
        </view>
      </view>
      <view v-else class="empty-tip">暂无积分记录</view>
    </view>

    <!-- 积分商城 -->
    <view class="card">
      <view class="card-title">积分商城</view>
      <view v-if="shop.length > 0" class="shop-grid">
        <view v-for="item in shop" :key="item.id" class="shop-item" @tap="exchange(item)">
          <view class="shop-image">{{ item.image || '🎁' }}</view>
          <view class="shop-name">{{ item.name }}</view>
          <view class="shop-points">🪙 {{ item.points }} 积分</view>
        </view>
      </view>
      <view v-else class="empty-tip">商城筹备中，敬请期待</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { http } from '@/utils/request'

const balance = ref(0)
const logs = ref<any[]>([])
const shop = ref<any[]>([])
const signing = ref(false)
const signedToday = ref(false)

const LOG_META: Record<string, { label: string; icon: string }> = {
  meet: { label: '碰头奖励', icon: '🤝' },
  invite: { label: '邀请奖励', icon: '🎁' },
  signin: { label: '每日签到', icon: '📅' },
  purchase: { label: '兑换消费', icon: '🛒' },
  expire: { label: '积分过期', icon: '⏰' },
  admin: { label: '后台调整', icon: '⚙️' },
}

function logName(type: string): string {
  return LOG_META[type]?.label || type
}

function logIcon(type: string): string {
  return LOG_META[type]?.icon || '🪙'
}

function formatTime(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getMonth() + 1}月${d.getDate()}日 ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function loadAll() {
  try {
    const [balData, logsData, shopData] = await Promise.all([
      http.get<any>('/points/balance'),
      http.get<any>('/points/logs?page=1&size=30'),
      http.get<any>('/points/shop'),
    ])
    balance.value = balData?.balance || 0
    logs.value = logsData?.items || logsData || []
    shop.value = shopData || []

    // 判断今日是否已签到
    const today = new Date().toDateString()
    signedToday.value = logs.value.some(
      (l) => l.type === 'signin' && new Date(l.created_at).toDateString() === today
    )
  } catch (e: any) {
    uni.showToast({ title: e.message || '加载失败', icon: 'none' })
  }
}

async function signin() {
  if (signedToday.value || signing.value) return
  signing.value = true
  try {
    const data = await http.post<any>('/points/signin')
    uni.showToast({ title: `签到成功 +${data?.awarded || 5} 积分 🎉`, icon: 'success' })
    loadAll()
  } catch (e: any) {
    uni.showToast({ title: e.message || '签到失败', icon: 'none' })
  } finally {
    signing.value = false
  }
}

function exchange(item: any) {
  if (balance.value < item.points) {
    uni.showToast({ title: '积分不足，继续努力～', icon: 'none' })
    return
  }
  uni.showModal({
    title: '确认兑换',
    content: `用 ${item.points} 积分兑换「${item.name}」？`,
    success: (res) => {
      if (res.confirm) {
        uni.showToast({ title: '兑换功能开发中，敬请期待～', icon: 'none' })
      }
    },
  })
}

onShow(loadAll)
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f6f7fb;
  padding: 24rpx 0 60rpx;
}

/* Hero */
.points-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0 24rpx 20rpx;
  border-radius: 24rpx;
  padding: 48rpx 0;
  background: linear-gradient(135deg, #3d6cf5, #5b8cff);
  color: #fff;
}

.hero-label {
  font-size: 26rpx;
  opacity: 0.9;
}

.hero-balance {
  font-size: 96rpx;
  font-weight: 800;
  margin: 8rpx 0;
  font-family: 'DIN Alternate', sans-serif;
}

.sign-btn {
  margin-top: 16rpx;
  padding: 14rpx 48rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.22);
  font-size: 28rpx;
  font-weight: 600;
}

.sign-btn.signed {
  background: rgba(255, 255, 255, 0.12);
  opacity: 0.8;
}

/* 卡片 */
.card-title {
  font-size: 30rpx;
  font-weight: 700;
  margin-bottom: 20rpx;
}

/* 积分明细 */
.log-row {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 18rpx 0;
  border-bottom: 2rpx solid #f3f4f6;
}

.log-row:last-child {
  border-bottom: none;
}

.log-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
}

.log-info {
  flex: 1;
}

.log-name {
  font-size: 28rpx;
  font-weight: 600;
}

.log-time {
  font-size: 22rpx;
  color: #9aa0a6;
  margin-top: 4rpx;
}

.log-change {
  font-size: 30rpx;
  font-weight: 700;
}

.log-change.plus {
  color: #3d6cf5;
}

.log-change.minus {
  color: #6b7280;
}

/* 商城 */
.shop-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20rpx;
}

.shop-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24rpx 12rpx;
  border-radius: 16rpx;
  background: #f6f7fb;
}

.shop-image {
  font-size: 64rpx;
}

.shop-name {
  font-size: 24rpx;
  font-weight: 600;
  margin-top: 12rpx;
  text-align: center;
}

.shop-points {
  font-size: 22rpx;
  color: #f59e0b;
  margin-top: 8rpx;
}

.empty-tip {
  text-align: center;
  color: #9aa0a6;
  padding: 40rpx 0;
  font-size: 26rpx;
}
</style>
