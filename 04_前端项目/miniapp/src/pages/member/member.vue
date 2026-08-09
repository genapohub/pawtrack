<template>
  <view class="page">
    <!-- 当前会员状态 -->
    <view class="member-hero" :class="'lv-' + (sub?.level || 'free')">
      <view class="hero-icon">{{ levelIcon(sub?.level) }}</view>
      <view class="hero-info">
        <view class="hero-level">{{ levelLabel(sub?.level) }}</view>
        <view class="hero-expire" v-if="sub?.expire_at">
          有效期至 {{ formatDate(sub.expire_at) }}
          <text v-if="sub?.auto_renew" class="renew-tag">自动续费</text>
        </view>
        <view class="hero-expire" v-else>未开通会员</view>
      </view>
    </view>

    <!-- 权益对比 -->
    <view class="card">
      <view class="card-title">会员权益</view>
      <view v-for="b in benefits" :key="b.level" class="benefit-row">
        <view class="benefit-level">{{ levelIcon(b.level) }} {{ levelLabel(b.level) }}</view>
        <view class="benefit-items">{{ b.items.join(' · ') }}</view>
      </view>
    </view>

    <!-- 套餐列表 -->
    <view class="card">
      <view class="card-title">开通会员</view>
      <view v-for="plan in plans" :key="plan.plan" class="plan-card" @tap="buyPlan(plan)">
        <view class="plan-info">
          <view class="plan-name">{{ plan.name }}</view>
          <view class="plan-days">{{ plan.days }} 天</view>
        </view>
        <view class="plan-price">
          <text class="price-symbol">¥</text>
          <text class="price-num">{{ plan.price }}</text>
          <view class="buy-btn" :class="{ paying: payingPlan === plan.plan }">
            {{ payingPlan === plan.plan ? '支付中...' : sub?.plan === plan.plan ? '当前套餐' : '开通' }}
          </view>
        </view>
      </view>
      <view class="pay-tip">💳 MVP 阶段为模拟支付，点击即开通</view>
    </view>

    <!-- 订单历史 -->
    <view class="card">
      <view class="card-title" @tap="loadHistory">订单历史 <text class="arrow">▾</text></view>
      <view v-for="o in orders" :key="o.id" class="order-row">
        <view class="order-info">
          <view class="order-name">{{ o.type === 'subscription' ? '会员订阅' : o.type }}</view>
          <view class="order-no">{{ o.order_no }}</view>
        </view>
        <view class="order-right">
          <view class="order-amount">¥{{ o.amount }}</view>
          <view class="order-status" :class="o.status">{{ orderStatus(o.status) }}</view>
        </view>
      </view>
      <view v-if="orders.length === 0" class="empty-tip">暂无订单</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { http } from '@/utils/request'

interface Plan {
  plan: string
  name: string
  price: number
  level: string
  days: number
}

const plans = ref<Plan[]>([])
const sub = ref<any>(null)
const orders = ref<any[]>([])
const payingPlan = ref('')

const LEVEL_META: Record<string, { label: string; icon: string }> = {
  free: { label: '免费版', icon: '🆓' },
  basic: { label: '基础版', icon: '⭐' },
  pro: { label: 'Pro版', icon: '💎' },
}

const benefits = [
  { level: 'free', items: ['定位 5 分钟/次', '轨迹 7 天', '围栏报警', '1 台设备'] },
  { level: 'basic', items: ['定位 5 秒/次', '轨迹无限', '围栏报警', '3 台设备', '附近宠物'] },
  { level: 'pro', items: ['定位 5 秒/次', '轨迹无限', '围栏报警', '10 台设备', '家人共享 5 人', '优先客服'] },
]

function levelIcon(level: string | undefined): string {
  return LEVEL_META[level || 'free'].icon
}

function levelLabel(level: string | undefined): string {
  return LEVEL_META[level || 'free'].label
}

function formatDate(iso: string): string {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('zh-CN')
}

function orderStatus(status: string): string {
  return { pending: '待支付', paid: '已支付', failed: '失败', cancelled: '已取消', refunded: '已退款' }[status] || status
}

async function loadAll() {
  try {
    const [plansData, subData] = await Promise.all([
      http.get<Plan[]>('/orders/plans'),
      http.get<any>('/orders/subscription'),
    ])
    plans.value = plansData || []
    sub.value = subData || null
  } catch (e: any) {
    uni.showToast({ title: e.message || '加载失败', icon: 'none' })
  }
}

async function loadHistory() {
  try {
    const data = await http.get<any>(`/orders/history?page=1&size=20`)
    orders.value = data?.items || data || []
  } catch (e) {
    // 忽略
  }
}

