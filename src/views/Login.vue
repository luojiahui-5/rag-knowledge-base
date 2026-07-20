<template>
  <div class="login-page">
    <!-- ==================== 左侧品牌区 ==================== -->
    <div class="left-panel">
      <!-- 网格背景 -->
      <div class="grid-bg"></div>

      <!-- 浮动光点 -->
      <div class="particles">
        <span v-for="i in 20" :key="i" class="particle" :style="particleStyle(i)"></span>
      </div>

      <!-- 品牌区 -->
      <div class="brand-header">
        <div class="brand-icon">
          <svg viewBox="0 0 40 40" fill="none" class="brand-icon-svg">
            <rect x="4" y="4" width="32" height="32" rx="8" stroke="url(#iconGrad)" stroke-width="2" fill="none" />
            <circle cx="20" cy="14" r="5" fill="url(#iconGrad)" opacity="0.8" />
            <path d="M10 28 L20 22 L30 28" stroke="url(#iconGrad)" stroke-width="2" stroke-linecap="round" />
            <path d="M13 31 L20 26 L27 31" stroke="url(#iconGrad)" stroke-width="1.5" stroke-linecap="round" opacity="0.5" />
            <defs>
              <linearGradient id="iconGrad" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#00d4ff" />
                <stop offset="100%" stop-color="#0066ff" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <h1 class="brand-title">企业级智能知识库系统</h1>
        <p class="brand-subtitle">基于 RAG 技术的新一代智能知识管理平台</p>
      </div>

      <!-- 4 个功能标签 2x2 -->
      <div class="feature-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none">
              <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="1.5" />
              <path d="M20 20l-3.5-3.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
            </svg>
          </div>
          <div class="feature-text">
            <div class="feature-title">智能检索</div>
            <div class="feature-desc">语义级精准搜索</div>
          </div>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="5" r="2" stroke="currentColor" stroke-width="1.5" />
              <circle cx="5" cy="19" r="2" stroke="currentColor" stroke-width="1.5" />
              <circle cx="19" cy="19" r="2" stroke="currentColor" stroke-width="1.5" />
              <path d="M12 7v3" stroke="currentColor" stroke-width="1.5" />
              <path d="M7.5 10L6 17" stroke="currentColor" stroke-width="1.5" />
              <path d="M16.5 10L18 17" stroke="currentColor" stroke-width="1.5" />
            </svg>
          </div>
          <div class="feature-text">
            <div class="feature-title">知识图谱</div>
            <div class="feature-desc">多维度关联挖掘</div>
          </div>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none">
              <rect x="3" y="3" width="18" height="12" rx="2" stroke="currentColor" stroke-width="1.5" />
              <path d="M7 21v-6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
              <path d="M12 21v-6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
              <path d="M17 21v-6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
            </svg>
          </div>
          <div class="feature-text">
            <div class="feature-title">RAG 增强</div>
            <div class="feature-desc">大模型私有化部署</div>
          </div>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M12 2L3 7v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7L12 2z" stroke="currentColor" stroke-width="1.5" />
              <path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </div>
          <div class="feature-text">
            <div class="feature-title">安全可靠</div>
            <div class="feature-desc">企业级权限管控</div>
          </div>
        </div>
      </div>

      <!-- 底部科技球体 -->
      <div class="globe-wrapper">
        <div class="globe">
          <div class="globe-grid"></div>
          <div class="globe-glow"></div>
        </div>
        <div class="orbit orbit-1"></div>
        <div class="orbit orbit-2"></div>
        <div class="orbit orbit-3"></div>
        <div class="globe-dots">
          <span v-for="i in 8" :key="i" class="globe-dot" :style="dotStyle(i)"></span>
        </div>
      </div>
    </div>

    <!-- ==================== 右侧登录区 ==================== -->
    <div class="right-panel">
      <!-- 右侧装饰光点 -->
      <div class="right-particles">
        <span v-for="i in 12" :key="'r'+i" class="r-particle" :style="rParticleStyle(i)"></span>
      </div>
      <!-- 右侧小行星 -->
      <div class="right-globe">
        <div class="rg-core"></div>
        <div class="rg-ring rgr-1"></div>
        <div class="rg-ring rgr-2"></div>
      </div>

      <div class="login-card">
        <h2 class="login-title">欢迎登录</h2>
        <p class="login-subtitle">请使用您的企业账号登录系统</p>

        <div class="login-form">
          <!-- 账号 -->
          <div class="input-group">
            <label class="input-label">账号</label>
            <div class="input-wrapper">
              <span class="input-icon">
                <svg viewBox="0 0 20 20" fill="none">
                  <circle cx="10" cy="7" r="4" stroke="currentColor" stroke-width="1.5" />
                  <path d="M3 18c0-3.87 3.13-7 7-7s7 3.13 7 7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                </svg>
              </span>
              <input ref="usernameRef" v-model="username" type="text" class="form-input" placeholder="请输入您的账号" @keydown.enter="toDashboard" />
            </div>
          </div>

          <!-- 密码 -->
          <div class="input-group">
            <label class="input-label">登录密码</label>
            <div class="input-wrapper">
              <span class="input-icon">
                <svg viewBox="0 0 20 20" fill="none">
                  <rect x="4" y="8" width="12" height="9" rx="2" stroke="currentColor" stroke-width="1.5" />
                  <path d="M7 8V6a3 3 0 016 0v2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                  <circle cx="10" cy="13" r="1.2" fill="currentColor" />
                </svg>
              </span>
              <input v-model="password" type="password" class="form-input" placeholder="请输入您的登录密码" @keydown.enter="toDashboard" />
            </div>
          </div>

          <!-- 记住我 & 忘记密码 -->
          <div class="form-options">
            <label class="remember-me">
              <input type="checkbox" class="checkbox" />
              <span class="checkmark"></span>
              <span class="remember-text">记住我</span>
            </label>
            <a href="#" class="forgot-link">忘记密码？</a>
          </div>

          <!-- 错误提示 -->
          <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

          <!-- 登录按钮 -->
          <button class="login-btn" :class="{ loading }" :disabled="loading" @click="toDashboard">
            <span v-if="!loading" class="btn-text">登 录</span>
            <span v-else class="btn-spinner"></span>
          </button>

          <!-- 注册引导 -->
          <p class="register-hint">
            还没有账号？<a href="#" class="register-link">立即注册</a>
          </p>
        </div>

        <!-- 底部文字链接 -->
        <div class="card-footer">
          <a href="#" class="footer-link">使用条款</a>
          <span class="footer-divider">|</span>
          <a href="#" class="footer-link">隐私政策</a>
          <span class="footer-divider">|</span>
          <a href="#" class="footer-link">帮助中心</a>
        </div>
      </div>

      <!-- 版权 -->
      <p class="copyright">© 2025 企业级智能知识库系统. All rights reserved.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const errorMsg = ref('')

