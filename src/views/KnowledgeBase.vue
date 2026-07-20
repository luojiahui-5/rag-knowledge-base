<template>
  <div class="page">
    <!-- ===== 顶栏 ===== -->
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">知识库管理</h2>
        <span class="page-count">共 {{ filteredList.length }} 个知识库</span>
      </div>
      <div class="toolbar-right">
        <div class="search-box">
          <svg viewBox="0 0 20 20" fill="none" class="search-box-icon"><circle cx="9" cy="9" r="6" stroke="currentColor" stroke-width="1.5"/><path d="M14 14l3.5 3.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
          <input v-model="searchQuery" class="search-box-input" placeholder="搜索知识库..." />
        </div>
        <button class="btn btn-primary" @click="openCreate">
          <svg viewBox="0 0 20 20" fill="none"><path d="M10 5v10M5 10h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          新建知识库
        </button>
      </div>
    </div>

    <!-- ===== 卡片网格 ===== -->
    <div v-if="loading" class="kb-grid">
      <div v-for="i in 6" :key="i" class="kb-card skeleton">
        <div class="skel-line w60"></div>
        <div class="skel-line w80 mt8"></div>
        <div class="skel-line w40 mt12"></div>
      </div>
    </div>

    <div v-else-if="filteredList.length === 0" class="empty-full">
      <svg viewBox="0 0 64 64" fill="none" class="empty-full-icon"><rect x="8" y="8" width="48" height="48" rx="12" stroke="currentColor" stroke-width="2"/><path d="M24 32h16M20 24h24M20 40h24" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
      <p class="empty-full-title">{{ searchQuery ? '没有匹配的知识库' : '还没有知识库' }}</p>
      <p class="empty-full-desc">{{ searchQuery ? '换个关键词试试' : '创建第一个知识库，开始管理文档' }}</p>
      <button v-if="!searchQuery" class="btn btn-primary" @click="openCreate">新建知识库</button>
    </div>

    <div v-else class="kb-grid">
      <div v-for="kb in filteredList" :key="kb.id" class="kb-card" @click="openDetail(kb)">
        <!-- 顶部色条 -->
        <div class="kb-color-strip" :style="{ background: kb.color }"></div>
        <!-- 内容 -->
        <div class="kb-card-body">
          <div class="kb-card-top">
            <div class="kb-avatar" :style="{ background: kb.color }">
              <svg viewBox="0 0 20 20" fill="none"><path d="M3 5h4l2-2h8a1.5 1.5 0 011.5 1.5V9M3 5v11a1.5 1.5 0 001.5 1.5H12M3 5l1.5-1.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
            <div class="kb-card-actions" @click.stop>
              <button class="act-icon" title="编辑" @click="openEdit(kb)"><svg viewBox="0 0 16 16" fill="none"><path d="M11 2l3 3-9 9H2v-3l9-9z" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
              <button class="act-icon danger" title="删除" @click="confirmDelete(kb)"><svg viewBox="0 0 16 16" fill="none"><path d="M3 4h10M6 4V2h4v2M5 4v9a1 1 0 001 1h4a1 1 0 001-1V4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
            </div>
          </div>
          <h3 class="kb-name">{{ kb.name }}</h3>
          <p class="kb-desc">{{ kb.description || '暂无描述' }}</p>
          <div class="kb-stats">
            <div class="kb-stat">
              <svg viewBox="0 0 16 16" fill="none" class="kb-stat-icon"><path d="M3 2h7l4 4v8a1 1 0 01-1 1H3a1 1 0 01-1-1V3a1 1 0 011-1z" stroke="currentColor" stroke-width="1.3"/></svg>
              <span class="kb-stat-val">{{ kb.docCount }}</span>
            </div>
            <div class="kb-stat">
              <svg viewBox="0 0 16 16" fill="none" class="kb-stat-icon"><path d="M3 4h10M3 8h10M3 12h7" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>
              <span class="kb-stat-val">{{ kb.chunkCount }}</span>
            </div>
            <div class="kb-stat">
              <svg viewBox="0 0 16 16" fill="none" class="kb-stat-icon"><ellipse cx="8" cy="4" rx="6" ry="2.5" stroke="currentColor" stroke-width="1.3"/><path d="M2 4v5c0 1.38 2.69 2.5 6 2.5s6-1.12 6-2.5V4" stroke="currentColor" stroke-width="1.3"/></svg>
              <span class="kb-stat-val">{{ kb.size }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 新建 / 编辑弹窗 ===== -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-card">
        <h3 class="modal-title">{{ editingKB ? '编辑知识库' : '新建知识库' }}</h3>

        <div class="form-group">
          <label class="form-label">知识库名称 <span class="required">*</span></label>
          <input class="form-field" v-model="form.name" placeholder="请输入知识库名称" maxlength="30" />
        </div>

        <div class="form-group">
          <label class="form-label">描述</label>
          <textarea class="form-field form-textarea" v-model="form.description" placeholder="简要描述知识库的内容和用途" rows="3" maxlength="200"></textarea>
        </div>

        <div class="form-group">
          <label class="form-label">所属部门</label>
          <select class="form-field form-select" v-model="form.department">
            <option value="">选择部门</option>
            <option>技术研发部</option>
            <option>产品部</option>
            <option>运维部</option>
            <option>人力资源部</option>
            <option>市场部</option>
            <option>财务部</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">主题色</label>
          <div class="color-picker">
            <button v-for="c in colors" :key="c" :class="['color-dot', { active: form.color === c }]" :style="{ background: c }" @click="form.color = c"></button>
          </div>
        </div>

        <div v-if="modalError" class="modal-error">{{ modalError }}</div>

        <div class="modal-actions">
          <button class="btn btn-ghost" @click="closeModal">取消</button>
          <button class="btn btn-primary" :disabled="!form.name || submitting" @click="saveKB">
            {{ submitting ? '保存中...' : (editingKB ? '保存修改' : '确认创建') }}
          </button>
        </div>
      </div>
    </div>

    <!-- ===== 删除确认弹窗 ===== -->
    <div v-if="showDelete" class="modal-overlay" @click.self="showDelete = null">
      <div class="modal-card modal-sm">
        <div class="delete-icon-wrap">
          <svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="11" stroke="currentColor" stroke-width="1.5"/><path d="M12 8v4M12 16h0" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </div>
        <h3 class="modal-title center">确认删除</h3>
        <p class="delete-text">确定要删除「<strong>{{ showDelete.name }}</strong>」吗？该知识库下的所有文档和切片数据将被<strong>永久删除</strong>，不可恢复。</p>
        <div class="modal-actions">
          <button class="btn btn-ghost" @click="showDelete = null">取消</button>
          <button class="btn btn-danger" @click="doDelete">确认删除</button>
        </div>
      </div>
    </div>

    <!-- ===== 详情抽屉 ===== -->
    <div v-if="showDetail" class="drawer-overlay" @click.self="showDetail = null">
      <div class="drawer">
        <div class="drawer-header">
          <div class="drawer-header-left">
            <div class="drawer-avatar" :style="{ background: showDetail.color }">
              <svg viewBox="0 0 20 20" fill="none"><path d="M3 5h4l2-2h8a1.5 1.5 0 011.5 1.5V9M3 5v11a1.5 1.5 0 001.5 1.5H12M3 5l1.5-1.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
            <div>
              <h3 class="drawer-title">{{ showDetail.name }}</h3>
              <p class="drawer-subtitle">{{ showDetail.department || '未分组' }} · {{ showDetail.updatedAt }}更新</p>
            </div>
          </div>
          <button class="drawer-close" @click="showDetail = null">&times;</button>
        </div>

        <div class="drawer-body">
          <p class="drawer-desc">{{ showDetail.description || '暂无描述' }}</p>

          <div class="drawer-stats-row">
            <div class="drawer-stat">
              <span class="drawer-stat-val">{{ showDetail.docCount }}</span>
              <span class="drawer-stat-lbl">文档总数</span>
            </div>
            <div class="drawer-stat">
              <span class="drawer-stat-val">{{ showDetail.chunkCount }}</span>
              <span class="drawer-stat-lbl">切片数</span>
            </div>
            <div class="drawer-stat">
              <span class="drawer-stat-val">{{ showDetail.size }}</span>
              <span class="drawer-stat-lbl">存储大小</span>
            </div>
          </div>

          <div class="drawer-section">
            <h4 class="drawer-section-title">最近文档</h4>
            <div v-if="detailDocs.length === 0" class="drawer-empty">暂无文档</div>
            <div v-else class="drawer-doc-list">
              <div v-for="d in detailDocs" :key="d.id" class="drawer-doc-item">
                <div class="file-icon-sm" :class="d.file_type">
                  <svg viewBox="0 0 16 16" fill="none"><rect x="2" y="1" width="12" height="14" rx="1.5" stroke="currentColor" stroke-width="1.2"/><path d="M5 5h6M5 8h6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
                </div>
                <span class="drawer-doc-name">{{ d.original_name }}</span>
                <span class="drawer-doc-status" :class="d.status">{{ statusLabel(d.status) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== Toast ===== -->
    <div v-if="toast" :class="['toast', toast.type]">{{ toast.message }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { kbAPI, docAPI } from '../api/knowledge'

const searchQuery = ref('')
const kbList = ref([])
const loading = ref(true)

// 表单
const showModal = ref(false)
const editingKB = ref(null)
const form = ref({ name: '', description: '', department: '', color: '' })
const submitting = ref(false)
const modalError = ref('')

// 删除
const showDelete = ref(null)

// 详情
const showDetail = ref(null)
const detailDocs = ref([])

// Toast
const toast = ref(null)
const showToast = (message, type = 'success') => {
  toast.value = { message, type }
  setTimeout(() => { toast.value = null }, 2500)
}

// 颜色选项
const colors = [
  'linear-gradient(135deg, #4a8cf7, #00d4ff)',
  'linear-gradient(135deg, #8b5cf6, #a78bfa)',
  'linear-gradient(135deg, #22c55e, #4ade80)',
  'linear-gradient(135deg, #f59e0b, #fbbf24)',
  'linear-gradient(135deg, #ef4444, #f87171)',
  'linear-gradient(135deg, #06b6d4, #22d3ee)',
  'linear-gradient(135deg, #ec4899, #f472b6)',
  'linear-gradient(135deg, #6366f1, #818cf8)',
]

// ===== 加载数据 =====
const fetchList = async () => {
  loading.value = true
  try {
    const { data } = await kbAPI.list()
    kbList.value = data.map(kb => ({
      ...kb,
      docCount: kb.doc_count,
      chunkCount: kb.chunk_count,
      size: formatSize(kb.total_size),
      updatedAt: timeAgo(kb.updated_at),
    }))
  } catch (e) {
    showToast('知识库列表加载失败', 'error')
  } finally {
    loading.value = false
  }
}

// ===== 创建/编辑 =====
const openCreate = () => {
  editingKB.value = null
  form.value = { name: '', description: '', department: '', color: colors[0] }
  modalError.value = ''
  showModal.value = true
}

const openEdit = (kb) => {
  editingKB.value = kb
  form.value = { name: kb.name, description: kb.description, department: kb.department, color: kb.color }
  modalError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingKB.value = null
}

const saveKB = async () => {
  if (!form.value.name.trim()) { modalError.value = '请输入知识库名称'; return }
  submitting.value = true
  modalError.value = ''
  try {
    if (editingKB.value) {
      await kbAPI.update(editingKB.value.id, {
        name: form.value.name, description: form.value.description,
        department: form.value.department, color: form.value.color,
      })
      showToast('知识库已更新')
    } else {
      await kbAPI.create({
        name: form.value.name, description: form.value.description,
        department: form.value.department, color: form.value.color,
      })
      showToast('知识库创建成功')
    }
    closeModal()
    await fetchList()
  } catch (e) {
    const detail = e.response?.data?.detail
    if (Array.isArray(detail)) {
      modalError.value = detail.map(d => d.msg).join('; ')
    } else {
      modalError.value = detail || '保存失败'
    }
  } finally {
    submitting.value = false
  }
}

// ===== 删除 =====
const confirmDelete = (kb) => { showDelete.value = kb }
const doDelete = async () => {
  try {
    await kbAPI.remove(showDelete.value.id)
    showToast(`「${showDelete.value.name}」已删除`)
    showDelete.value = null
    await fetchList()
  } catch (e) {
    showToast('删除失败: ' + (e.response?.data?.detail || e.message), 'error')
  }
}

// ===== 详情抽屉 =====
const openDetail = async (kb) => {
  showDetail.value = kb
  detailDocs.value = []
  try {
    const { data } = await docAPI.list({ kb_id: kb.id })
    detailDocs.value = data.slice(0, 10)
  } catch (e) { /* ignore */ }
}

// ===== 搜索 =====
const filteredList = computed(() => {
  if (!searchQuery.value) return kbList.value
  const q = searchQuery.value.toLowerCase()
  return kbList.value.filter(k => k.name.toLowerCase().includes(q) || k.description.toLowerCase().includes(q))
})

// ===== 工具函数 =====
const formatSize = (bytes) => {
  if (bytes >= 1e9) return (bytes / 1e9).toFixed(1) + ' GB'
  if (bytes >= 1e6) return (bytes / 1e6).toFixed(0) + ' MB'
  if (bytes >= 1e3) return (bytes / 1e3).toFixed(0) + ' KB'
  return bytes + ' B'
}

const timeAgo = (dateStr) => {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return mins + ' 分钟前'
  const hours = Math.floor(mins / 60)
  if (hours < 24) return hours + ' 小时前'
  return Math.floor(hours / 24) + ' 天前'
}

const statusLabel = (s) => ({ done: '已完成', processing: '索引中', uploading: '上传中', failed: '失败' }[s] || s)

onMounted(fetchList)
</script>

<style scoped>
.page { padding: 24px; }

/* ===== 顶栏 ===== */
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.toolbar-left { display: flex; align-items: baseline; gap: 10px; }
.toolbar-right { display: flex; align-items: center; gap: 10px; }
.page-title { font-size: 18px; font-weight: 700; color: #f0f4ff; margin: 0; }
.page-count { font-size: 13px; color: rgba(255,255,255,.35); }
.search-box { position: relative; }
.search-box-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); width: 16px; height: 16px; color: rgba(255,255,255,.25); pointer-events: none; }
.search-box-input { width: 240px; height: 36px; padding: 0 16px 0 36px; font-size: 13px; color: #e2e8f0; background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.08); border-radius: 8px; outline: none; font-family: inherit; transition: border-color .2s; }
.search-box-input::placeholder { color: rgba(255,255,255,.2); }
.search-box-input:focus { border-color: rgba(74,140,247,.4); }

/* ===== 按钮系统 ===== */
.btn { display: inline-flex; align-items: center; gap: 6px; height: 36px; padding: 0 16px; border-radius: 8px; font-size: 13px; font-weight: 500; cursor: pointer; transition: all .2s; font-family: inherit; border: 1px solid transparent; }
.btn svg { width: 16px; height: 16px; flex-shrink: 0; }
.btn-primary { background: linear-gradient(135deg,#4a6cf7,#5b8cf7); color: #fff; }
.btn-primary:hover:not(:disabled) { opacity: .9; }
.btn-primary:disabled { opacity: .4; cursor: not-allowed; }
.btn-ghost { background: rgba(255,255,255,.04); color: rgba(255,255,255,.6); border-color: rgba(255,255,255,.08); }
.btn-ghost:hover { background: rgba(255,255,255,.08); }
.btn-danger { background: rgba(239,68,68,.1); color: #f87171; border-color: rgba(239,68,68,.2); }
.btn-danger:hover { background: rgba(239,68,68,.2); }

/* ===== 卡片网格 ===== */
.kb-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }

.kb-card { background: rgba(255,255,255,.02); border: 1px solid rgba(255,255,255,.05); border-radius: 14px; overflow: hidden; transition: all .25s; cursor: pointer; }
.kb-card:hover { background: rgba(255,255,255,.04); border-color: rgba(255,255,255,.1); transform: translateY(-3px); box-shadow: 0 12px 32px rgba(0,0,0,.35); }
.kb-color-strip { height: 3px; }
.kb-card-body { padding: 18px 20px 20px; }
.kb-card-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.kb-avatar { width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.kb-avatar svg { width: 22px; height: 22px; color: #fff; }
.kb-card-actions { display: flex; gap: 2px; opacity: 0; transition: opacity .2s; }
.kb-card:hover .kb-card-actions { opacity: 1; }
.act-icon { width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,.04); border: none; border-radius: 6px; color: rgba(255,255,255,.35); cursor: pointer; transition: all .15s; }
.act-icon:hover { background: rgba(255,255,255,.1); color: rgba(255,255,255,.7); }
.act-icon.danger:hover { background: rgba(239,68,68,.15); color: #f87171; }
.act-icon svg { width: 14px; height: 14px; }

.kb-name { font-size: 15px; font-weight: 600; color: #e2e8f0; margin: 0 0 5px; }
.kb-desc { font-size: 12.5px; color: rgba(255,255,255,.35); line-height: 1.5; margin: 0 0 14px; min-height: 18px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

/* 统计行 */
.kb-stats { display: flex; gap: 0; border-top: 1px solid rgba(255,255,255,.04); padding-top: 12px; }
.kb-stat { flex: 1; display: flex; align-items: center; gap: 4px; font-size: 12.5px; color: rgba(255,255,255,.35); }
.kb-stat-icon { width: 14px; height: 14px; color: rgba(255,255,255,.2); flex-shrink: 0; }
.kb-stat-val { font-weight: 600; color: rgba(255,255,255,.55); }

/* ===== 骨架屏 ===== */
.kb-card.skeleton { pointer-events: none; padding: 20px; }
.skel-line { height: 14px; border-radius: 6px; background: rgba(255,255,255,.04); animation: skelPulse 1.5s ease-in-out infinite; }
.skel-line.w60 { width: 60%; }
.skel-line.w80 { width: 80%; }
.skel-line.w40 { width: 40%; }
.skel-line.mt8 { margin-top: 8px; }
.skel-line.mt12 { margin-top: 12px; }
@keyframes skelPulse { 0%,100%{opacity:.4} 50%{opacity:.8} }

/* ===== 空状态 ===== */
.empty-full { grid-column: 1/-1; display: flex; flex-direction: column; align-items: center; padding: 80px 0; text-align: center; }
.empty-full-icon { width: 64px; height: 64px; color: rgba(255,255,255,.08); margin-bottom: 16px; }
.empty-full-title { font-size: 15px; color: rgba(255,255,255,.35); margin: 0 0 6px; }
.empty-full-desc { font-size: 13px; color: rgba(255,255,255,.2); margin: 0 0 20px; }

/* ===== 弹窗 ===== */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.55); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal-card { width: 460px; max-width: 90vw; background: #111a35; border: 1px solid rgba(255,255,255,.08); border-radius: 16px; padding: 28px; }
.modal-sm { width: 400px; text-align: center; }
.modal-title { font-size: 17px; font-weight: 700; color: #e2e8f0; margin: 0 0 20px; }
.modal-title.center { text-align: center; }

.form-group { margin-bottom: 15px; }
.form-label { display: block; font-size: 12.5px; font-weight: 500; color: rgba(255,255,255,.45); margin-bottom: 5px; }
.form-label .required { color: #f87171; }
.form-field { width: 100%; height: 40px; padding: 0 12px; font-size: 13px; color: #e2e8f0; background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08); border-radius: 8px; outline: none; font-family: inherit; transition: border-color .2s; }
.form-field:focus { border-color: rgba(74,140,247,.4); }
.form-textarea { height: auto; padding: 10px 12px; resize: vertical; }
.form-select { appearance: none; cursor: pointer; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.modal-error { font-size: 12.5px; color: #f87171; background: rgba(239,68,68,.08); padding: 8px 12px; border-radius: 8px; margin-bottom: 4px; }

/* 颜色选择器 */
.color-picker { display: flex; gap: 8px; }
.color-dot { width: 28px; height: 28px; border-radius: 8px; border: 2px solid transparent; cursor: pointer; transition: all .15s; padding: 0; }
.color-dot:hover { transform: scale(1.15); }
.color-dot.active { border-color: #fff; box-shadow: 0 0 12px rgba(255,255,255,.2); }

/* ===== 删除确认 ===== */
.delete-icon-wrap { width: 48px; height: 48px; margin: 0 auto 12px; color: #f87171; }
.delete-icon-wrap svg { width: 100%; height: 100%; }
.delete-text { font-size: 13px; color: rgba(255,255,255,.45); line-height: 1.7; margin: 0 0 8px; }
.delete-text strong { color: rgba(255,255,255,.7); }

/* ===== 详情抽屉 ===== */
.drawer-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.4); z-index: 100; display: flex; justify-content: flex-end; }
.drawer { width: 440px; max-width: 90vw; height: 100%; background: #0d1538; border-left: 1px solid rgba(255,255,255,.06); display: flex; flex-direction: column; animation: slideIn .25s ease; }
@keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
.drawer-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid rgba(255,255,255,.05); flex-shrink: 0; }
.drawer-header-left { display: flex; align-items: center; gap: 12px; }
.drawer-avatar { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.drawer-avatar svg { width: 22px; height: 22px; color: #fff; }
.drawer-title { font-size: 15px; font-weight: 700; color: #e2e8f0; margin: 0; }
.drawer-subtitle { font-size: 12px; color: rgba(255,255,255,.3); margin: 2px 0 0; }
.drawer-close { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: none; border: none; color: rgba(255,255,255,.3); font-size: 24px; cursor: pointer; border-radius: 6px; }
.drawer-close:hover { background: rgba(255,255,255,.05); color: rgba(255,255,255,.6); }
.drawer-body { flex: 1; overflow-y: auto; padding: 20px 24px; }
.drawer-body::-webkit-scrollbar { width: 3px; }
.drawer-body::-webkit-scrollbar-thumb { background: rgba(255,255,255,.06); border-radius: 2px; }
.drawer-desc { font-size: 13px; color: rgba(255,255,255,.4); line-height: 1.6; margin: 0 0 20px; }
.drawer-stats-row { display: flex; gap: 0; background: rgba(255,255,255,.025); border-radius: 10px; padding: 16px 0; margin-bottom: 24px; }
.drawer-stat { flex: 1; text-align: center; }
.drawer-stat-val { display: block; font-size: 20px; font-weight: 700; color: #e2e8f0; }
.drawer-stat-lbl { display: block; font-size: 11px; color: rgba(255,255,255,.3); margin-top: 3px; }
.drawer-section-title { font-size: 13px; font-weight: 600; color: rgba(255,255,255,.4); margin: 0 0 10px; }
.drawer-empty { font-size: 12px; color: rgba(255,255,255,.2); padding: 16px 0; }
.drawer-doc-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,.03); }
.drawer-doc-name { flex: 1; font-size: 12.5px; color: rgba(255,255,255,.5); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.drawer-doc-status { font-size: 11px; padding: 2px 8px; border-radius: 10px; flex-shrink: 0; }
.drawer-doc-status.done { color: #4ade80; background: rgba(34,197,94,.08); }
.drawer-doc-status.processing { color: #fbbf24; background: rgba(245,158,11,.08); }
.drawer-doc-status.failed { color: #f87171; background: rgba(239,68,68,.08); }
.file-icon-sm { width: 26px; height: 26px; border-radius: 5px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.file-icon-sm svg { width: 14px; height: 14px; }
.file-icon-sm.pdf { background: rgba(239,68,68,.1); color: #f87171; }
.file-icon-sm.docx, .file-icon-sm.doc { background: rgba(74,140,247,.1); color: #4a8cf7; }
.file-icon-sm.md { background: rgba(139,92,246,.1); color: #a78bfa; }
.file-icon-sm.pptx, .file-icon-sm.ppt { background: rgba(245,158,11,.1); color: #fbbf24; }
.file-icon-sm.txt { background: rgba(34,197,94,.1); color: #4ade80; }

/* ===== Toast ===== */
.toast { position: fixed; top: 20px; right: 20px; z-index: 200; padding: 12px 20px; border-radius: 10px; font-size: 13px; font-weight: 500; backdrop-filter: blur(12px); box-shadow: 0 8px 32px rgba(0,0,0,.4); animation: toastIn .3s ease; }
.toast.success { background: rgba(34,197,94,.15); border: 1px solid rgba(34,197,94,.25); color: #4ade80; }
.toast.error { background: rgba(239,68,68,.15); border: 1px solid rgba(239,68,68,.25); color: #f87171; }
@keyframes toastIn { from { opacity: 0; transform: translateX(40px); } to { opacity: 1; transform: translateX(0); } }

@media (max-width: 1400px) { .kb-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 900px) { .kb-grid { grid-template-columns: 1fr; } .drawer { width: 100%; } }
</style>
