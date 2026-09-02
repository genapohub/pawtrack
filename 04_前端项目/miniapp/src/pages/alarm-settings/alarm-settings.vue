<template>
  <view class="page">
    <view class="navbar-sm">
      <view class="back" @tap="goBack">‹</view>
      报警设置
      <view class="placeholder"></view>
    </view>

    <!-- 围栏主开关 -->
    <view class="card">
      <view class="switch-row">
        <view class="switch-info">
          <view class="switch-title">电子围栏报警</view>
          <view class="switch-sub">宠物离开设定范围时提醒</view>
        </view>
        <view class="switch" :class="{ on: settings.fence_enabled }" @tap="settings.fence_enabled = !settings.fence_enabled"></view>
      </view>

      <view v-if="settings.fence_enabled" class="field">
        <!-- 地图拖拽圆心 -->
        <view class="label">围栏圆心（拖拽地图调整）</view>
        <map
          style="width:100%;height:400rpx;border-radius:16rpx;margin-bottom:24rpx"
          :latitude="fenceCenter.lat"
          :longitude="fenceCenter.lng"
          :markers="[fenceMarker]"
          scale="16"
          @tap="onMapTap"
        />
        <view class="range-value">圆心：{{ fenceCenter.lat.toFixed(6) }}, {{ fenceCenter.lng.toFixed(6) }}</view>

        <view class="label">围栏半径</view>
        <view class="slider-row">
          <text>50m</text>
          <view class="slider">
            <view class="slider-fill" :style="{ width: radiusPct + '%' }"></view>
            <view class="knob" :style="{ left: radiusPct + '%' }"></view>
          </view>
          <text>1000m</text>
        </view>
        <view class="range-value">当前：<text class="strong">{{ settings.fence_radius }}m</text></view>
        <view class="rule-note">
          🐱 猫咪默认 100m（楼栋范围）· 🐶 狗狗默认 300m（小区范围）
        </view>
      </view>

      <view class="switch-row">
        <view class="switch-info">
          <view class="switch-title">进入围栏提醒</view>
          <view class="switch-sub">宠物回到安全区域时通知</view>
        </view>
        <view class="switch" :class="{ on: settings.enter_fence_notify }" @tap="settings.enter_fence_notify = !settings.enter_fence_notify"></view>
      </view>
    </view>

    <!-- 其他报警 -->
    <view class="card">
      <view class="card-title">设备状态提醒</view>
      <view class="switch-row">
        <view class="switch-info">
          <view class="switch-title">低电量提醒</view>
          <view class="switch-sub">电量低于阈值时通知</view>
        </view>
        <view class="switch" :class="{ on: settings.low_battery }" @tap="settings.low_battery = !settings.low_battery"></view>
      </view>
      <view class="switch-row">
        <view class="switch-info">
          <view class="switch-title">设备离线提醒</view>
          <view class="switch-sub">离线超过 30 分钟通知</view>
        </view>
        <view class="switch" :class="{ on: settings.offline_warning }" @tap="settings.offline_warning = !settings.offline_warning"></view>
      </view>
      <view class="switch-row">
        <view class="switch-info">
          <view class="switch-title">拆卸检测</view>
          <view class="switch-sub">检测到设备被拆卸立即报警</view>
        </view>
        <view class="switch" :class="{ on: settings.tamper_detected }" @tap="settings.tamper_detected = !settings.tamper_detected"></view>
      </view>
    </view>

    <!-- 通知渠道 -->
    <view class="card">
      <view class="card-title">通知渠道</view>
      <view class="switch-row">
        <view class="switch-info">
          <view class="switch-title">Push 推送</view>
          <view class="switch-sub">微信订阅消息推送</view>
        </view>
        <view class="switch" :class="{ on: settings.push_notify }" @tap="settings.push_notify = !settings.push_notify"></view>
      </view>
      <view class="switch-row">
        <view class="switch-info">
          <view class="switch-title">App 内通知</view>
          <view class="switch-sub">小程序内弹窗提醒</view>
        </view>
        <view class="switch" :class="{ on: settings.app_notify }" @tap="settings.app_notify = !settings.app_notify"></view>
      </view>
    </view>

    <!-- S11 紧急联系人 -->
    <view class="card">
      <view class="card-title">📞 紧急联系人</view>
      <view class="card-sub">报警时同步通知紧急联系人</view>

      <view v-for="(c, i) in contacts" :key="i" class="contact-item">
        <view class="contact-info">
          <view class="contact-name">{{ c.name }} · {{ relationLabel(c.relation) }}</view>
          <view class="contact-phone">{{ c.phone }}</view>
        </view>
        <view class="contact-del" @tap="delContact(i)">删除</view>
      </view>

      <view v-if="contacts.length < 3" class="add-contact-form">
        <view class="form-row">
          <input v-model="newContact.name" placeholder="姓名" maxlength="10" class="input-half" />
          <input v-model="newContact.phone" placeholder="手机号" type="number" maxlength="11" class="input-half" />
        </view>
        <view class="form-row">
          <picker :range="relationOptions" @change="newContact.relation = relationOptions[$event.detail.value]">
            <view class="picker">{{ newContact.relation || '选择关系' }}</view>
          </picker>
          <view class="btn-sm" @tap="addContact">+ 添加</view>
        </view>
      </view>
      <view v-if="contacts.length >= 3" class="hint-text">最多添加 3 位紧急联系人</view>
    </view>

    <view class="save-btn" :class="{ saving }" @tap="save">保存设置</view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { http } from '@/utils/request'

