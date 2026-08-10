<template>
  <view class="page">
    <!-- 顶部状态 -->
    <view class="hero" :class="{ arrived: distance !== null && distance < 5 }">
      <view class="hero-emoji">{{ distance !== null && distance < 5 ? '🎉' : '🐾' }}</view>
      <view class="hero-title">
        {{ distance !== null && distance < 5 ? '对方就在眼前！' : '正在寻找碰头对象…' }}
      </view>
      <view class="hero-sub">
        {{ distance === null ? '等待对方设备上线…' : `当前距离 ${distance}m` }}
      </view>

      <!-- 距离环 -->
      <view class="distance-ring" :class="{ reached: distance !== null && distance < 5 }">
        <view class="ring-center">
          <view class="ring-num">{{ distance === null ? '--' : distance }}</view>
          <view class="ring-unit">米</view>
        </view>
      </view>

      <view class="hero-hint">
        {{ distance !== null && distance < 5 ? '双方距离小于 5m，点击确认完成碰头' : '向对方靠近，距离小于 5m 即可确认碰头' }}
      </view>
    </view>

    <!-- 倒计时 -->
    <view class="timer-bar">
      <view class="timer-label">⏱ 碰头时限（30 分钟）</view>
      <view class="timer-num">{{ formatTimeLeft }}</view>
    </view>

    <!-- 操作按钮 -->
    <view v-if="distance !== null && distance < 5" class="action-area">
      <view class="confirm-btn" @tap="confirmArrive">✓ 我已到达，确认碰头</view>
    </view>
    <view v-else class="action-area">
      <view class="hint-card">
        <view class="hint-row">📍 实时更新双方距离</view>
        <view class="hint-row">📡 设备每 5 秒上报一次位置</view>
        <view class="hint-row">🤝 距离 &lt; 5m 即可确认成功</view>
      </view>
    </view>

    <view class="cancel-link" @tap="cancelMeet">取消碰头</view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { http } from '@/utils/request'

const meetId = ref(0)
const distance = ref<number | null>(null)
const confirmedAt = ref<number>(Date.now())
const remaining = ref(30 * 60) // 30 分钟倒计时（秒）

let pollTimer: ReturnType<typeof setInterval> | null = null
let countdownTimer: ReturnType<typeof setInterval> | null = null

const formatTimeLeft = computed(() => {
  const s = Math.max(0, remaining.value)
  const m = Math.floor(s / 60)
  const sec = String(s % 60).padStart(2, '0')
  return `${m}:${sec}`
})

onLoad((options: any) => {
  meetId.value = Number(options.id || 0)
  if (!meetId.value) {
    uni.showToast({ title: '参数错误', icon: 'none' })
    return
  }
  startPolling()
  startCountdown()
})

/** 轮询双方实时距离 */
async function startPolling() {
  pollTimer = setInterval(async () => {
    try {
      const data = await http.get<any>(`/social/meets/${meetId.value}/distance`)
      if (data && data.distance !== null) {
        distance.value = data.distance
        if (data.elapsed_min) {
          remaining.value = Math.max(0, 30 * 60 - Math.round(data.elapsed_min * 60))
        }
      }
    } catch (e) {
      // 忽略轮询错误
    }
  }, 5000)
}

/** 30 分钟倒计时，超时自动取消 */
function startCountdown() {
  countdownTimer = setInterval(() => {
    remaining.value -= 1
    if (remaining.value <= 0) {
      clearAll()
      uni.showModal({
        title: '碰头超时',
        content: '30 分钟内未完成碰头，本次碰头已取消',
        showCancel: false,
        success: () => uni.navigateBack(),
      })
    }
  }, 1000)
}

/** 确认到达 → 完成碰头 */
async function confirmArrive() {
  try {
    await http.put(`/social/meets/${meetId.value}/complete`)
    clearAll()
    uni.redirectTo({ url: `/pages/meet-success/meet-success?id=${meetId.value}` })
  } catch (e: any) {
    uni.showToast({ title: e.message || '确认失败', icon: 'none' })
  }
}

/** 取消碰头 */
async function cancelMeet() {
  uni.showModal({
    title: '取消碰头',
    content: '确定取消本次碰头吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await http.put(`/social/meets/${meetId.value}/cancel`)
          clearAll()
          uni.navigateBack()
        } catch (e: any) {
          uni.showToast({ title: e.message || '取消失败', icon: 'none' })
        }
      }
    },
  })
}

function clearAll() {
  if (pollTimer) clearInterval(pollTimer)
  if (countdownTimer) clearInterval(countdownTimer)
  pollTimer = null
  countdownTimer = null
}

onUnmounted(clearAll)
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f6f7fb;
  padding-bottom: 60rpx;
}

.hero {
  background: #3d6cf5;
  color: #fff;
  padding: 60rpx 40rpx 80rpx;
  border-radius: 0 0 40rpx 40rpx;
  text-align: center;
}

.hero.arrived {
  background: #22c55e;
}

.hero-emoji {
  font-size: 80rpx;
}

.hero-title {
  font-size: 36rpx;
  font-weight: 700;
  margin-top: 12rpx;
}

.hero-sub {
  font-size: 26rpx;
  opacity: 0.85;
  margin-top: 8rpx;
}

.distance-ring {
  width: 260rpx;
  height: 260rpx;
  border-radius: 50%;
  border: 12rpx solid rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 48rpx auto 32rpx;
}

.distance-ring.reached {
  border-color: rgba(255, 255, 255, 0.9);
}

.ring-center {
  text-align: center;
}

.ring-num {
  font-size: 72rpx;
  font-weight: 800;
  line-height: 1;
}

.ring-unit {
  font-size: 26rpx;
  opacity: 0.85;
  margin-top: 8rpx;
}

.hero-hint {
  font-size: 24rpx;
  opacity: 0.9;
}

.timer-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  margin: 24rpx 32rpx;
  padding: 24rpx 32rpx;
  border-radius: 16rpx;
}

.timer-label {
  font-size: 26rpx;
  color: #6b7280;
}

.timer-num {
  font-size: 30rpx;
  font-weight: 700;
  color: #f59e0b;
  font-variant-numeric: tabular-nums;
}

.action-area {
  margin: 24rpx 32rpx;
}

.confirm-btn {
  background: #22c55e;
  color: #fff;
  text-align: center;
  padding: 28rpx 0;
  border-radius: 16rpx;
  font-size: 30rpx;
  font-weight: 700;
}

.hint-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 28rpx 32rpx;
}

.hint-row {
  font-size: 26rpx;
  color: #6b7280;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #f3f4f6;
}

.hint-row:last-child {
  border-bottom: none;
}

.cancel-link {
  text-align: center;
  color: #ef4444;
  font-size: 26rpx;
  margin-top: 48rpx;
}
</style>
