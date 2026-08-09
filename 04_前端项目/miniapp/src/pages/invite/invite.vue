<template>
  <view class="page">
    <view class="navbar-sm">
      <view class="back" @tap="goBack">‹</view>
      邀请好友
      <view class="placeholder"></view>
    </view>

    <!-- 邀请主卡 -->
    <view class="card center" style="padding: 36rpx 28rpx">
      <view class="big-avatar">🎁</view>
      <view class="invite-title">邀请好友，各得 50 积分</view>
      <view class="invite-sub">好友注册并绑定宠物后积分自动到账</view>
      <view class="invite-code-box">
        <view class="invite-code">{{ inviteCode || 'PAWTRACK-0000' }}</view>
        <view class="copy-btn" @tap="copyCode">复制</view>
      </view>
      <button class="primary-btn" @tap="shareInvite">📤 分享给好友</button>
    </view>

    <!-- 积分说明 -->
    <view class="card">
      <view class="card-title">奖励规则</view>
      <view class="rule-row">
        <view class="rule-icon">👤</view>
        <view class="rule-info">
          <view class="rule-title">好友成功注册</view>
          <view class="rule-sub">+50 积分（你）</view>
        </view>
        <view class="rule-status">✅</view>
      </view>
      <view class="rule-row">
        <view class="rule-icon">🐾</view>
        <view class="rule-info">
          <view class="rule-title">好友绑定宠物</view>
          <view class="rule-sub">+50 积分（好友）</view>
        </view>
        <view class="rule-status">✅</view>
      </view>
    </view>

    <!-- 邀请记录 -->
    <view class="card">
      <view class="card-title">邀请记录</view>
      <view v-if="records.length > 0" class="record-list">
        <view v-for="r in records" :key="r.id" class="record-row">
          <view class="record-avatar">{{ r.nickname ? r.nickname[0] : '宠' }}</view>
          <view class="record-info">
            <view class="record-name">{{ r.nickname || '新用户' }}</view>
            <view class="record-sub">{{ r.created_at }}</view>
          </view>
          <view class="record-points">+{{ r.points_awarded || 50 }}</view>
        </view>
      </view>
      <view v-else class="empty-tip">还没有邀请记录，快去分享吧～</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { http } from '@/utils/request'

const inviteCode = ref('')
const records = ref<any[]>([])

onLoad(async () => {
  await loadInvite()
})

async function loadInvite() {
  try {
    const data = await http.get<any>('/users/me')
    if (data) {
      inviteCode.value = `PAWTRACK-${String(data.user_id || 0).padStart(4, '0')}`
    }
  } catch (e) { /* 静默 */ }
  try {
    const data = await http.get<any>('/invites')
    records.value = data?.items || data || []
  } catch (e) { /* 静默 */ }
}

function copyCode() {
  uni.setClipboardData({
    data: inviteCode.value,
    success: () => uni.showToast({ title: '邀请码已复制', icon: 'success' }),
  })
}

function shareInvite() {
  uni.showModal({
    title: '分享邀请',
    content: `我的宠迹邀请码：${inviteCode.value}。注册即各得 50 积分！`,
    showCancel: false,
    confirmText: '知道了',
  })
}

function goBack() { uni.navigateBack() }
</script>

<style scoped>
.page { min-height: 100vh; background: #f6f7fb; padding-bottom: 60rpx; }
.navbar-sm { display: flex; align-items: center; justify-content: space-between; padding: 20rpx 24rpx; font-size: 32rpx; font-weight: 700; }
.back { font-size: 44rpx; font-weight: 400; color: #333; }
.placeholder { width: 44rpx; }
.card { background: #fff; border-radius: 20rpx; padding: 28rpx; margin: 0 24rpx 20rpx; box-shadow: 0 4rpx 16rpx rgba(0,0,0,.04); }
.card.center { text-align: center; }
.card-title { font-size: 30rpx; font-weight: 700; margin-bottom: 12rpx; }
.big-avatar { font-size: 72rpx; }
.invite-title { font-size: 32rpx; font-weight: 700; margin-top: 12rpx; }
.invite-sub { font-size: 24rpx; color: #9aa0a6; margin-top: 6rpx; }
.invite-code-box { display: flex; align-items: center; justify-content: center; gap: 16rpx; margin: 24rpx 0; }
.invite-code { background: #f6f7fb; border: 2rpx dashed #3d6cf5; border-radius: 12rpx; padding: 16rpx 28rpx; font-size: 30rpx; letter-spacing: 4rpx; color: #3d6cf5; font-weight: 700; }
.copy-btn { background: #eef2ff; color: #3d6cf5; border-radius: 999rpx; padding: 12rpx 24rpx; font-size: 24rpx; font-weight: 600; }
.primary-btn { width: 100%; background: linear-gradient(135deg, #5b8cff, #3d6cf5); color: #fff; border: none; border-radius: 999rpx; padding: 22rpx 0; font-size: 30rpx; font-weight: 600; }
.rule-row { display: flex; align-items: center; gap: 16rpx; padding: 18rpx 0; border-bottom: 1px solid #f3f4f6; }
.rule-row:last-child { border-bottom: none; }
.rule-icon { font-size: 36rpx; }
.rule-info { flex: 1; }
.rule-title { font-size: 28rpx; font-weight: 600; }
.rule-sub { font-size: 22rpx; color: #9aa0a6; margin-top: 2rpx; }
.rule-status { font-size: 28rpx; }
.record-row { display: flex; align-items: center; gap: 16rpx; padding: 16rpx 0; border-bottom: 1px solid #f3f4f6; }
.record-row:last-child { border-bottom: none; }
.record-avatar { width: 64rpx; height: 64rpx; border-radius: 50%; background: #eef2ff; display: flex; align-items: center; justify-content: center; font-size: 28rpx; font-weight: 700; color: #3d6cf5; }
.record-info { flex: 1; }
.record-name { font-size: 28rpx; font-weight: 600; }
.record-sub { font-size: 22rpx; color: #9aa0a6; margin-top: 2rpx; }
.record-points { font-size: 28rpx; font-weight: 700; color: #3d6cf5; }
.empty-tip { text-align: center; color: #9aa0a6; padding: 40rpx 0; font-size: 26rpx; }
</style>