const petId = ref(0)
const settings = ref({
  fence_enabled: true,
  fence_radius: 300,
  enter_fence_notify: false,
  low_battery: true,
  offline_warning: true,
  tamper_detected: true,
  push_notify: true,
  app_notify: true,
})
const saving = ref(false)
const fenceCenter = ref({ lat: 34.7466, lng: 113.6253 })

// 紧急联系人
const contacts = ref<{ phone: string; name: string; relation: string }[]>([])
const newContact = ref({ name: '', phone: '', relation: '家人' })
const relationOptions = ['家人', '配偶', '子女', '父母', '朋友']
const fenceMarker = computed(() => ({
  id: 1, latitude: fenceCenter.value.lat, longitude: fenceCenter.value.lng,
  iconPath: '/static/marker-dog.png', width: 32, height: 32
}))
function onMapTap(e: any) { fenceCenter.value = { lat: e.detail.latitude, lng: e.detail.longitude } }

const radiusPct = computed(() => {
  const v = settings.value.fence_radius
  return Math.min(100, Math.max(0, ((v - 50) / (1000 - 50)) * 100))
})

onLoad(async (options: any) => {
  petId.value = Number(options.id || 0)
  await loadPet()
  await loadSettings()
  await loadContacts()
})

async function loadPet() {
  try {
    const pet = await http.get<any>(`/pets/${petId.value}`)
    if (pet) {
      settings.value.fence_enabled = pet.fence_enabled
      settings.value.fence_radius = pet.fence_radius || (pet.type === 'cat' ? 100 : 300)
      if (pet.fence_center_lat) fenceCenter.value = { lat: pet.fence_center_lat, lng: pet.fence_center_lng || fenceCenter.value.lng }
    }
  } catch (e) { /* 静默 */ }
}

async function loadSettings() {
  try {
    const s = await http.get<any>('/alarms/settings')
    if (s) {
      settings.value.enter_fence_notify = !!s.enter_fence_notify
      settings.value.low_battery = s.low_battery_threshold != null
      settings.value.offline_warning = !!s.offline_warning
      settings.value.push_notify = !!s.push_notify
    }
  } catch (e) { /* 静默 */ }
}

async function loadContacts() {
  try {
    const data = await http.get<any[]>('/users/me/contacts')
    contacts.value = data || []
  } catch (e) { /* 静默 */ }
}

