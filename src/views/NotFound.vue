<template>
  <div class="not-found">
    <div class="nf-content">
      <div class="nf-code">404</div>
      <h1 class="nf-title">页面未找到</h1>
      <p class="nf-desc">您访问的页面不存在或已被移除</p>
      <button class="nf-btn" @click="$router.push('/dashboard')">返回首页</button>
    </div>
    <div class="nf-bg"></div>
  </div>
</template>

<style scoped>
.not-found {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(160deg, #060b1f 0%, #0a1030 30%, #0d1538 60%, #091028 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
}

.nf-bg {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(0, 180, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 180, 255, 0.03) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(ellipse 60% 60% at 50% 50%, black 30%, transparent 70%);
  pointer-events: none;
}

.nf-content {
  position: relative;
  z-index: 1;
  text-align: center;
}

.nf-code {
  font-size: 140px;
  font-weight: 800;
  background: linear-gradient(135deg, #4a8cf7 0%, #00d4ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  margin-bottom: 8px;
  letter-spacing: -4px;
}

.nf-title {
  font-size: 22px;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0 0 8px;
}

.nf-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.4);
  margin: 0 0 28px;
}

.nf-btn {
  height: 40px;
  padding: 0 28px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #4a6cf7, #5b8cf7);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
  font-family: inherit;
}

.nf-btn:hover {
  opacity: 0.9;
}
</style>
