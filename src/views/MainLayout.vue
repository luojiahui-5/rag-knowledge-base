<template>
  <div class="app-shell">
    <!-- ========== 侧边栏 ========== -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <!-- Logo -->
      <div class="sidebar-brand">
        <div class="brand-logo">
          <svg viewBox="0 0 32 32" fill="none" class="logo-svg">
            <rect x="2" y="2" width="28" height="28" rx="7" stroke="url(#logoGrad)" stroke-width="2" fill="none"/>
            <circle cx="16" cy="11" r="4.5" fill="url(#logoGrad)" opacity="0.85"/>
            <path d="M7 23l5.5-4.5L16 21l4-3 5 4" stroke="url(#logoGrad)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            <defs><linearGradient id="logoGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#00d4ff"/><stop offset="100%" stop-color="#4a6cf7"/></linearGradient></defs>
          </svg>
        </div>
        <span v-show="!sidebarCollapsed" class="brand-name">智能知识库系统</span>
      </div>

      <!-- 导航菜单 -->
      <nav class="sidebar-nav">
        <a
          v-for="item in navItems"
          :key="item.key"
          :class="['nav-item', { active: isActive(item) }]"
          @click="navigateTo(item)"
        >
          <span class="nav-icon" v-html="item.icon"></span>
          <span v-show="!sidebarCollapsed" class="nav-label">{{ item.label }}</span>
        </a>
      </nav>

      <!-- 底部折叠按钮 -->
      <div class="sidebar-footer">
        <button class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed">
          <svg viewBox="0 0 20 20" fill="none" :class="{ rotated: sidebarCollapsed }">
            <path d="M7 4l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </aside>

    <!-- ========== 主区域 ========== -->
    <div class="main-area">
      <!-- 顶栏 -->
      <header class="topbar">
        <div class="topbar-left">
          <span class="current-page-title">{{ currentPageTitle }}</span>
        </div>
        <div class="topbar-right">
          <!-- 搜索 -->
          <div class="global-search" @click="showSearch = true">
            <svg viewBox="0 0 20 20" fill="none" class="search-icon"><circle cx="9" cy="9" r="6" stroke="currentColor" stroke-width="1.5"/><path d="M14 14l3.5 3.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
            <span class="search-placeholder">搜索文档、知识库...</span>
            <kbd class="search-kbd">⌘K</kbd>
          </div>
          <!-- 通知 -->
          <button class="icon-btn" :class="{ 'has-dot': unreadCount > 0 }" @click="showNotify = !showNotify">
            <svg viewBox="0 0 20 20" fill="none"><path d="M12 16a2 2 0 01-4 0M5 7a5 5 0 0110 0v3l2 3v1H3v-1l2-3V7z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
          <!-- 通知弹窗 -->
          <div v-if="showNotify" class="notify-popup" @click.stop>
            <div class="notify-header">
              <h4>消息通知</h4>
              <button class="notify-mark" @click="markAllRead">全部已读</button>
            </div>
            <div class="notify-list" v-if="notifications.length">
              <div v-for="n in notifications" :key="n.id" :class="['notify-item', { unread: !n.read }]" @click="n.read = true">
                <div class="notify-icon" :class="n.type">{{ n.icon }}</div>
                <div class="notify-body">
                  <p class="notify-title">{{ n.title }}</p>
                  <p class="notify-time">{{ n.time }}</p>
                </div>
                <span v-if="!n.read" class="notify-dot"></span>
              </div>
            </div>
            <div v-else class="notify-empty">暂无通知</div>
          </div>
          <!-- 用户菜单 -->
          <div class="user-menu" @click="showUserMenu = !showUserMenu">
            <div class="user-avatar">{{ userInitial }}</div>
            <span class="user-name">{{ userName }}</span>
            <svg viewBox="0 0 20 20" fill="none" class="chevron" :class="{ rotated: showUserMenu }"><path d="M5 7l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <!-- 用户弹窗 -->
          <div v-if="showUserMenu" class="user-popup" @click.stop>
            <div class="user-popup-header">
              <div class="user-avatar lg">{{ userInitial }}</div>
              <div>
                <p class="user-popup-name">{{ userName }}</p>
                <p class="user-popup-role">{{ userRoleLabel }}</p>
              </div>
            </div>
            <div class="user-popup-links">
              <a class="user-popup-link" @click="goTo('/dashboard/settings'); showUserMenu = false">
                <svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="3" stroke="currentColor" stroke-width="1.3"/><path d="M8 3v2M8 11v2M3.5 6.5l1.7 1M10.8 8.5l1.7 1M3.5 9.5l1.7-1M10.8 7.5l1.7-1" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>
                系统设置
              </a>
              <a class="user-popup-link" @click="handleLogout">
                <svg viewBox="0 0 16 16" fill="none"><path d="M6 3V2h7v12H6v-1M2 8h9M9 5l3 3-3 3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>
                退出登录
              </a>
            </div>
          </div>
        </div>
      </header>

      <!-- ===== 全局搜索弹窗 ===== -->
      <div v-if="showSearch" class="search-overlay" @click.self="showSearch = false">
        <div class="search-modal">
          <div class="search-modal-input">
            <svg viewBox="0 0 20 20" fill="none" class="search-modal-icon"><circle cx="9" cy="9" r="6" stroke="currentColor" stroke-width="1.5"/><path d="M14 14l3.5 3.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
            <input ref="searchInputRef" v-model="searchKeyword" class="search-modal-field" placeholder="搜索文档、知识库..." @keydown.escape="showSearch = false" @keydown.enter="searchSelect(0)" @keydown.down.prevent="searchIdx = Math.min(searchIdx + 1, searchResults.length - 1)" @keydown.up.prevent="searchIdx = Math.max(searchIdx - 1, 0)" />
            <kbd class="search-modal-kbd">ESC</kbd>
          </div>
          <div class="search-results" v-if="searchKeyword && searchResults.length">
            <div v-for="(r, i) in searchResults" :key="r.id" :class="['search-result-item', { active: i === searchIdx }]" @click="searchSelect(i)">
              <div class="search-result-icon" :class="r.type">
                <svg v-if="r.type === 'kb'" viewBox="0 0 16 16" fill="none"><path d="M2 4h3l2-2h7v8M2 4v9a1 1 0 001 1h9M2 4l1.5-1.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>
                <svg v-else viewBox="0 0 16 16" fill="none"><rect x="2" y="1" width="12" height="14" rx="1.5" stroke="currentColor" stroke-width="1.2"/><path d="M5 5h6M5 8h6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
              </div>
              <div class="search-result-body">
                <span class="search-result-name">{{ r.name }}</span>
                <span class="search-result-meta">{{ r.type === 'kb' ? '知识库' : '文档' }} · {{ r.desc }}</span>
              </div>
            </div>
          </div>
          <div v-else-if="searchKeyword" class="search-no-result">未找到相关结果</div>
        </div>
      </div>

      <!-- 内容区 -->
      <main class="content-area">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const sidebarCollapsed = ref(false)

