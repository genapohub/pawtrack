<template>
  <view class="page">

    <view v-if="noDevice" class="pt-card">
      <view class="empty-title">请先绑定定位器再设置围栏</view>
      <view class="empty-desc">请先绑定定位器再设置围栏。</view>
      <view class="btn-primary" @tap="goBind">去绑定定位器</view>
    </view>

    <template v-else>
      <view v-if="intro" class="intro">{{ intro }}</view>

      <view class="pt-card switch-card">
        <view>
          <view class="row-title">离家报警</view>
          <view class="row-sub">{{ isCat ? '锁定开启' : (settings.fence_enabled ? '已开启' : '已关闭') }}</view>
        </view>
        <switch
          :checked="settings.fence_enabled"
          :disabled="saving"
          :color="PT.accent"
          @change="onToggle"
        />
      </view>

      <view v-if="lockNote" class="warn-box lock-note">{{ lockNote }}</view>
      <view class="hint">离开围栏时记录一条告警。半径不能小于 20 米。可在地图上点选围栏圆心。</view>

      <view class="pt-card radius-card">
        <view class="radius-row">
          <text class="row-title">围栏半径</text>
          <text class="radius-val">{{ settings.fence_radius }} 米</text>
        </view>
        <slider
          :value="settings.fence_radius"
          min="1"
          max="1000"
          step="1"
          :activeColor="PT.accent"
          :backgroundColor="PT.bgMuted"
          :block-size="20"
          :block-color="PT.accent"
          @changing="onRadiusChanging"
          @change="onRadiusChange"
        />
      </view>

      <view v-if="radiusError" class="err-box radius-err">{{ radiusError }}</view>

      <view
        class="btn-primary save-btn"
        :class="{ disabled: saving || !!radiusError }"
        @tap="save"
      >
        {{ saving ? '保存中...' : (isCat ? '保存半径与圆心' : '保存设置') }}
      </view>
    </template>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { http } from '@/utils/request'
import { PT } from '@/styles/tokens'

const petId = ref(0)
const pet = ref<any>(null)
const settings = ref({ fence_enabled: true, fence_radius: 100 })
const savedRadius = ref(100)
const saving = ref(false)
const lockNote = ref('')
const radiusError = ref('')
const noDevice = ref(false)
const intro = ref('')
const isCat = ref(false)

onLoad(async (options: any) => {
  petId.value = Number(options.id || options.petId || 0)
  await load()
})

async function load() {
  try {
    let current = petId.value
    if (!current) {
      const list = await http.get<any[]>('/pets')
      current = list?.[0]?.id || 0
      petId.value = current
    }
    if (!current) {
      noDevice.value = true
      return
    }
    const p = await http.get<any>(`/pets/${current}`)
    pet.value = p
    isCat.value = p?.type === 'cat'
    const radius = p?.fence_radius || (isCat.value ? 100 : 300)
    settings.value = {
      fence_enabled: isCat.value ? true : !!p?.fence_enabled,
      fence_radius: radius,
    }
    savedRadius.value = radius
    const devices = await http.get<any[]>('/devices').catch(() => [])
    noDevice.value = !devices?.some((d: any) => d.pet_id === current)
    if (isCat.value) {
      intro.value = `报警设置绑定${p?.name || '宠物'}（猫）。`
      lockNote.value = '开启且不可关闭（猫规则）。'
    } else {
      intro.value = `报警设置绑定${p?.name || '宠物'}（狗）。狗可关闭离家报警，默认半径 300 米。`
    }
  } catch (e) {
    noDevice.value = true
  }
}

function onToggle(e: any) {
  const next = !!e.detail.value
  if (isCat.value) {
    settings.value.fence_enabled = true
    lockNote.value = '开启且不可关闭（猫规则）。'
    return
  }
  settings.value.fence_enabled = next
}

function onRadiusChanging(e: any) {
  settings.value.fence_radius = Number(e.detail.value)
}

function onRadiusChange(e: any) {
  const v = Number(e.detail.value)
  settings.value.fence_radius = v
  if (v < 20) {
    radiusError.value = '半径不能小于 20 米。'
  } else {
    radiusError.value = ''
  }
}

function goBind() { uni.navigateTo({ url: '/pages/device-bind/device-bind' }) }

async function save() {
  if (saving.value) return
  if (settings.value.fence_radius < 20) {
    radiusError.value = '半径不能小于 20 米。'
    return
  }
  if (isCat.value) settings.value.fence_enabled = true
  saving.value = true
  try {
    await http.put(`/pets/${petId.value}/fence`, {
      fence_enabled: settings.value.fence_enabled,
      fence_radius: settings.value.fence_radius,
      fence_center_lat: 31.23,
      fence_center_lng: 121.473,
    })
    savedRadius.value = settings.value.fence_radius
    uni.showToast({ title: '已保存', icon: 'none' })
  } catch (e: any) {
    uni.showToast({ title: e.message || '保存失败', icon: 'none' })
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--pt-bg); padding-bottom: 80rpx; }
.intro {
  margin: 24rpx 40rpx 8rpx;
  font-size: 24rpx;
  color: var(--pt-fg-2);
  line-height: 1.5;
  font-weight: 400;
}
.switch-card, .radius-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  margin-top: 16rpx;
}
.radius-card { flex-direction: column; align-items: stretch; }
.row-title { font-size: 30rpx; font-weight: 500; color: var(--pt-fg); }
.row-sub { margin-top: 6rpx; font-size: 22rpx; color: var(--pt-fg-3); }
.radius-row { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8rpx; }
.radius-val { font-size: 30rpx; font-weight: 500; color: var(--pt-fg); }
.lock-note, .radius-err { margin: 0 32rpx; }
.save-btn { margin: 24rpx 32rpx 0; }
.empty-title { font-size: 30rpx; font-weight: 500; margin-bottom: 8rpx; }
.empty-desc { font-size: 24rpx; color: var(--pt-fg-2); margin-bottom: 24rpx; line-height: 1.5; }
.hint { margin: 8rpx 40rpx 0; font-size: 22rpx; color: var(--pt-fg-2); line-height: 1.55; font-weight: 400; }
</style>
