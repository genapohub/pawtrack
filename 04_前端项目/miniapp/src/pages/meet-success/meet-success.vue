<template>
  <view class="page">
    <!-- 成功动画区 -->
    <view class="success-hero">
      <view class="badge">🎉</view>
      <view class="title">碰头成功！</view>
      <view class="sub">双方确认到场，友谊 +1</view>
    </view>

    <!-- 积分奖励卡 -->
    <view class="points-card">
      <view class="points-head">
        <view class="points-label">碰头奖励</view>
        <view class="points-value">+{{ points }} 积分</view>
      </view>
      <view class="points-row">
        <text>🥇 完成碰头</text>
        <text>+{{ points }}</text>
      </view>
      <view class="points-row">
        <text>💰 当前余额</text>
        <text>{{ balance }} 分</text>
      </view>
      <view class="points-note">积分可在积分商城兑换宠物用品（12 个月内有效）</view>
    </view>

    <!-- 碰头记录卡 -->
    <view class="record-card" v-if="meet">
      <view class="record-title">📅 碰头记录</view>
      <view class="record-row">
        <text>碰头对象</text>
        <text>{{ meet.pet_name || '未知宠物' }}</text>
      </view>
      <view class="record-row">
        <text>完成时间</text>
        <text>{{ formatTime(meet.completed_at) }}</text>
      </view>
    </view>

    <!-- 操作 -->
    <view class="actions">
      <view class="btn-primary" @tap="goShop">去积分商城逛逛</view>
      <view class="btn-outline" @tap="backToSocial">返回社交首页</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { http } from '@/utils/request'

const meetId = ref(0)
const points = ref(100)
const balance = ref(0)
const meet = ref<any>(null)

onLoad(async (options: any) => {
  meetId.value = Number(options.id || 0)
  try {
    // 查询碰头详情
    const data = await http.get<any>(`/social/meets?page=1&size=20`)
    const items = data?.items || data || []
    meet.value = items.find((m: any) => m.id === meetId.value) || null
    if (meet.value?.points_awarded) points.value = meet.value.points_awarded
    // 查询积分余额
    const bal = await http.get<any>('/points/balance')
    balance.value = bal?.balance || 0
  } catch (e) {
    // 忽略
  }
})

function formatTime(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getMonth() + 1}月${d.getDate()}日 ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function goShop() {
  uni.switchTab({ url: '/pages/points/points' })
}

function backToSocial() {
  uni.switchTab({ url: '/pages/social/social' })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f6f7fb;
  padding: 60rpx 32rpx;
}

.success-hero {
  text-align: center;
  padding: 60rpx 0 40rpx;
}

.badge {
  font-size: 120rpx;
}

.title {
  font-size: 44rpx;
  font-weight: 800;
  margin-top: 16rpx;
  background: linear-gradient(90deg, #3d6cf5, #22c55e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.sub {
  font-size: 26rpx;
  color: #9aa0a6;
  margin-top: 12rpx;
}

.points-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 32rpx;
  margin-top: 32rpx;
}

.points-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid #f3f4f6;
}

.points-label {
  font-size: 28rpx;
  font-weight: 600;
}

.points-value {
  font-size: 36rpx;
  font-weight: 800;
  color: #3d6cf5;
}

.points-row {
  display: flex;
  justify-content: space-between;
  padding: 20rpx 0;
  font-size: 26rpx;
  color: #4b5563;
}

.points-note {
  font-size: 22rpx;
  color: #9aa0a6;
  padding-top: 12rpx;
  border-top: 1rpx solid #f3f4f6;
}

.record-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 32rpx;
  margin-top: 24rpx;
}

.record-title {
  font-size: 28rpx;
  font-weight: 600;
  margin-bottom: 12rpx;
}

.record-row {
  display: flex;
  justify-content: space-between;
  padding: 12rpx 0;
  font-size: 26rpx;
  color: #6b7280;
}

.actions {
  margin-top: 48rpx;
}

.btn-primary {
  background: #3d6cf5;
  color: #fff;
  text-align: center;
  padding: 28rpx 0;
  border-radius: 16rpx;
  font-size: 30rpx;
  font-weight: 700;
}

.btn-outline {
  border: 2rpx solid #3d6cf5;
  color: #3d6cf5;
  text-align: center;
  padding: 26rpx 0;
  border-radius: 16rpx;
  font-size: 28rpx;
  font-weight: 600;
  margin-top: 24rpx;
}
</style>