const allNavItems = [
  { key: 'overview', route: '/dashboard/overview', label: '仪表盘', adminOnly: false, icon: '<svg viewBox="0 0 20 20" fill="none"><rect x="2" y="2" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="1.5"/><rect x="11" y="2" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="1.5"/><rect x="2" y="11" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="1.5"/><rect x="11" y="11" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="1.5"/></svg>' },
  { key: 'ask', route: '/dashboard/ask', label: '智能问答', adminOnly: false, icon: '<svg viewBox="0 0 20 20" fill="none"><path d="M3 4h14a1.5 1.5 0 011.5 1.5v7A1.5 1.5 0 0117 14H7l-4 3v-3a1.5 1.5 0 01-1-1.5v-7A1.5 1.5 0 013 4z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="8" cy="9" r="1" fill="currentColor"/><circle cx="12" cy="9" r="1" fill="currentColor"/><circle cx="10" cy="9" r="1" fill="currentColor"/></svg>' },
  { key: 'documents', route: '/dashboard/documents', label: '文档管理', adminOnly: false, icon: '<svg viewBox="0 0 20 20" fill="none"><path d="M5 2h7l4 4v11a1.5 1.5 0 01-1.5 1.5h-8A1.5 1.5 0 014 17V3.5A1.5 1.5 0 015.5 2z" stroke="currentColor" stroke-width="1.5"/><path d="M12 2v4h4" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M7 10h6M7 13h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>' },
  { key: 'knowledge', route: '/dashboard/knowledge', label: '知识库', adminOnly: false, icon: '<svg viewBox="0 0 20 20" fill="none"><path d="M3 5h4l2-2h8a1.5 1.5 0 011.5 1.5V9M3 5v11a1.5 1.5 0 001.5 1.5H12M3 5l1.5-1.5M16 15a.5.5 0 01-.5.5M12 11v6l3.5-3-3.5-3z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>' },
  { key: 'settings', route: '/dashboard/settings', label: '系统设置', adminOnly: true, icon: '<svg viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="3" stroke="currentColor" stroke-width="1.5"/><path d="M10 3v2M10 15v2M3.5 6.5l1.7 1M14.8 13l1.7 1M3.5 13.5l1.7-1M14.8 7l1.7-1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>' },
]

