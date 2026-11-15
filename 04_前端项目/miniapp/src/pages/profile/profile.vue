<template>
  <view class="page">

    <view v-if="loadError" class="pt-card">
      <view class="err-box">资料加载失败，请稍后重试。</view>
      <view class="btn-primary" @tap="reload">重新加载</view>
    </view>

    <template v-else>
      <view class="pt-card user-card">
        <view class="avatar-mark avatar-cat">{{ nameMark }}</view>
        <view class="user-meta">
          <view class="user-name">{{ displayName }}</view>
          <view class="user-sub">{{ maskedPhone }} · {{ memberLabel }}</view>
        </view>
      </view>

      <view class="pt-card menu">
        <view class="menu-item" @tap="goDevices">
          <text class="mi-name">设备管理</text>
          <text class="mi-note">主路径</text>
        </view>
        <view class="menu-item" @tap="goMember">
          <text class="mi-name">会员</text>
          <text class="mi-note">会员与积分</text>
        </view>
        <view class="menu-item" @tap="goPoints">
          <text class="mi-name">积分</text>
          <text class="mi-note">会员与积分</text>
        </view>
        <view class="menu-item" @tap="goInvite">
          <text class="mi-name">邀请</text>
          <text class="mi-note"></text>
        </view>
        <view class="menu-item" @tap="goNotify">
          <text class="mi-name">通知</text>
          <text class="mi-note">与报警设置分离</text>
        </view>
        <view class="menu-item last" @tap="goSettings">
          <text class="mi-name">设置</text>
          <text class="mi-note">隐私与退出</text>
        </view>
      </view>

      <view class="foot-note">管理账号、通知与设备相关设置。</view>
    </template>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { http } from '@/utils/request'
import { getUser } from '@/utils/auth'

const user = ref<any>(getUser() || {})
const loadError = ref(false)

const displayName = computed(() => user.value?.nickname || '林晓荷')
const nameMark = computed(() => displayName.value.slice(0, 1))
const maskedPhone = computed(() => {
  const p = String(user.value?.phone || '13800000000')
  if (p.length >= 7) return p.slice(0, 3) + '****' + p.slice(-4)
  return p || '未绑定手机号'
})
const memberLabel = computed(() => {
  const lv = user.value?.member_level
  if (lv === 'pro') return 'Pro 版'
  if (lv === 'basic') return '基础版'
  return '免费版'
})

async function loadUser() {
  loadError.value = false
  try {
    const me = await http.get<any>('/users/me')
    if (me) user.value = me
  } catch (e) {
    if (!user.value?.phone) loadError.value = true
  }
}

function reload() { loadUser() }
function goMember() { uni.navigateTo({ url: '/pages/member/member' }) }
function goPoints() { uni.navigateTo({ url: '/pages/points/points' }) }
function goInvite() { uni.navigateTo({ url: '/pages/invite/invite' }) }
function goDevices() { uni.navigateTo({ url: '/pages/device-manage/device-manage' }) }
function goNotify() { uni.navigateTo({ url: '/pages/notify-settings/notify-settings' }) }
function goSettings() { uni.navigateTo({ url: '/pages/settings/settings' }) }

onShow(() => { loadUser() })
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--pt-bg);
  padding-bottom: 80rpx;
}

.user-card {
  margin-top: 24rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.user-meta { flex: 1; }

.user-name {
  font-size: 32rpx;
  font-weight: 500;
  color: var(--pt-fg);
}

.user-sub {
  margin-top: 6rpx;
  font-size: 24rpx;
  font-weight: 400;
  color: var(--pt-fg-2);
}

.menu {
  padding: 8rpx 32rpx;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  padding: 28rpx 0;
  border-bottom: 1rpx solid var(--pt-border);
}

.menu-item.last { border-bottom: none; }

.mi-name {
  font-size: 30rpx;
  font-weight: 400;
  color: var(--pt-fg);
}

.mi-note {
  font-size: 22rpx;
  font-weight: 400;
  color: var(--pt-fg-3);
  text-align: right;
}

.foot-note {
  margin: 8rpx 40rpx 0;
  font-size: 22rpx;
  font-weight: 400;
  color: var(--pt-fg-3);
  line-height: 1.5;
}
</style>
