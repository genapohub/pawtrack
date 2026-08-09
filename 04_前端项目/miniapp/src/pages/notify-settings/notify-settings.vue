<template>
  <view class="page">
    <view class="navbar-sm">
      <view class="back" @tap="goBack">‹</view>
      通知设置
      <view class="placeholder"></view>
    </view>

    <!-- 推送类型 -->
    <view class="card">
      <view class="card-title">推送类型</view>
      <view class="switch-row">
        <view class="switch-info">
          <view class="switch-title">系统消息</view>
          <view class="switch-sub">设备绑定、固件升级等</view>
        </view>
        <view class="switch" :class="{ on: settings.system }" @tap="settings.system = !settings.system"></view>
      </view>
      <view class="switch-row">
        <view class="switch-info">
          <view class="switch-title">社交互动</view>
          <view class="switch-sub">碰头邀请、好友动态</view>
        </view>
        <view class="switch" :class="{ on: settings.social }" @tap="settings.social = !settings.social"></view>
      </view>
      <view class="switch-row">
        <view class="switch-info">
          <view class="switch-title">营销活动</view>
          <view class="switch-sub">会员优惠、积分到期提醒</view>
        </view>
        <view class="switch" :class="{ on: settings.marketing }" @tap="settings.marketing = !settings.marketing"></view>
      </view>
      <view class="switch-row">
        <view class="switch-info">
          <view class="switch-title">微信订阅消息</view>
          <view class="switch-sub">通过微信服务通知接收报警</view>
        </view>
        <view class="switch" :class="{ on: settings.wechat_sub }" @tap="settings.wechat_sub = !settings.wechat_sub"></view>
      </view>
    </view>

    <!-- 免打扰 -->
    <view class="card">
      <view class="card-title">免打扰时段</view>
      <view class="switch-row">
        <view class="switch-info">
          <view class="switch-title">开启免打扰</view>
          <view class="switch-sub">该时段内仅保留紧急报警</view>
        </view>
        <view class="switch" :class="{ on: settings.quiet }" @tap="settings.quiet = !settings.quiet"></view>
      </view>
      <view v-if="settings.quiet" class="time-row">
        <picker mode="time" :value="settings.quiet_start" @change="settings.quiet_start = $event.detail.value">
          <view class="time-box">🕐 开始 {{ settings.quiet_start }}</view>
        </picker>
        <text class="time-arrow">→</text>
        <picker mode="time" :value="settings.quiet_end" @change="settings.quiet_end = $event.detail.value">
          <view class="time-box">🕐 结束 {{ settings.quiet_end }}</view>
        </picker>
      </view>
    </view>

    <view class="save-btn" :class="{ saving }" @tap="save">保存设置</view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { http } from '@/utils/request'

const settings = ref({
  system: true,
  social: true,
  marketing: false,
  wechat_sub: true,
  quiet: false,
  quiet_start: '22:00',
  quiet_end: '08:00',
})
const saving = ref(false)

async function save() {
  saving.value = true
  try {
    // 复用报警设置接口的 quiet_hours 字段，其余存本地
    await http.put('/alarms/settings', {
      quiet_hours_start: settings.value.quiet ? settings.value.quiet_start : undefined,
      quiet_hours_end: settings.value.quiet ? settings.value.quiet_end : undefined,
    }).catch(() => { /* 接口缺字段时静默 */ })
    uni.setStorageSync('pawtrack_notify_settings', settings.value)
    uni.showToast({ title: '保存成功！', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 800)
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  } finally {
    saving.value = false
  }
}

function goBack() { uni.navigateBack() }
</script>

<style scoped>
.page { min-height: 100vh; background: #f6f7fb; padding-bottom: 60rpx; }
.navbar-sm { display: flex; align-items: center; justify-content: space-between; padding: 20rpx 24rpx; font-size: 32rpx; font-weight: 700; }
.back { font-size: 44rpx; font-weight: 400; color: #333; }
.placeholder { width: 44rpx; }
.card { background: #fff; border-radius: 20rpx; padding: 16rpx 28rpx; margin: 0 24rpx 20rpx; box-shadow: 0 4rpx 16rpx rgba(0,0,0,.04); }
.card-title { font-size: 30rpx; font-weight: 700; padding: 12rpx 0 4rpx; }
.switch-row { display: flex; align-items: center; justify-content: space-between; padding: 24rpx 0; border-bottom: 1px solid #f3f4f6; }
.switch-row:last-child { border-bottom: none; }
.switch-info { flex: 1; }
.switch-title { font-size: 28rpx; font-weight: 600; }
.switch-sub { font-size: 22rpx; color: #9aa0a6; margin-top: 4rpx; }
.switch { width: 88rpx; height: 48rpx; border-radius: 999rpx; background: #d1d5db; position: relative; transition: .2s; }
.switch::after { content: ''; position: absolute; width: 40rpx; height: 40rpx; border-radius: 50%; background: #fff; top: 4rpx; left: 4rpx; transition: .2s; }
.switch.on { background: #3d6cf5; }
.switch.on::after { left: 44rpx; }
.time-row { display: flex; align-items: center; gap: 16rpx; padding: 20rpx 0; }
.time-box { background: #f6f7fb; border-radius: 12rpx; padding: 16rpx 24rpx; font-size: 26rpx; font-weight: 600; color: #3d6cf5; }
.time-arrow { color: #c0c4cc; font-size: 26rpx; }
.save-btn { margin: 30rpx 24rpx 0; text-align: center; background: linear-gradient(135deg, #5b8cff, #3d6cf5); color: #fff; border-radius: 999rpx; padding: 24rpx 0; font-size: 30rpx; font-weight: 600; }
.save-btn.saving { opacity: .6; }
</style>