const username = ref('')
const password = ref('')
const usernameRef = ref(null)

onMounted(() => {
  setTimeout(() => usernameRef.value?.focus(), 100)
})

const toDashboard = async () => {
  if (!username.value || !password.value) {
    errorMsg.value = '请输入账号和密码'
    return
  }
  errorMsg.value = ''
  loading.value = true
  try {
    await authStore.login(username.value, password.value)
    router.push('/dashboard')
  } catch (err) {
    const detail = err.response?.data?.detail
    errorMsg.value = typeof detail === 'string' ? detail : '登录失败，请检查网络连接或确认后端已启动'
  } finally {
    loading.value = false
  }
}

const rParticleStyle = (i) => ({
  top: ((i * 19 + 11) % 100) + '%',
  left: ((i * 29 + 5) % 100) + '%',
  width: (1.5 + (i % 3)) + 'px',
  height: (1.5 + (i % 3)) + 'px',
  animationDelay: ((i * 0.9) % 5) + 's',
  opacity: 0.08 + (i % 4) * 0.04,
})

const particleStyle = (i) => {
  const top = ((i * 17 + 3) % 100)
  const left = ((i * 23 + 7) % 100)
  const size = 2 + (i % 4)
  const delay = (i * 0.7) % 5
  const opacity = 0.15 + (i % 5) * 0.1
  return {
    top: `${top}%`,
    left: `${left}%`,
    width: `${size}px`,
    height: `${size}px`,
    animationDelay: `${delay}s`,
    opacity,
  }
}

const dotStyle = (i) => {
  const angle = (i / 8) * 360 * Math.PI / 180
  const radius = 38 + (i % 3) * 6
  return {
    top: `${50 + Math.sin(angle) * (radius / 100) * 50}%`,
    left: `${50 + Math.cos(angle) * (radius / 100) * 50}%`,
    animationDelay: `${i * 0.3}s`,
  }
}
</script>