const navItems = computed(() => allNavItems.filter(item => !item.adminOnly || authStore.isAdmin))
const isActive = (item) => route.path === item.route
const currentPageTitle = computed(() => { const item = navItems.value.find(n => isActive(n)); return item ? item.label : '仪表盘' })
const navigateTo = (item) => { router.push(item.route) }

// ===== 用户信息 =====
const userName = computed(() => authStore.user?.display_name || authStore.user?.username || '用户')
const userInitial = computed(() => (authStore.user?.display_name || authStore.user?.username || '?')[0])
const userRoleLabel = computed(() => ({ admin: '超级管理员', editor: '编辑者', viewer: '阅读者' }[authStore.user?.role] || ''))
const showUserMenu = ref(false)

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const goTo = (path) => {
  router.push(path)
}

// ===== 通知 =====
const showNotify = ref(false)
const notifications = ref([])
const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)
const markAllRead = () => { notifications.value.forEach(n => n.read = true) }

// ===== 全局搜索 =====
const showSearch = ref(false)
const searchKeyword = ref('')
const searchIdx = ref(0)
const searchInputRef = ref(null)
const searchResults = ref([])

const openSearch = () => {
  showSearch.value = true
  searchKeyword.value = ''
  searchResults.value = []
  nextTick(() => searchInputRef.value?.focus())
}

const doSearch = async () => {
  const kw = searchKeyword.value.trim()
  if (!kw) { searchResults.value = []; return }
  // 搜索知识库
  try {
    const token = sessionStorage.getItem('token')
    const [kbResp, docResp] = await Promise.all([
      fetch('/api/v1/knowledge', { headers: { Authorization: `Bearer ${token}` } }),
      fetch('/api/v1/documents', { headers: { Authorization: `Bearer ${token}` } }),
    ])
    const kbs = kbResp.ok ? await kbResp.json() : []
    const docs = docResp.ok ? await docResp.json() : []
    const q = kw.toLowerCase()
    searchResults.value = [
      ...kbs.filter(k => k.name.toLowerCase().includes(q)).map(k => ({ id: 'kb-' + k.id, type: 'kb', name: k.name, desc: k.department || k.description?.slice(0, 20) || '', route: '/dashboard/knowledge' })),
      ...docs.filter(d => d.original_name.toLowerCase().includes(q)).map(d => ({ id: 'doc-' + d.id, type: 'doc', name: d.original_name, desc: d.file_type?.toUpperCase() || '', route: '/dashboard/documents' })),
    ].slice(0, 8)
  } catch { searchResults.value = [] }
  searchIdx.value = 0
}

const searchSelect = (i) => {
  const r = searchResults.value[i]
  if (r) {
    router.push(r.route)
    showSearch.value = false
  }
}

// 键盘快捷键
const onKeyDown = (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    if (showSearch.value) showSearch.value = false
    else openSearch()
  }
  if (e.key === 'Escape') {
    showSearch.value = false
    showNotify.value = false
    showUserMenu.value = false
  }
}

onMounted(() => { document.addEventListener('keydown', onKeyDown); authStore.fetchUser() })
onUnmounted(() => { document.removeEventListener('keydown', onKeyDown) })

// 监听搜索关键词变化
watch(searchKeyword, doSearch)
</script>

<style scoped>
/* ==================== 整体 ==================== */
.app-shell {
  display: flex;
  width: 100vw;
  height: 100vh;
  background: #060b1f;
  overflow: hidden;
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
}

/* ==================== 侧边栏 ==================== */
.sidebar {
  width: 232px;
  height: 100%;
  background: #080e24;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  transition: width 0.25s ease;
  flex-shrink: 0;
  z-index: 10;
}

.sidebar.collapsed {
  width: 64px;
}

/* 品牌区 */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.brand-logo {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
}

.logo-svg {
  width: 100%;
  height: 100%;
}

