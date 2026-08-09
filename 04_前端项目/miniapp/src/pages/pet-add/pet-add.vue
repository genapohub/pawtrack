<template>
  <view class="page">
    <view class="card">
      <!-- 宠物名称 -->
      <view class="form-item">
        <view class="label">宠物名称 <text class="required">*</text></view>
        <input v-model="form.name" class="input" placeholder="如：旺财" maxlength="50" />
      </view>

      <!-- 宠物类型 -->
      <view class="form-item">
        <view class="label">宠物类型 <text class="required">*</text></view>
        <view class="type-picker">
          <view
            class="type-option"
            :class="{ active: form.pet_type === 'cat' }"
            @tap="selectType('cat')"
          >
            🐱 猫咪
          </view>
          <view
            class="type-option"
            :class="{ active: form.pet_type === 'dog' }"
            @tap="selectType('dog')"
          >
            🐶 狗狗
          </view>
        </view>
        <view class="type-hint">
          {{ form.pet_type === 'cat' ? '猫咪定位器：BLE + WiFi 室内定位' : '狗狗定位器：GPS + 4G 户外定位' }}
        </view>
      </view>

      <!-- 品种 -->
      <view class="form-item">
        <view class="label">品种</view>
        <input v-model="form.breed" class="input" placeholder="如：布偶猫 / 金毛" maxlength="50" />
      </view>

      <!-- 性别 -->
      <view class="form-item">
        <view class="label">性别</view>
        <view class="type-picker">
          <view
            v-for="g in genders"
            :key="g.value"
            class="type-option small"
            :class="{ active: form.gender === g.value }"
            @tap="form.gender = g.value"
          >{{ g.label }}</view>
        </view>
      </view>

      <!-- 体重 -->
      <view class="form-item">
        <view class="label">体重（kg）</view>
        <input v-model="form.weight" class="input" type="digit" placeholder="如：5.2" />
      </view>

      <!-- 围栏设置 -->
      <view class="form-item">
        <view class="label-row">
          <view class="label">安全围栏</view>
          <switch
            :checked="form.fence_enabled"
            color="#3D6CF5"
            @change="form.fence_enabled = $event.detail.value"
          />
        </view>
        <view v-if="form.fence_enabled" class="slider-row">
          <view class="slider-label">围栏半径：{{ form.fence_radius }}m</view>
          <slider
            :value="form.fence_radius"
            min="20"
            max="5000"
            step="10"
            activeColor="#3D6CF5"
            @change="form.fence_radius = $event.detail.value"
          />
          <view class="slider-hint">
            默认：猫咪 100m · 狗狗 300m（{{ form.pet_type === 'cat' ? '🐱' : '🐶' }}）
          </view>
        </view>
      </view>

      <!-- 提交 -->
      <view class="btn-primary submit-btn" :class="{ loading }" @tap="handleSubmit">
        {{ loading ? '提交中...' : '添加宠物' }}
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { http } from '@/utils/request'

const genders = [
  { label: '未知', value: 'unknown' },
  { label: '男孩', value: 'male' },
  { label: '女孩', value: 'female' },
]

const form = reactive({
  name: '',
  pet_type: 'dog' as 'cat' | 'dog',
  breed: '',
  gender: 'unknown' as 'unknown' | 'male' | 'female',
  weight: '',
  fence_enabled: true,
  fence_radius: 300,
})

const loading = ref(false)

function selectType(t: 'cat' | 'dog') {
  form.pet_type = t
  // 切换类型时同步默认围栏半径（猫 100m / 狗 300m）
  form.fence_radius = t === 'cat' ? 100 : 300
}

async function handleSubmit() {
  if (!form.name.trim()) {
    uni.showToast({ title: '请输入宠物名称', icon: 'none' })
    return
  }

  // 按类型给默认围栏半径
  if (form.fence_enabled) {
    if (form.pet_type === 'cat' && form.fence_radius >= 300) form.fence_radius = 100
    if (form.pet_type === 'dog' && form.fence_radius <= 100) form.fence_radius = 300
  }

  loading.value = true
  try {
    await http.post('/pets', {
      name: form.name.trim(),
      pet_type: form.pet_type,
      breed: form.breed.trim() || undefined,
      gender: form.gender,
      weight: form.weight ? parseFloat(form.weight) : undefined,
      fence_enabled: form.fence_enabled,
      fence_radius: form.fence_radius,
    })
    uni.showToast({ title: '添加成功！', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 800)
  } catch (e: any) {
    uni.showToast({ title: e.message || '添加失败', icon: 'none' })
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

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.input {
  background: #f6f7fb;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  font-size: 28rpx;
}

/* 类型选择 */
.type-picker {
  display: flex;
  gap: 20rpx;
}

.type-option {
  flex: 1;
  text-align: center;
  padding: 28rpx 0;
  border-radius: 16rpx;
  background: #f6f7fb;
  border: 3rpx solid transparent;
  font-size: 28rpx;
  font-weight: 600;
  color: #6b7280;
}

.type-option.active {
  background: #eef2ff;
  border-color: #3d6cf5;
  color: #3d6cf5;
}

.type-option.small {
  padding: 16rpx 0;
  font-size: 26rpx;
}

.type-hint {
  margin-top: 14rpx;
  font-size: 22rpx;
  color: #9aa0a6;
}

/* 围栏滑块 */
.slider-row {
  margin-top: 10rpx;
}

.slider-label {
  font-size: 26rpx;
  color: #3d6cf5;
  font-weight: 600;
}

.slider-hint {
  font-size: 22rpx;
  color: #9aa0a6;
  margin-top: 8rpx;
}

.submit-btn {
  margin-top: 20rpx;
}

.submit-btn.loading {
  opacity: 0.6;
}
</style>