<style scoped>
/* ==================== 全局布局 ==================== */
.login-page {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
  background: linear-gradient(160deg, #060b1f 0%, #0a1030 30%, #0d1538 60%, #091028 100%);
}

/* ==================== 左侧品牌区 ==================== */
.left-panel {
  position: relative;
  width: 42%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 44px 40px 0;
  overflow: hidden;
  flex-shrink: 0;
}

/* 网格 */
.grid-bg {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(0, 180, 255, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 180, 255, 0.04) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(ellipse 70% 70% at 50% 50%, black 30%, transparent 70%);
  pointer-events: none;
}

/* 浮动粒子 */
.particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.particle {
  position: absolute;
  border-radius: 50%;
  background: #00d4ff;
  box-shadow: 0 0 6px 2px rgba(0, 212, 255, 0.4);
  animation: floatUp 6s ease-in-out infinite;
}

@keyframes floatUp {
  0%, 100% { transform: translateY(0) scale(1); opacity: 0.2; }
  50% { transform: translateY(-30px) scale(1.8); opacity: 0.7; }
}

/* 品牌标题 */
.brand-header {
  position: relative;
  z-index: 2;
  text-align: center;
  margin-top: 12px;
}

.brand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  margin-bottom: 20px;
  background: rgba(0, 180, 255, 0.08);
  border-radius: 14px;
  border: 1px solid rgba(0, 200, 255, 0.2);
}

.brand-icon-svg { width: 36px; height: 36px; }

.brand-title {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 2px;
  color: #ffffff;
  margin: 0 0 10px;
  text-shadow: 0 0 30px rgba(0, 200, 255, 0.3);
}

.brand-subtitle {
  font-size: 14px;
  font-weight: 300;
  letter-spacing: 3px;
  color: rgba(255, 255, 255, 0.55);
  margin: 0;
}

/* ==================== 功能标签 2x2 ==================== */
.feature-grid {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  width: 100%;
  max-width: 420px;
  margin-top: 38px;
}

.feature-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  transition: background 0.3s, border-color 0.3s;
  cursor: default;
}

.feature-card:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(0, 200, 255, 0.25);
}

.feature-icon {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 200, 255, 0.1);
  border-radius: 8px;
  color: #00d4ff;
}

.feature-icon svg { width: 20px; height: 20px; }

.feature-title {
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
  line-height: 1.4;
}

.feature-desc {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  line-height: 1.4;
  margin-top: 1px;
}

/* ==================== 科技球体 ==================== */
.globe-wrapper {
  position: relative;
  width: 250px;
  height: 250px;
  margin-top: auto;
  margin-bottom: 36px;
  z-index: 2;
  flex-shrink: 0;
}

.globe {
  position: absolute;
  inset: 26px;
  border-radius: 50%;
  overflow: hidden;
}

.globe-grid {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background:
    repeating-linear-gradient(0deg, transparent, transparent 14px, rgba(0, 180, 255, 0.12) 14px, rgba(0, 180, 255, 0.12) 15px),
    repeating-linear-gradient(90deg, transparent, transparent 14px, rgba(0, 180, 255, 0.12) 14px, rgba(0, 180, 255, 0.12) 15px);
  mask-image: radial-gradient(circle at 50% 50%, black 55%, transparent 95%);
}

.globe-glow {
  position: absolute;
  inset: -40px;
  border-radius: 50%;
  background: radial-gradient(circle at 50% 50%, rgba(0, 200, 255, 0.15) 0%, rgba(0, 150, 255, 0.05) 40%, transparent 70%);
  filter: blur(20px);
  pointer-events: none;
}

/* 轨道环 */
.orbit {
  position: absolute;
  border: 1px solid rgba(0, 200, 255, 0.18);
  border-radius: 50%;
  pointer-events: none;
}

.orbit-1 { inset: 0; transform: rotateX(70deg); }
.orbit-2 { inset: -12px; transform: rotateX(50deg) rotateY(30deg); }
.orbit-3 { inset: -6px; transform: rotateX(75deg) rotateY(-20deg); }

/* 光点 */
.globe-dots { position: absolute; inset: 26px; }

.globe-dot {
  position: absolute;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: #00e5ff;
  box-shadow: 0 0 6px 2px rgba(0, 220, 255, 0.6);
  animation: dotPulse 3s ease-in-out infinite;
}

@keyframes dotPulse {
  0%, 100% { transform: scale(1); box-shadow: 0 0 6px 2px rgba(0, 220, 255, 0.6); }
  50% { transform: scale(2); box-shadow: 0 0 12px 4px rgba(0, 220, 255, 0.9); }
}

/* ==================== 右侧登录区 ==================== */
.right-panel {
  width: 58%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
  overflow: hidden;
}

/* 右侧装饰光点 */
.right-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.r-particle {
  position: absolute;
  border-radius: 50%;
  background: #4a8cf7;
  box-shadow: 0 0 4px 1px rgba(74,140,247,0.3);
  animation: rFloat 8s ease-in-out infinite;
}

@keyframes rFloat {
  0%, 100% { transform: translateY(0) scale(1); opacity: 0.15; }
  50% { transform: translateY(-20px) scale(2); opacity: 0.4; }
}

/* 右侧装饰小球体 */
.right-globe {
  position: absolute;
  bottom: -60px;
  right: -40px;
  width: 200px;
  height: 200px;
  opacity: 0.12;
  pointer-events: none;
}

