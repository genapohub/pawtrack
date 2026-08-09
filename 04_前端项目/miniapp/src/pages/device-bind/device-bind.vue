<template>
  <view class="page">
    <view class="card">
      <!-- 设备类型说明 -->
      <view class="hw-info">
        <view class="hw-icon">{{ hwType === 'cat' ? '🐱' : '🐶' }}</view>
        <view class="hw-text">
          <view class="hw-title">{{ hwType === 'cat' ? '猫咪定位器' : '狗狗定位器' }}</view>
          <view class="hw-desc">
            {{ hwType === 'cat' ? 'BLE + WiFi 室内定位 · 适合猫猫' : 'GPS + 4G 户外定位 · 适合狗狗' }}
          </view>
        </view>
        <view class="hw-switch" @tap="hwType = hwType === 'cat' ? 'dog' : 'cat'">切换</view>
      </view>

      <!-- SN 序列号 -->
      <view class="form-item">
        <view class="label">设备序列号 SN <text class="required">*</text></view>
        <input
          v-model="form.sn"
          class="input"
          placeholder="设备机身或包装盒上的 SN 码"
          maxlength="32"
          style="text-transform: uppercase;"
        />
      </view>

      <!-- 激活码 -->
      <view class="form-item">
        <view class="label">激活码 <text class="required">*</text></view>
        <input
          v-model="form.activation_code"
          class="input"
          placeholder="购买时随附的激活码"
          maxlength="20"
        />
      </view>

      <!-- 固件版本（选填） -->
      <view class="form-item">
        <view class="label">固件版本（选填）</view>
        <input v-model="form.fw_version" class="input" placeholder="如：v1.2.0" maxlength="20" />
      </view>

      <!-- 绑定宠物 -->
      <view class="form-item">
        <view class="label">绑定宠物</view>
        <picker :range="petNames" @change="onPetChange">
          <view class="picker-box">
            {{ selectedPetName || '选择要绑定的宠物（可跳过）' }}
            <text class="picker-arrow">▾</text>
          </view>
        </picker>
      </view>

      <!-- 提交 -->
      <view class="btn-primary submit-btn" :class="{ loading }" @tap="handleSubmit">
        {{ loading ? '注册中...' : '注册并绑定设备' }}
      </view>

      <view class="tip">
        💡 注册成功后，设备会出现在「我的设备」中，可随时绑定到宠物
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted } from 'vue'
import { http } from '@/utils/request'

const hwType = ref<'cat' | 'dog'>('dog')
const form = reactive({
  sn: '',
  activation_code: '',
  fw_version: '',
})

const pets = ref<any[]>([])
const petIndex = ref(-1)
const petNames = computed(() => pets.value.map((p) => `${p.type === 'cat' ? '🐱' : '🐶'} ${p.name}`))
const selectedPetName = computed(() =>
  petIndex.value >= 0 ? petNames.value[petIndex.value] : ''
)

const loading = ref(false)

onMounted(async () => {
  try {
    const list = await http.get<any[]>('/pets')
    pets.value = list || []
  } catch (e) {
    // 忽略
  }
})

function onPetChange(e: any) {
  petIndex.value = Number(e.detail.value)
}

async function handleSubmit() {
  if (!form.sn.trim()) {
    uni.showToast({ title: '请输入设备 SN 码', icon: 'none' })
    return
  }
  if (!form.activation_code.trim()) {
    uni.showToast({ title: '请输入激活码', icon: 'none' })
    return
  }

  loading.value = true
  try {
    // 1. 注册设备（设备 JWT）
    const device = await http.post<any>('/devices/register', {
      sn: form.sn.trim().toUpperCase(),
      activation_code: form.activation_code.trim(),
      hw_type: hwType.value,
      fw_version: form.fw_version.trim() || undefined,
    })

    // 2. 绑定宠物（可选）
    let bindMsg = ''
    if (petIndex.value >= 0 && pets.value[petIndex.value]) {
      try {
        await http.post('/devices/bind', {
          sn: form.sn.trim().toUpperCase(),
          pet_id: pets.value[petIndex.value].id,
        })
        bindMsg = '，已绑定宠物'
      } catch (e) {
        bindMsg = '，宠物绑定失败请稍后重试'
      }
    }

    uni.showToast({ title: `设备注册成功${bindMsg}`, icon: 'success' })
    setTimeout(() => uni.navigateBack(), 1000)
  } catch (e: any) {
    uni.showToast({ title: e.message || '注册失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f6f7fb;
  padding: 24rpx 0 60rpx;
}

/* 硬件信息 */
.hw-info {
  display: flex;
  align-items: center;
  gap: 20rpx;
  background: #eef2ff;
  border-radius: 20rpx;
  padding: 28rpx;
  margin-bottom: 40rpx;
}

.hw-icon {
  font-size: 60rpx;
}

.hw-text {
  flex: 1;
}

.hw-title {
  font-size: 30rpx;
  font-weight: 700;
}

.hw-desc {
  font-size: 22rpx;
  color: #6b7280;
  margin-top: 4rpx;
}

.hw-switch {
  font-size: 24rpx;
  color: #3d6cf5;
  font-weight: 600;
  border: 2rpx solid #3d6cf5;
  padding: 8rpx 20rpx;
  border-radius: 999rpx;
}

/* 表单 */
.form-item {
  margin-bottom: 36rpx;
}

.label {
  font-size: 26rpx;
  color: #6b7280;
  margin-bottom: 14rpx;
}

.required {
  color: #ef4444;
}

.input {
  background: #f6f7fb;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  font-size: 28rpx;
}

.picker-box {
  background: #f6f7fb;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  font-size: 28rpx;
  color: #1f2329;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.picker-arrow {
  color: #9aa0a6;
}

.submit-btn {
  margin-top: 20rpx;
}

.submit-btn.loading {
  opacity: 0.6;
}

.tip {
  margin-top: 24rpx;
  font-size: 24rpx;
  color: #9aa0a6;
  line-height: 1.6;
}
</style>
