<template>
  <view class="page">

    <view class="form-block">
      <view class="label">设备 SN / 激活码</view>
      <input
        v-model="form.sn"
        class="input"
        placeholder="请输入设备 SN"
        maxlength="32"
      />
      <input
        v-model="form.activation_code"
        class="input second"
        placeholder="请输入激活码"
        maxlength="20"
      />
      <view class="scan-hint" @tap="onScanUnused">输入 SN 或扫码。相机不可用时可改用手动输入。</view>

      <view v-if="errorText" class="err-box">{{ errorText }}</view>

      <view
        class="btn-primary submit"
        :class="{ loading }"
        @tap="handleSubmit"
      >
        {{ loading ? '绑定中，请稍候。' : (errorText ? '重新绑定' : '绑定定位器') }}
      </view>
      <view class="hint">绑定后即可查看位置与围栏告警。</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { http } from '@/utils/request'

const form = reactive({ sn: '', activation_code: '' })
const pets = ref<any[]>([])
const loading = ref(false)
const errorText = ref('')

onMounted(async () => {
  try {
    pets.value = (await http.get<any[]>('/pets')) || []
  } catch (e) { /* 忽略 */ }
})

function onScanUnused() {
  uni.showToast({ title: '暂时无法使用相机，请改用手动输入。', icon: 'none' })
}

async function handleSubmit() {
  if (loading.value) return
  if (!form.sn.trim() || !form.activation_code.trim()) {
    errorText.value = '请先填写设备 SN 和激活码。'
    return
  }
  errorText.value = ''
  loading.value = true
  try {
    await http.post<any>('/devices/register', {
      sn: form.sn.trim().toUpperCase(),
      activation_code: form.activation_code.trim(),
    })
    const first = pets.value[0]
    if (first) {
      try {
        await http.post('/devices/bind', {
          sn: form.sn.trim().toUpperCase(),
          pet_id: first.id,
        })
      } catch (e: any) {
        const msg = String(e?.message || '')
        if (/已绑定|其他宠物/.test(msg)) {
          errorText.value = '该设备已绑定其他宠物。'
          return
        }
        throw e
      }
    }
    uni.showToast({ title: '绑定成功', icon: 'none' })
    setTimeout(() => uni.navigateBack(), 800)
  } catch (e: any) {
    const msg = String(e?.message || '')
    if (/已绑定|其他宠物/.test(msg)) {
      errorText.value = '该设备已绑定其他宠物。'
    } else {
      errorText.value = '未找到该设备或激活码不正确，请检查后重试。'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--pt-bg); }
.form-block { padding: 32rpx; }
.label { font-size: 26rpx; font-weight: 400; color: var(--pt-fg-2); margin-bottom: 16rpx; }
.input {
  background: var(--pt-surface);
  border: 1rpx solid var(--pt-border);
  border-radius: 24rpx;
  padding: 24rpx 28rpx;
  font-size: 28rpx;
  color: var(--pt-fg);
}
.input.second { margin-top: 16rpx; }
.scan-hint {
  margin: 16rpx 0 8rpx;
  font-size: 24rpx;
  color: var(--pt-fg-3);
  font-weight: 400;
}
.submit { margin-top: 8rpx; }
.hint { margin-top: 16rpx; font-size: 22rpx; color: var(--pt-fg-3); line-height: 1.5; }
</style>
