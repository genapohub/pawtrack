<script setup lang="ts">
import { onLaunch } from '@dcloudio/uni-app'

onLaunch(() => {
  console.log('[宠迹] 小程序启动')
})
</script>

<style lang="scss">
@import "./styles/tokens.scss";

page {
  background-color: var(--pt-bg);
  font-size: 30rpx;
  color: var(--pt-fg);
  font-family: var(--pt-font);
  font-weight: 400;
}


.pt-card {
  background: var(--pt-surface);
  border-radius: 28rpx;
  border: 1rpx solid var(--pt-border);
  padding: 32rpx;
  margin: 0 32rpx 24rpx;
}

.btn-primary {
  background: var(--pt-accent);
  color: #fff;
  border-radius: 24rpx;
  font-size: 30rpx;
  font-weight: 500;
  padding: 22rpx 0;
  text-align: center;
}

.btn-primary:active {
  background: var(--pt-accent-hover);
}

.btn-primary.disabled,
.btn-primary.loading {
  opacity: 0.55;
}

.btn-ghost {
  background: transparent;
  color: var(--pt-accent);
  border: 2rpx solid var(--pt-accent);
  border-radius: 24rpx;
  font-size: 28rpx;
  font-weight: 500;
  padding: 20rpx 0;
  text-align: center;
}

.btn-danger {
  background: var(--pt-danger);
  color: #fff;
  border-radius: 24rpx;
  font-size: 30rpx;
  font-weight: 500;
  padding: 22rpx 0;
  text-align: center;
}

.err-box {
  background: var(--pt-danger-subtle);
  color: var(--pt-danger);
  border-radius: 20rpx;
  padding: 20rpx 24rpx;
  font-size: 26rpx;
  font-weight: 400;
  line-height: 1.5;
  margin: 16rpx 0;
}

.warn-box {
  background: var(--pt-warning-subtle);
  color: var(--pt-warning);
  border-radius: 20rpx;
  padding: 20rpx 24rpx;
  font-size: 26rpx;
  font-weight: 400;
  line-height: 1.5;
  margin: 16rpx 0;
}

.tag {
  display: inline-flex;
  align-items: center;
  font-size: 22rpx;
  font-weight: 400;
  padding: 6rpx 16rpx;
  border-radius: 12rpx;
}

.tag-success {
  background: var(--pt-success-subtle);
  color: var(--pt-success);
}

.tag-warning {
  background: var(--pt-warning-subtle);
  color: var(--pt-warning);
}

.tag-muted {
  background: var(--pt-bg-muted);
  color: var(--pt-fg-3);
}

.avatar-mark {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 500;
}

.avatar-cat {
  background: var(--pt-accent-subtle);
  color: var(--pt-accent);
}

.avatar-dog {
  background: var(--pt-dog-tag-bg);
  color: var(--pt-dog-tag-fg);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 48rpx;
  color: var(--pt-fg-2);
  font-size: 28rpx;
  font-weight: 400;
  text-align: center;
  line-height: 1.5;
}
</style>
