<template>
  <view class="page">

    <view v-if="loadError" class="pt-card">
      <view class="err-box">列表加载失败，请稍后重试。</view>
      <view class="btn-primary" @tap="load">重新加载</view>
    </view>

    <view v-else-if="loading" class="pt-card skeleton">列表加载中...</view>

    <view v-else-if="!pets.length" class="pt-card">
      <view class="empty-title">还没有宠物，先添加一只</view>
      <view class="btn-primary" @tap="goAdd">添加宠物</view>
    </view>

    <view v-else class="list">
      <view v-for="p in pets" :key="p.id" class="pt-card pet-card" @tap="goDetail(p)">
        <view class="avatar-mark" :class="p.type==='cat'?'avatar-cat':'avatar-dog'">{{ (p.name||'宠').slice(0,1) }}</view>
        <view class="info">
          <view class="name">{{ p.name }}</view>
          <view class="sub">{{ p.breed || (p.type==='cat'?'猫':'狗') }} · {{ p.type==='cat'?'宅家':'户外' }}</view>
        </view>
        <text class="tag" :class="p.fence_enabled ? 'tag-success' : 'tag-muted'">{{ p.fence_enabled ? '围栏开启' : '围栏关闭' }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { http } from '@/utils/request'

const pets = ref<any[]>([])
const loading = ref(true)
const loadError = ref(false)

onShow(load)

async function load() {
  loading.value = true
  loadError.value = false
  try {
    pets.value = (await http.get<any[]>('/pets')) || []
  } catch (e) {
    loadError.value = true
  } finally {
    loading.value = false
  }
}

function goDetail(p: any) {
  uni.navigateTo({ url: '/pages/pet-detail/pet-detail?id=' + p.id })
}
function goAdd() { uni.navigateTo({ url: '/pages/pet-add/pet-add' }) }
</script>

<style scoped>
.page { min-height: 100vh; background: var(--pt-bg); }
.list { padding-top: 24rpx; }
.pet-card { display: flex; align-items: center; gap: 20rpx; }
.info { flex: 1; }
.name { font-size: 30rpx; font-weight: 500; color: var(--pt-fg); }
.sub { margin-top: 4rpx; font-size: 22rpx; color: var(--pt-fg-2); }
.skeleton { color: var(--pt-fg-3); }
.empty-title { font-size: 30rpx; font-weight: 500; margin-bottom: 24rpx; }
</style>