/** 购买套餐（MVP 模拟支付） */
async function buyPlan(plan: Plan) {
  if (payingPlan.value) return
  payingPlan.value = plan.plan
  try {
    // 1. 创建订单
    const order = await http.post<any>('/orders', { plan: plan.plan, pay_channel: 'wechat' })
    const orderNo = order?.order_no
    if (!orderNo) {
      uni.showToast({ title: '订单创建失败', icon: 'none' })
      return
    }
    // 2. 模拟支付回调
    const txnId = `MOCK${Date.now()}${Math.floor(Math.random() * 10000)}`
    await http.post('/orders/pay-callback', { order_no: orderNo, transaction_id: txnId })
    uni.showToast({ title: `🎉 ${plan.name} 开通成功！`, icon: 'success' })
    loadAll()
    loadHistory()
  } catch (e: any) {
    uni.showToast({ title: e.message || '开通失败', icon: 'none' })
  } finally {
    payingPlan.value = ''
  }
}

onShow(loadAll)
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f6f7fb;
  padding: 24rpx 0 60rpx;
}

/* Hero */
.member-hero {
  display: flex;
  align-items: center;
  gap: 24rpx;
  margin: 0 24rpx 20rpx;
  border-radius: 24rpx;
  padding: 40rpx;
  background: linear-gradient(135deg, #8b9dfa, #3d6cf5);
}

.member-hero.lv-free {
  background: linear-gradient(135deg, #a5b4fc, #6366f1);
}

.member-hero.lv-basic {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
}

.member-hero.lv-pro {
  background: linear-gradient(135deg, #a78bfa, #7c3aed);
}

.hero-icon {
  font-size: 80rpx;
}

.hero-info {
  color: #fff;
}

.hero-level {
  font-size: 40rpx;
  font-weight: 700;
}

.hero-expire {
  font-size: 24rpx;
  opacity: 0.9;
  margin-top: 8rpx;
}

.renew-tag {
  background: rgba(255, 255, 255, 0.25);
  padding: 4rpx 12rpx;
  border-radius: 999rpx;
  font-size: 20rpx;
  margin-left: 12rpx;
}

/* 卡片 */
.card-title {
  font-size: 30rpx;
  font-weight: 700;
  margin-bottom: 20rpx;
}

.benefit-row {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
  padding: 14rpx 0;
  border-bottom: 2rpx solid #f3f4f6;
}

.benefit-row:last-child {
  border-bottom: none;
}

.benefit-level {
  font-size: 26rpx;
  font-weight: 600;
  white-space: nowrap;
  width: 160rpx;
}

.benefit-items {
  font-size: 24rpx;
  color: #6b7280;
  flex: 1;
  line-height: 1.6;
}

/* 套餐 */
.plan-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx;
  border-radius: 16rpx;
  background: #f6f7fb;
  margin-bottom: 16rpx;
}

.plan-name {
  font-size: 30rpx;
  font-weight: 700;
}

.plan-days {
  font-size: 24rpx;
  color: #9aa0a6;
  margin-top: 4rpx;
}

.plan-price {
  display: flex;
  align-items: baseline;
  gap: 4rpx;
}

.price-symbol {
  font-size: 24rpx;
  color: #ef4444;
  font-weight: 600;
}

.price-num {
  font-size: 44rpx;
  font-weight: 700;
  color: #ef4444;
}

.buy-btn {
  margin-left: 20rpx;
  padding: 12rpx 28rpx;
  border-radius: 999rpx;
  background: #3d6cf5;
  color: #fff;
  font-size: 26rpx;
  font-weight: 600;
}

.buy-btn.paying {
  opacity: 0.6;
}

.pay-tip {
  font-size: 22rpx;
  color: #9aa0a6;
  margin-top: 8rpx;
}

/* 订单 */
.order-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18rpx 0;
  border-bottom: 2rpx solid #f3f4f6;
}

.order-name {
  font-size: 28rpx;
  font-weight: 600;
}

.order-no {
  font-size: 22rpx;
  color: #9aa0a6;
  margin-top: 4rpx;
}

.order-right {
  text-align: right;
}

.order-amount {
  font-size: 30rpx;
  font-weight: 700;
}

.order-status {
  font-size: 22rpx;
  color: #22c55e;
}

.order-status.pending {
  color: #f59e0b;
}

.order-status.failed,
.order-status.cancelled {
  color: #9aa0a6;
}

.empty-tip {
  text-align: center;
  color: #9aa0a6;
  padding: 30rpx 0;
  font-size: 26rpx;
}

.arrow {
  color: #9aa0a6;
  font-size: 26rpx;
}
</style>
