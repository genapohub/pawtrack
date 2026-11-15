<template>
  <view class="page">

    <view v-if="loadError" class="pt-card">
      <view class="err-box">设备列表加载失败，请稍后重试。</view>
      <view class="btn-primary" @tap="loadDevices">重新加载</view>
    </view>

    <view v-else-if="!devices.length" class="pt-card">
      <view class="empty-title">还没有定位器</view>
      <view class="empty-desc">添加后可绑定定位器，查看位置与围栏。</view>
      <view class="btn-primary" @tap="goBind">绑定定位器</view>
    </view>

    <view v-else class="list">
      <view v-for="d in devices" :key="d.id" class="pt-card device-card">
        <view class="dev-row">
          <view class="dev-meta">
            <view class="sn">{{ d.sn }}</view>
            <view class="sub">绑定宠物：{{ bindDetail(d) }}</view>
            <view class="sub">{{ deviceStateText(d) }}</view>
            <view class="sub firmware" @tap="onFirmware">固件已是最新，暂无可升级版本。</view>
          </view>
          <text class="tag" :class="statusClass(d)">{{ statusLabel(d) }}</text>
        </view>
      </view>

      <view v-if="unbindError" class="err-box unbind-err">{{ unbindError }}</view>
      <view
        v-if="devices.length"
        class="btn-danger unbind-btn"
        @tap="unbind(devices[0])"
      >{{ unbindError ? '再次尝试解绑' : '解绑设备' }}</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { http } from '@/utils/request'
import { PT } from '@/styles/tokens'

const devices = ref<any[]>([])
const loadError = ref(false)
const unbindError = ref('')

onShow(loadDevices)

async function loadDevices() {
  loadError.value = false
  try {
    devices.value = (await http.get<any[]>('/devices')) || []
  } catch (e) {
    loadError.value = true
  }
}

function petLabel(d: any) {
  if (d.pet_name) {
    const kind = d.hardware_type === 'cat' || d.pet_type === 'cat' ? '猫' : (d.hardware_type === 'dog' || d.pet_type === 'dog' ? '狗' : '')
    return kind ? `${d.pet_name}（${kind}）` : d.pet_name
  }
  if (!d.pet_id) return '未绑定'
  return d.hardware_type === 'cat' ? '已绑定（猫）' : d.hardware_type === 'dog' ? '已绑定（狗）' : '已绑定'
}

function statusLabel(d: any) {
  if (d.status === 'online') return '已绑定 · 在线'
  if (d.status === 'low_battery') return '已绑定 · 低电'
  if (!d.pet_id) return '未绑定 · 离线'
  return '离线'
}

function statusClass(d: any) {
  if (d.status === 'online') return 'tag-success'
  if (d.status === 'low_battery') return 'tag-warning'
  return 'tag-muted'
}


function bindDetail(d: any) {
  if (!d.pet_id && !d.pet_name) return '未绑定'
  const kind = d.hardware_type === 'cat' || d.pet_type === 'cat' ? '猫' : (d.hardware_type === 'dog' || d.pet_type === 'dog' ? '狗' : '')
  const name = d.pet_name || '已绑定'
  const parts = [kind ? `${name}（${kind}）` : name]
  if (d.battery != null) parts.push(`电量 ${d.battery}%`)
  if (d.pet_id || d.pet_name) {
    const src = d.source === 'gps' || d.source === 'GPS' ? 'GPS' : 'Wi-Fi'
    parts.push(`来源 ${src}`)
  }
  return parts.join(' · ')
}

function deviceStateText(d: any) {
  if (!d.pet_id && !d.pet_name) return '设备状态：未绑定。绑定后即可查看位置与围栏告警。'
  return '设备状态：已绑定。可查看电量、位置来源或解绑。'
}

function onFirmware() {
  uni.showToast({ title: '固件已是最新，暂无可升级版本', icon: 'none' })
}

function unbind(d: any) {
  uni.showModal({
    title: '解绑确认',
    content: `解绑后，${d.pet_name || '该宠物'}将不再收到位置与围栏告警。`,
    confirmColor: PT.danger,
    success: async (res) => {
      if (!res.confirm) return
      const snapshot = devices.value.slice()
      try {
        await http.post('/devices/unbind', { sn: d.sn })
        unbindError.value = ''
        uni.showToast({ title: '已解绑', icon: 'none' })
        loadDevices()
      } catch (e: any) {
        devices.value = snapshot
        unbindError.value = '解绑未完成，设备仍留在列表中。请稍后重试。'
      }
    },
  })
}

function goBind() { uni.navigateTo({ url: '/pages/device-bind/device-bind' }) }
</script>

<style scoped>
.page { min-height: 100vh; background: var(--pt-bg); padding-bottom: 80rpx; }
.list { padding-top: 24rpx; }
.dev-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 16rpx; }
.sn { font-size: 30rpx; font-weight: 500; color: var(--pt-fg); }
.sub { margin-top: 8rpx; font-size: 24rpx; color: var(--pt-fg-2); font-weight: 400; }
.unbind-err { margin: 0 32rpx 16rpx; }
.unbind-btn { margin: 0 32rpx; }
.empty-title { font-size: 30rpx; font-weight: 500; margin-bottom: 8rpx; }
.empty-desc { font-size: 24rpx; color: var(--pt-fg-2); margin-bottom: 24rpx; line-height: 1.5; }
</style>
