<script setup lang="ts">
import { onLaunch } from '@dcloudio/uni-app'

onLaunch(() => {
  console.log('[宠迹] 小程序启动')
})
</script>

<style lang="scss">
/* 全局样式 */
page {
  background-color: #f6f7fb;
  font-size: 28rpx;
  color: #1f2329;
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
}

/* 通用按钮 */
.btn-primary {
  background: linear-gradient(135deg, #5b8cff, #3d6cf5);
  color: #fff;
  border-radius: 44rpx;
  font-size: 30rpx;
  font-weight: 600;
  padding: 22rpx 0;
  text-align: center;
}

.btn-primary:active {
  opacity: 0.85;
}

/* 通用卡片 */
.card {
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  margin: 20rpx 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.04);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120rpx 0;
  color: #9aa0a6;
  font-size: 26rpx;
}
</style>
