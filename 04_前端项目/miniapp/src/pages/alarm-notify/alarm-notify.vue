<template>
  <view class="page">
    <!-- 通知渠道 -->
    <view class="section">
      <view class="section-title">🔔 通知渠道</view>
      <view class="switch-row">
        <text>App Push 推送</text>
        <switch :checked="form.notify_push" color="#3D6CF5" @change="form.notify_push = $event.detail.value" />
      </view>
      <view class="switch-row">
        <view class="switch-label">
          <text>短信通知</text>
          <text class="pro-tag">Pro</text>
        </view>
        <switch :checked="form.notify_sms" color="#3D6CF5" @change="form.notify_sms = $event.detail.value" />
      </view>
    </view>

    <!-- 紧急联系人 -->
    <view class="section">
      <view class="section-title">🆘 紧急联系人</view>
      <view class="section-desc">报警发生时同步通知紧急联系人（最多 3 人）</view>

      <view v-for="(c, i) in form.emergency_contacts" :key="i" class="contact-card">
        <view class="contact-info">
          <text class="contact-name">{{ c.name }}</text>
          <text class="contact-phone">{{ c.phone }}</text>
        </view>
        <view class="contact-del" @tap="removeContact(i)">删除</view>
      </view>

      <view v-if="form.emergency_contacts.length < 3" class="add-contact" @tap="showAdd = true">
        + 添加紧急联系人
      </view>
    </view>

    <view class="save-btn" @tap="handleSave">保存设置</view>

    <!-- 添加弹窗 -->
    <view v-if="showAdd" class="modal-mask" @tap="showAdd = false">
      <view class="modal-card" @tap.stop>
        <view class="modal-title">添加紧急联系人</view>
        <input class="modal-input" v-model="newName" placeholder="联系人姓名" />
        <input class="modal-input" v-model="newPhone" placeholder="手机号" type="number" maxlength="11" />
        <view class="modal-btns">
          <view class="mbtn cancel" @tap="showAdd = false">取消</view>
          <view class="mbtn ok" @tap="addContact">添加</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { http } from '@/utils/request'

const form = reactive({
  leave_fence_notify: true,
  enter_fence_notify: false,
  low_battery_threshold: 20,
  quiet_hours_start: '',
  quiet_hours_end: '',
  emergency_contacts: [] as { name: string; phone: string }[],
  notify_push: true,
  notify_sms: false
})

const showAdd = ref(false)
const newName = ref('')
const newPhone = ref('')

onShow(async () => {
  try {
    const data = await http.get<any>('/alarms/settings')
    if (data) Object.assign(form, data)
  } catch (e) { /* 默认值 */ }
})

function addContact() {
  if (!newName.value.trim() || !newPhone.value.trim()) {
    uni.showToast({ title: '请填写完整', icon: 'none' })
    return
  }
  if (!/^1[3-9]\d{9}$/.test(newPhone.value)) {
    uni.showToast({ title: '手机号格式错误', icon: 'none' })
    return
  }
  form.emergency_contacts.push({ name: newName.value.trim(), phone: newPhone.value.trim() })
  newName.value = ''
  newPhone.value = ''
  showAdd.value = false
}

function removeContact(i: number) {
  form.emergency_contacts.splice(i, 1)
}

async function handleSave() {
  try {
    await http.put('/alarms/settings', form)
    uni.showToast({ title: '已保存', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e.message || '保存失败', icon: 'none' })
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: #f6f7fb; padding: 24rpx 0 80rpx; }
.section { background: #fff; margin: 24rpx 24rpx; border-radius: 16rpx; padding: 24rpx; }
.section-title { font-size: 30rpx; font-weight: 700; }
.section-desc { font-size: 24rpx; color: #9aa0a6; margin-top: 8rpx; }
.switch-row { display: flex; justify-content: space-between; align-items: center; padding: 20rpx 0; border-bottom: 1rpx solid #f3f4f6; }
.switch-row:last-child { border-bottom: none; }
.switch-label { display: flex; align-items: center; gap: 8rpx; }
.pro-tag { font-size: 20rpx; background: #3d6cf5; color: #fff; padding: 2rpx 10rpx; border-radius: 999rpx; }
.contact-card { display: flex; justify-content: space-between; align-items: center; padding: 20rpx 0; border-bottom: 1rpx solid #f3f4f6; }
.contact-name { font-size: 28rpx; font-weight: 600; }
.contact-phone { font-size: 24rpx; color: #9aa0a6; margin-left: 16rpx; }
.contact-del { font-size: 24rpx; color: #ef4444; }
.add-contact { text-align: center; padding: 24rpx 0; font-size: 26rpx; color: #3d6cf5; font-weight: 600; }
.save-btn { margin: 48rpx 24rpx; background: #3d6cf5; color: #fff; text-align: center; padding: 28rpx 0; border-radius: 16rpx; font-size: 30rpx; font-weight: 700; }
.modal-mask { position: fixed; inset: 0; background: rgba(0,0,0,.5); display: flex; align-items: center; justify-content: center; z-index: 999; }
.modal-card { background: #fff; border-radius: 20rpx; padding: 40rpx 32rpx; width: 600rpx; }
.modal-title { font-size: 32rpx; font-weight: 700; margin-bottom: 24rpx; }
.modal-input { border: 1rpx solid #e5e7eb; border-radius: 12rpx; padding: 18rpx 20rpx; font-size: 28rpx; margin-bottom: 16rpx; }
.modal-btns { display: flex; gap: 20rpx; margin-top: 16rpx; }
.mbtn { flex:1; text-align: center; padding: 20rpx 0; border-radius: 12rpx; font-size: 28rpx; font-weight: 600; }
.mbtn.cancel { background: #f3f4f6; color: #6b7280; }
.mbtn.ok { background: #3d6cf5; color: #fff; }
</style>