function relationLabel(r: string) { return r }
function addContact() {
  if (!newContact.value.name.trim() || !newContact.value.phone.trim()) {
    uni.showToast({ title: '姓名和手机号必填', icon: 'none' })
    return
  }
  if (!/^1\d{10}$/.test(newContact.value.phone.trim())) {
    uni.showToast({ title: '手机号格式不正确', icon: 'none' })
    return
  }
  contacts.value.push({ ...newContact.value })
  newContact.value = { name: '', phone: '', relation: '家人' }
}
function delContact(i: number) { contacts.value.splice(i, 1) }

async function save() {
  saving.value = true
  try {
    // 1. 保存宠物围栏
    await http.put(`/pets/${petId.value}/fence`, {
      fence_enabled: settings.value.fence_enabled,
      fence_radius: settings.value.fence_radius,
      fence_center_lat: fenceCenter.value.lat,
      fence_center_lng: fenceCenter.value.lng,
    })
    // 2. 保存报警设置
    await http.put('/alarms/settings', {
      enter_fence_notify: settings.value.enter_fence_notify,
      low_battery_threshold: settings.value.low_battery ? 20 : null,
      leave_fence_notify: settings.value.fence_enabled,
    })
    // 3. 保存紧急联系人
    await http.put('/users/me/contacts', { contacts: contacts.value })
    uni.showToast({ title: '保存成功！', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 800)
  } catch (e: any) {
    uni.showToast({ title: e.message || '保存失败', icon: 'none' })
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
.field { margin: 24rpx 0; }
.label { font-size: 24rpx; color: #6b7280; margin-bottom: 16rpx; }
.slider-row { display: flex; align-items: center; gap: 16rpx; font-size: 22rpx; color: #9aa0a6; }
.slider { flex: 1; height: 8rpx; background: #e5e7eb; border-radius: 999rpx; position: relative; }
.slider-fill { position: absolute; height: 100%; background: #3d6cf5; border-radius: 999rpx; }
.knob { position: absolute; top: 50%; transform: translate(-50%,-50%); width: 30rpx; height: 30rpx; background: #fff; border: 6rpx solid #3d6cf5; border-radius: 50%; }
.range-value { text-align: center; font-size: 26rpx; color: #6b7280; margin-top: 14rpx; }
.strong { color: #3d6cf5; font-weight: 700; font-size: 30rpx; }
.rule-note { margin-top: 14rpx; font-size: 22rpx; color: #9aa0a6; background: #f8f9fb; border-radius: 12rpx; padding: 14rpx; }
.save-btn { margin: 30rpx 24rpx 0; text-align: center; background: linear-gradient(135deg, #5b8cff, #3d6cf5); color: #fff; border-radius: 999rpx; padding: 24rpx 0; font-size: 30rpx; font-weight: 600; }
.save-btn.saving { opacity: .6; }

/* 紧急联系人 */
.card-sub { font-size: 22rpx; color: #9aa0a6; margin: -4rpx 0 16rpx; }
.contact-item { display: flex; align-items: center; justify-content: space-between; padding: 20rpx 0; border-bottom: 1rpx solid #f3f4f6; }
.contact-info { flex: 1; }
.contact-name { font-size: 28rpx; font-weight: 600; }
.contact-phone { font-size: 22rpx; color: #9aa0a6; margin-top: 4rpx; }
.contact-del { font-size: 24rpx; color: #ef4444; }
.add-contact-form { margin-top: 20rpx; }
.form-row { display: flex; gap: 12rpx; margin-bottom: 12rpx; align-items: center; }
.input-half { flex: 1; border: 1rpx solid #e5e7eb; border-radius: 10rpx; padding: 12rpx 16rpx; font-size: 26rpx; }
.picker { flex: 1; border: 1rpx solid #e5e7eb; border-radius: 10rpx; padding: 12rpx 16rpx; font-size: 26rpx; color: #6b7280; }
.btn-sm { background: #3d6cf5; color: #fff; padding: 10rpx 24rpx; border-radius: 10rpx; font-size: 24rpx; font-weight: 600; white-space: nowrap; }
.hint-text { font-size: 22rpx; color: #9aa0a6; margin-top: 12rpx; }
</style>