.brand-name {
  font-size: 15px;
  font-weight: 700;
  color: #e2e8f0;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

/* 导航 */
.sidebar-nav {
  flex: 1;
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.45);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  white-space: nowrap;
  font-size: 13.5px;
  font-weight: 500;
}

.nav-item:hover {
  color: rgba(255, 255, 255, 0.75);
  background: rgba(255, 255, 255, 0.04);
}

.nav-item.active {
  color: #e2e8f0;
  background: rgba(74, 140, 247, 0.12);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 18px;
  background: linear-gradient(180deg, #00d4ff, #4a8cf7);
  border-radius: 0 3px 3px 0;
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-icon :deep(svg) {
  width: 20px;
  height: 20px;
}

.nav-badge {
  margin-left: auto;
  font-size: 11px;
  font-weight: 600;
  background: #ef4444;
  color: #fff;
  padding: 1px 6px;
  border-radius: 10px;
  line-height: 1.5;
}

/* 侧边栏底部 */
.sidebar-footer {
  padding: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.collapse-btn {
  width: 100%;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.collapse-btn:hover {
  color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.04);
}

.collapse-btn svg {
  width: 18px;
  height: 18px;
  transition: transform 0.25s ease;
}

.collapse-btn svg.rotated {
  transform: rotate(180deg);
}

/* ==================== 顶栏 ==================== */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
}

.current-page-title {
  font-size: 15px;
  font-weight: 600;
  color: #e2e8f0;
  letter-spacing: 0.5px;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
}

/* 全局搜索 */
.global-search {
  position: relative;
  cursor: pointer;
  display: flex;
  align-items: center;
  width: 260px;
  height: 36px;
  padding: 0 12px 0 34px;
  background: rgba(255,255,255,.05);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 8px;
  transition: border-color .2s;
}
.global-search:hover { border-color: rgba(255,255,255,.14); }

.search-icon {
  position: absolute;
  left: 12px;
  width: 16px;
  height: 16px;
  color: rgba(255, 255, 255, 0.3);
  pointer-events: none;
}

.search-kbd {
  margin-left: auto;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-family: inherit;
  flex-shrink: 0;
}

/* 图标按钮 */
.icon-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.icon-btn:hover {
  color: rgba(255, 255, 255, 0.7);
  background: rgba(255, 255, 255, 0.05);
}

.icon-btn svg {
  width: 20px;
  height: 20px;
}

.icon-btn.has-dot::after {
  content: '';
  position: absolute;
  top: 8px;
  right: 8px;
  width: 7px;
  height: 7px;
  background: #ef4444;
  border-radius: 50%;
  border: 2px solid #080e24;
}

/* 用户菜单 */
.user-menu {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 10px 4px 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.user-menu:hover {
  background: rgba(255, 255, 255, 0.04);
}

.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4a8cf7, #00d4ff);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  flex-shrink: 0;
}

.user-name {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.chevron {
  width: 16px;
  height: 16px;
  color: rgba(255, 255, 255, 0.3);
}

/* ==================== 内容区 ==================== */
.content-area {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 滚动条 */
.content-area::-webkit-scrollbar {
  width: 4px;
}

.content-area::-webkit-scrollbar-track {
  background: transparent;
}

.content-area::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
}

.content-area::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.15);
}

/* ===== 搜索框（顶栏） ===== */
.search-placeholder { font-size: 13px; color: rgba(255,255,255,.25); }

/* ===== 通知弹窗 ===== */
.notify-popup { position: absolute; top: 48px; right: 52px; width: 340px; background: #111a35; border: 1px solid rgba(255,255,255,.08); border-radius: 14px; box-shadow: 0 16px 48px rgba(0,0,0,.5); z-index: 60; overflow: hidden; }
.notify-header { display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,.05); }
.notify-header h4 { font-size: 14px; font-weight: 600; color: #e2e8f0; margin: 0; }
.notify-mark { font-size: 11px; color: #8bb8ff; background: none; border: none; cursor: pointer; font-family: inherit; }
.notify-mark:hover { opacity: .8; }
.notify-list { max-height: 320px; overflow-y: auto; }
.notify-list::-webkit-scrollbar { width: 3px; }
.notify-list::-webkit-scrollbar-thumb { background: rgba(255,255,255,.06); border-radius: 2px; }
.notify-item { display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,.025); cursor: pointer; transition: background .15s; position: relative; }
.notify-item:hover { background: rgba(255,255,255,.02); }
.notify-item.unread { background: rgba(74,140,247,.04); }
.notify-icon { font-size: 18px; flex-shrink: 0; width: 20px; text-align: center; }
.notify-body { flex: 1; min-width: 0; }
.notify-title { font-size: 12.5px; color: rgba(255,255,255,.6); margin: 0; line-height: 1.5; }
.notify-time { font-size: 11px; color: rgba(255,255,255,.2); margin: 2px 0 0; }
.notify-dot { width: 7px; height: 7px; background: #4a8cf7; border-radius: 50%; flex-shrink: 0; margin-top: 6px; }
.notify-empty { padding: 32px 0; text-align: center; font-size: 13px; color: rgba(255,255,255,.2); }

/* ===== 用户弹窗 ===== */
.user-popup { position: absolute; top: 48px; right: 8px; width: 220px; background: #111a35; border: 1px solid rgba(255,255,255,.08); border-radius: 14px; box-shadow: 0 16px 48px rgba(0,0,0,.5); z-index: 60; overflow: hidden; }
.user-popup-header { display: flex; align-items: center; gap: 12px; padding: 16px; border-bottom: 1px solid rgba(255,255,255,.05); }
.user-avatar.lg { width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg,#4a8cf7,#00d4ff); display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 700; color: #fff; flex-shrink: 0; }
.user-popup-name { font-size: 14px; font-weight: 600; color: #e2e8f0; margin: 0; }
.user-popup-role { font-size: 11px; color: rgba(255,255,255,.35); margin: 2px 0 0; }
.user-popup-links { padding: 6px; }
.user-popup-link { display: flex; align-items: center; gap: 8px; padding: 9px 12px; border-radius: 8px; font-size: 13px; color: rgba(255,255,255,.5); cursor: pointer; transition: all .15s; }
.user-popup-link:hover { background: rgba(255,255,255,.04); color: rgba(255,255,255,.75); }
.user-popup-link svg { width: 16px; height: 16px; flex-shrink: 0; }
.chevron.rotated { transform: rotate(180deg); }

/* ===== 全局搜索弹窗 ===== */
.search-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.5); backdrop-filter: blur(3px); display: flex; justify-content: center; padding-top: 15vh; z-index: 200; }
.search-modal { width: 540px; max-width: 90vw; background: #111a35; border: 1px solid rgba(255,255,255,.08); border-radius: 16px; overflow: hidden; box-shadow: 0 24px 64px rgba(0,0,0,.6); animation: searchIn .15s ease; }
@keyframes searchIn { from { opacity: 0; transform: translateY(-8px) scale(.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
.search-modal-input { display: flex; align-items: center; gap: 10px; padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,.06); }
.search-modal-icon { width: 18px; height: 18px; color: rgba(255,255,255,.3); flex-shrink: 0; }
.search-modal-field { flex: 1; height: 32px; border: none; background: none; font-size: 15px; color: #e2e8f0; outline: none; font-family: inherit; }
.search-modal-field::placeholder { color: rgba(255,255,255,.25); }
.search-modal-kbd { font-size: 11px; color: rgba(255,255,255,.2); background: rgba(255,255,255,.05); padding: 3px 8px; border-radius: 4px; border: 1px solid rgba(255,255,255,.08); font-family: inherit; }

.search-results { max-height: 320px; overflow-y: auto; }
.search-results::-webkit-scrollbar { width: 3px; }
.search-results::-webkit-scrollbar-thumb { background: rgba(255,255,255,.06); border-radius: 2px; }
.search-result-item { display: flex; align-items: center; gap: 10px; padding: 10px 16px; cursor: pointer; transition: background .12s; }
.search-result-item:hover, .search-result-item.active { background: rgba(74,140,247,.08); }
.search-result-icon { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.search-result-icon svg { width: 16px; height: 16px; }
.search-result-icon.kb { background: rgba(0,212,255,.1); color: #00d4ff; }
.search-result-icon.doc { background: rgba(74,140,247,.1); color: #4a8cf7; }
.search-result-body { min-width: 0; }
.search-result-name { display: block; font-size: 13px; color: rgba(255,255,255,.7); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.search-result-meta { display: block; font-size: 11px; color: rgba(255,255,255,.25); margin-top: 1px; }
.search-no-result { padding: 32px 0; text-align: center; font-size: 13px; color: rgba(255,255,255,.2); }
</style>