.rg-core {
  position: absolute;
  inset: 30px;
  border-radius: 50%;
  background: radial-gradient(circle at 40% 40%, rgba(74,140,247,0.5), rgba(74,140,247,0.05));
  box-shadow: 0 0 60px rgba(74,140,247,0.15);
}

.rg-ring {
  position: absolute;
  border: 1px solid rgba(74,140,247,0.3);
  border-radius: 50%;
}

.rgr-1 { inset: 10px; transform: rotateX(60deg); }
.rgr-2 { inset: 0; transform: rotateX(75deg) rotateY(-25deg); }

/* 登录卡片 — 纯白实体 + 阴影 */
.login-card {
  width: 424px;
  max-width: 90%;
  background: #ffffff;
  border-radius: 16px;
  padding: 40px 44px 34px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06), 0 1px 4px rgba(0, 0, 0, 0.04);
  border: 1px solid #edf0f4;
}

.login-title {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  text-align: center;
  margin: 0 0 6px;
}

.login-subtitle {
  font-size: 13px;
  color: #9099a8;
  text-align: center;
  margin: 0 0 30px;
}

/* 表单 */
.login-form {
  display: flex;
  flex-direction: column;
}

.input-group {
  margin-bottom: 18px;
}

.input-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: #a0aec0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  z-index: 1;
}

.input-icon svg { width: 18px; height: 18px; }

.form-input {
  width: 100%;
  height: 46px;
  padding: 0 16px 0 42px;
  font-size: 14px;
  color: #1a1a2e;
  background: #f5f6f8;
  border: 1px solid #e8ecf1;
  border-radius: 10px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: inherit;
}

.form-input::placeholder {
  color: #b0b8c4;
}

.form-input:focus {
  border-color: #4a8cf7;
  box-shadow: 0 0 0 3px rgba(74, 140, 247, 0.1);
}

/* 记住我 & 忘记密码 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 4px 0 22px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 7px;
  cursor: pointer;
  user-select: none;
}

.checkbox { display: none; }

.checkmark {
  width: 16px;
  height: 16px;
  border: 1.5px solid #cfd7e2;
  border-radius: 4px;
  background: #f5f6f8;
  transition: all 0.2s;
  flex-shrink: 0;
  position: relative;
}

.checkbox:checked + .checkmark {
  background: #4a8cf7;
  border-color: #4a8cf7;
}

.checkbox:checked + .checkmark::after {
  content: '';
  position: absolute;
  left: 4px;
  top: 1px;
  width: 5px;
  height: 9px;
  border: 2px solid #fff;
  border-top: none;
  border-right: none;
  transform: rotate(-45deg);
}

.remember-text {
  font-size: 13px;
  color: #6b7280;
}

.forgot-link {
  font-size: 13px;
  color: #4a8cf7;
  text-decoration: none;
  transition: color 0.2s;
}

.forgot-link:hover { color: #3b7de6; }

/* 错误提示 */
.error-msg {
  color: #f87171;
  font-size: 13px;
  text-align: center;
  margin: 0 0 12px;
  padding: 8px 12px;
  background: rgba(239, 68, 68, 0.08);
  border-radius: 8px;
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  height: 46px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #4a6cf7 0%, #5b8cf7 40%, #4ab8d4 100%);
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 6px;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.15s;
  font-family: inherit;
}

.login-btn:hover {
  opacity: 0.92;
}

.login-btn:active {
  transform: scale(0.99);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: wait;
}

.btn-spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 注册引导 */
.register-hint {
  text-align: center;
  font-size: 13px;
  color: #9099a8;
  margin: 20px 0 0;
}

.register-link {
  color: #4a8cf7;
  text-decoration: none;
  font-weight: 500;
  margin-left: 2px;
}

.register-link:hover { color: #3b7de6; }

/* 卡片底部链接 */
.card-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  padding-top: 18px;
  border-top: 1px solid #f2f4f7;
}

.footer-link {
  font-size: 12px;
  color: #b0b8c4;
  text-decoration: none;
  transition: color 0.2s;
}

.footer-link:hover { color: #6b7280; }

.footer-divider {
  color: #e0e4ea;
  font-size: 12px;
}

/* 版权 */
.copyright {
  position: absolute;
  bottom: 28px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.35);
  text-align: center;
}

/* ==================== 响应式 ==================== */
@media (max-width: 1024px) {
  .left-panel { width: 44%; padding: 36px 28px 0; }
  .right-panel { width: 56%; }
  .brand-title { font-size: 24px; }
  .login-card { width: 370px; padding: 32px 34px 28px; }
}

@media (max-width: 768px) {
  .login-page { flex-direction: column; }
  .left-panel { display: none; }
  .right-panel { width: 100%; }
  .login-card { width: 92%; max-width: 400px; }
}
</style>
