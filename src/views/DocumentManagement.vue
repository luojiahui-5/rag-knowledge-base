<template>
  <div class="page">
    <!-- ===== 顶部工具栏 ===== -->
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">文档管理</h2>
        <span class="page-count">{{ totalDocs }} 个文档</span>
      </div>
      <div class="toolbar-right">
        <button v-if="selectedIds.length" class="btn btn-ghost" @click="clearSelection">取消选择({{ selectedIds.length }})</button>
        <button v-if="selectedIds.length" class="btn btn-danger" @click="batchDelete">批量删除</button>
        <button class="btn btn-primary" @click="showUpload = true">
          <svg viewBox="0 0 20 20" fill="none"><path d="M10 3v10M6 7l4-4 4 4M4 13v2a2 2 0 002 2h8a2 2 0 002-2v-2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
          上传文档
        </button>
      </div>
    </div>

    <!-- ===== 搜索 + 筛选 ===== -->
    <div class="filter-bar">
      <div class="search-box">
        <svg viewBox="0 0 20 20" fill="none" class="search-box-icon"><circle cx="9" cy="9" r="6" stroke="currentColor" stroke-width="1.5"/><path d="M14 14l3.5 3.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
        <input v-model="searchQuery" class="search-box-input" placeholder="搜索文档名称、类型..." @input="onSearchInput" />
        <svg v-if="searchQuery" class="search-clear" @click="searchQuery=''" viewBox="0 0 16 16" fill="none"><path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
      </div>
      <div class="filter-chips">
        <button v-for="kb in kbList.slice(0,5)" :key="kb.id" :class="['chip', { active: kbFilter === kb.id }]" @click="kbFilter = kbFilter === kb.id ? null : kb.id">{{ kb.name }}</button>
        <button :class="['chip', { active: kbFilter === null }]" @click="kbFilter = null">全部</button>
      </div>
      <div class="filter-right">
        <select v-model="typeFilter" class="select-sm">
          <option value="">全部类型</option>
          <option value="pdf">PDF</option>
          <option value="docx">Word</option>
          <option value="md">Markdown</option>
          <option value="pptx">PPT</option>
          <option value="txt">TXT</option>
        </select>
        <select v-model="statusFilter" class="select-sm">
          <option value="">全部状态</option>
          <option value="done">已完成</option>
          <option value="processing">处理中</option>
          <option value="failed">失败</option>
        </select>
        <button class="btn btn-ghost btn-sm" @click="refreshDocs">
          <svg viewBox="0 0 16 16" fill="none" :class="{ spinning: refreshing }"><path d="M2 8a6 6 0 0111.3-2.5M14 8a6 6 0 01-11.3 2.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M14 4v2h-2M2 12v-2h2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
      </div>
    </div>

    <!-- ===== 表格 ===== -->
    <div class="table-card">
      <table class="doc-table">
        <thead>
          <tr>
            <th class="th-check"><input type="checkbox" :checked="allSelected" :indeterminate="someSelected" @change="toggleAll" /></th>
            <th class="th-name">文档名称</th>
            <th class="th-kb">所属知识库</th>
            <th class="th-type">类型</th>
            <th class="th-size">大小</th>
            <th class="th-chunks">切片</th>
            <th class="th-status">状态</th>
            <th class="th-time">上传时间</th>
            <th class="th-actions">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="displayDocs.length === 0">
            <td colspan="9" class="empty-row">
              <div class="empty-state">
                <svg viewBox="0 0 48 48" fill="none" class="empty-img"><rect x="10" y="4" width="28" height="36" rx="3" stroke="currentColor" stroke-width="2"/><path d="M18 16h12M18 22h8M18 28h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
                <p class="empty-text">暂无文档</p>
                <p class="empty-hint">点击"上传文档"添加第一批内容</p>
              </div>
            </td>
          </tr>
          <tr v-for="doc in displayDocs" :key="doc.id" :class="{ selected: selectedIds.includes(doc.id) }" @click="toggleSelect(doc.id)">
            <td class="td-check" @click.stop>
              <input type="checkbox" :checked="selectedIds.includes(doc.id)" @change="toggleSelect(doc.id)" />
            </td>
            <td class="td-name">
              <div class="file-cell">
                <div class="file-icon" :class="doc.type">
                  <template v-if="doc.type === 'pdf'">
                    <svg viewBox="0 0 24 24" fill="none"><path d="M6 2h10l5 5v14a1 1 0 01-1 1H6a1 1 0 01-1-1V3a1 1 0 011-1z" stroke="currentColor" stroke-width="1.5"/><path d="M14 2v6h6" stroke="currentColor" stroke-width="1.5"/><path d="M8 13h8M8 17h5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                  </template>
                  <template v-else-if="doc.type === 'docx' || doc.type === 'doc'">
                    <svg viewBox="0 0 24 24" fill="none"><rect x="4" y="2" width="16" height="20" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M8 8h8M8 12h8M8 16h5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                  </template>
                  <template v-else-if="doc.type === 'md'">
                    <svg viewBox="0 0 24 24" fill="none"><rect x="4" y="2" width="16" height="20" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M8 7h5M8 11h8M8 15h3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                  </template>
                  <template v-else-if="doc.type === 'pptx' || doc.type === 'ppt'">
                    <svg viewBox="0 0 24 24" fill="none"><rect x="3" y="5" width="18" height="14" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M8 10l3 4 2-2 3 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  </template>
                  <template v-else>
                    <svg viewBox="0 0 24 24" fill="none"><rect x="4" y="2" width="16" height="20" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M8 8h8M8 12h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                  </template>
                </div>
                <div class="file-info">
                  <span class="file-name">{{ doc.name }}</span>
                  <span class="file-meta">{{ doc.type.toUpperCase() }} · {{ doc.size }}</span>
                </div>
              </div>
            </td>
            <td class="td-kb">{{ doc.knowledgeBase }}</td>
            <td class="td-type"><span class="type-badge">{{ doc.type.toUpperCase() }}</span></td>
            <td class="td-size">{{ doc.size }}</td>
            <td class="td-chunks">{{ doc.chunks || 0 }}</td>
            <td class="td-status">
              <span class="status-badge" :class="doc.status">
                <span class="status-dot"></span>
                {{ doc.statusText }}
              </span>
            </td>
            <td class="td-time">{{ doc.uploadTime }}</td>
            <td class="td-actions">
              <div class="action-btns">
                <button class="act-btn" title="预览内容" @click.stop="previewDoc(doc)">
                  <svg viewBox="0 0 16 16" fill="none"><path d="M2 8s2.5-5 6-5 6 5 6 5-2.5 5-6 5-6-5-6-5z" stroke="currentColor" stroke-width="1.3"/><circle cx="8" cy="8" r="2" stroke="currentColor" stroke-width="1.3"/></svg>
                </button>
                <button class="act-btn" title="下载" @click.stop="downloadDoc(doc)">
                  <svg viewBox="0 0 16 16" fill="none"><path d="M3 11v2a1 1 0 001 1h8a1 1 0 001-1v-2M8 3v8M5 7l3 3 3-3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </button>
                <button class="act-btn danger" title="删除" @click.stop="deleteDoc(doc)">
                  <svg viewBox="0 0 16 16" fill="none"><path d="M3 4h10M6 4V2h4v2M5 4v9a1 1 0 001 1h4a1 1 0 001-1V4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ===== 分页 ===== -->
    <div class="pagination-bar">
      <span class="paginate-info">{{ startRow }}-{{ endRow }} / 共 {{ totalDocs }} 条</span>
      <div class="paginate-btns">
        <button class="paginate-btn prev" :disabled="currentPage <= 1" @click="currentPage--">
          <svg viewBox="0 0 16 16" fill="none"><path d="M10 4l-4 4 4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          上一页
        </button>
        <button v-for="p in pageNumbers" :key="p" :class="['paginate-btn page', { active: p === currentPage }]" @click="currentPage = p">{{ p }}</button>
        <button class="paginate-btn next" :disabled="currentPage >= totalPages" @click="currentPage++">
          下一页
          <svg viewBox="0 0 16 16" fill="none"><path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
      </div>
    </div>

    <!-- ===== 上传弹窗 ===== -->
    <div v-if="showUpload" class="modal-overlay" @click.self="showUpload = false">
      <div class="modal-card modal-upload">
        <h3 class="modal-title">上传文档</h3>

        <!-- 拖拽上传区 -->
        <div class="drop-zone" :class="{ dragover: dragOver, hasFiles: uploadFiles.length }"
          @dragover.prevent="dragOver = true"
          @dragleave="dragOver = false"
          @drop.prevent="handleDrop"
          @click="$refs.fileInput.click()"
        >
          <input ref="fileInput" type="file" multiple style="display:none" @change="handleFileSelect"
            accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.md,.txt,.html" />
          <svg viewBox="0 0 48 48" fill="none" class="drop-icon"><path d="M24 10v20M14 20l10-10 10 10M10 30v3a4 4 0 004 4h20a4 4 0 004-4v-3" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
          <p class="drop-text" v-if="uploadFiles.length === 0">拖拽文件到此处，或点击选择</p>
          <div v-else class="drop-file-list">
            <div v-for="(f, i) in uploadFiles" :key="i" class="drop-file-item">
              <span class="drop-file-name">{{ f.name }}</span>
              <span class="drop-file-size">{{ formatSize(f.size) }}</span>
              <button class="drop-file-remove" @click.stop="uploadFiles.splice(i,1)">&times;</button>
            </div>
          </div>
          <p class="drop-hint">支持 PDF、Word、PPT、Excel、Markdown、TXT · 单文件最大 100MB</p>
        </div>

        <div class="form-group">
          <label class="form-label">目标知识库</label>
          <select v-model="uploadKbId" class="form-field form-select">
            <option value="" disabled v-if="!kbList.length">加载知识库中...</option>
            <option v-for="kb in kbList" :key="kb.id" :value="kb.id">{{ kb.name }}</option>
          </select>
        </div>

        <div v-if="uploadProgress > 0 && uploadProgress < 100" class="upload-progress-bar">
          <div class="upload-progress-fill" :style="{ width: uploadProgress + '%' }"></div>
        </div>

        <!-- 上传结果通知 -->
        <div v-if="uploadResult" :class="['upload-result', uploadResult.type]">
          <div class="upload-result-icon">
            <svg v-if="uploadResult.type === 'success'" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="1.5"/><path d="M6 10l3 3 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <svg v-else-if="uploadResult.type === 'error'" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="1.5"/><path d="M7 7l6 6M13 7l-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
            <svg v-else viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="1.5"/><path d="M10 6v4M10 14h0" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          </div>
          <div class="upload-result-body">
            <p class="upload-result-title">{{ uploadResult.title }}</p>
            <p v-if="uploadResult.detail" class="upload-result-detail">{{ uploadResult.detail }}</p>
          </div>
          <button v-if="uploadResult.type !== 'success'" class="upload-result-close" @click="uploadResult = null">&times;</button>
        </div>

        <div class="modal-actions">
          <button class="btn btn-ghost" @click="showUpload = false; uploadFiles = []; uploadProgress = 0; uploadResult = null">取消</button>
          <button v-if="!uploadResult || uploadResult.type === 'error'" class="btn btn-primary" :disabled="uploadFiles.length === 0 || !uploadKbId" @click="doUpload">上传 {{ uploadFiles.length }} 个文件</button>
          <button v-else-if="uploadResult.type === 'success'" class="btn btn-primary" @click="showUpload = false; uploadProgress = 0; uploadResult = null">完成</button>
          <button v-else class="btn btn-primary" @click="uploadResult = null; uploadProgress = 0">重新上传</button>
        </div>
      </div>
    </div>

    <!-- ===== 预览弹窗 ===== -->
    <div v-if="showPreview" class="modal-overlay" @click.self="showPreview = false">
      <div class="modal-card modal-preview">
        <div class="preview-header">
          <div class="preview-file-info">
            <div class="file-icon sm" :class="previewDocData?.type">
              <svg viewBox="0 0 24 24" fill="none"><rect x="4" y="2" width="16" height="20" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M8 8h8M8 12h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
            </div>
            <div>
              <h4 class="preview-name">{{ previewDocData?.name }}</h4>
              <span class="preview-meta">{{ previewDocData?.knowledgeBase }} · 切片数 {{ previewDocData?.chunks || 0 }}</span>
            </div>
          </div>
          <button class="modal-close-btn" @click="showPreview = false">&times;</button>
        </div>
        <div class="preview-body">
          <pre class="preview-content">{{ previewContent }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { docAPI, kbAPI } from '../api/knowledge'

// ===== 状态 =====
const searchQuery = ref('')
const kbFilter = ref(null)
const typeFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const docs = ref([])
const kbList = ref([])
const selectedIds = ref([])
const refreshing = ref(false)

// 上传
const showUpload = ref(false)
const uploadFiles = ref([])
const uploadKbId = ref(null)
const uploadProgress = ref(0)
const dragOver = ref(false)

// 预览
const showPreview = ref(false)
const previewDocData = ref(null)
const previewContent = ref('')

// 搜索防抖
let searchTimer = null
const onSearchInput = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { currentPage.value = 1 }, 300)
}

// ===== 计算属性 =====
const filteredDocs = computed(() => {
  let result = docs.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(d => d.name.toLowerCase().includes(q) || d.type.toLowerCase().includes(q))
  }
  if (kbFilter.value) result = result.filter(d => d.kb_id === kbFilter.value)
  if (typeFilter.value) result = result.filter(d => d.type === typeFilter.value)
  if (statusFilter.value) result = result.filter(d => d.status === statusFilter.value)
  return result
})

const totalDocs = computed(() => filteredDocs.value.length)
const totalPages = computed(() => Math.max(1, Math.ceil(totalDocs.value / pageSize.value)))
const pageNumbers = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const displayDocs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredDocs.value.slice(start, start + pageSize.value)
})

const startRow = computed(() => totalDocs.value === 0 ? 0 : (currentPage.value - 1) * pageSize.value + 1)
const endRow = computed(() => Math.min(currentPage.value * pageSize.value, totalDocs.value))

const allSelected = computed(() => displayDocs.value.length > 0 && displayDocs.value.every(d => selectedIds.value.includes(d.id)))
const someSelected = computed(() => !allSelected.value && displayDocs.value.some(d => selectedIds.value.includes(d.id)))

// ===== 数据加载 =====
const fetchDocs = async () => {
  try {
    const params = {}
    if (statusFilter.value) params.status = statusFilter.value
    if (typeFilter.value) params.file_type = typeFilter.value
    const { data } = await docAPI.list(params)
    docs.value = data.map(d => ({
      ...d,
      name: d.original_name,
      knowledgeBase: kbList.value.find(k => k.id === d.kb_id)?.name || '未知知识库',
      type: d.file_type,
      size: formatSize(d.file_size),
      chunks: d.chunk_count,
      statusText: statusLabel(d.status),
      uploadTime: d.created_at ? fmtTime(d.created_at) : '',
    }))
  } catch (e) {
    console.warn('文档列表加载失败', e)
  }
}

const refreshDocs = async () => {
  refreshing.value = true
  await fetchKBs()
  await fetchDocs()
  setTimeout(() => { refreshing.value = false }, 500)
}

const fetchKBs = async () => {
  try {
    const { data } = await kbAPI.list()
    kbList.value = data
    if (!uploadKbId.value && data.length) uploadKbId.value = data[0].id
  } catch (e) {
    console.warn('知识库列表加载失败，使用本地缓存', e)
    // 如果 API 失败，用当前文档所属知识库作为上传目标
    if (!uploadKbId.value && docs.value.length) {
      uploadKbId.value = docs.value[0].kb_id
    }
  }
}

// ===== 操作 =====
const toggleAll = () => {
  if (allSelected.value) selectedIds.value = []
  else selectedIds.value = displayDocs.value.map(d => d.id)
}

const toggleSelect = (id) => {
  const idx = selectedIds.value.indexOf(id)
  if (idx >= 0) selectedIds.value.splice(idx, 1)
  else selectedIds.value.push(id)
}

const clearSelection = () => { selectedIds.value = [] }

const deleteDoc = async (doc) => {
  if (!confirm(`确定删除「${doc.name}」？此操作不可撤销。`)) return
  try {
    await docAPI.remove(doc.id)
    selectedIds.value = selectedIds.value.filter(id => id !== doc.id)
    await fetchDocs()
  } catch (e) {
    alert('删除失败: ' + (e.response?.data?.detail || e.message))
  }
}

const batchDelete = async () => {
  if (!confirm(`确定删除选中的 ${selectedIds.value.length} 个文档？此操作不可撤销。`)) return
  try {
    await Promise.all(selectedIds.value.map(id => docAPI.remove(id)))
    selectedIds.value = []
    await fetchDocs()
  } catch (e) {
    alert('批量删除失败: ' + (e.response?.data?.detail || e.message))
  }
}

const downloadDoc = async (doc) => {
  try {
    const token = sessionStorage.getItem('token')
    const resp = await fetch(`/api/v1/documents/${doc.id}/download`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!resp.ok) throw new Error('下载失败')
    const blob = await resp.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = doc.name || 'download'
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    alert('下载失败: ' + e.message)
  }
}

const previewDoc = async (doc) => {
  previewDocData.value = doc
  showPreview.value = true
  previewContent.value = '加载中...'
  try {
    const token = sessionStorage.getItem('token')
    const resp = await fetch(`/api/v1/documents/${doc.id}/preview`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (resp.ok) {
      const data = await resp.json()
      const text = data.content
      previewContent.value = text.slice(0, 8000) + (text.length > 8000 ? '\n\n... 内容过长，已截断前 8000 字' : '')
    } else {
      const err = await resp.json().catch(() => ({}))
      previewContent.value = `[预览不可用: ${err.detail || resp.statusText}]`
    }
  } catch {
    previewContent.value = '[预览加载失败]'
  }
}

// ===== 上传 =====
const handleDrop = (e) => {
  dragOver.value = false
  const files = Array.from(e.dataTransfer.files)
  uploadFiles.value.push(...files)
}

const handleFileSelect = (e) => {
  const files = Array.from(e.target.files || [])
  uploadFiles.value.push(...files)
}

const uploadResult = ref(null) // { type: 'success'|'partial'|'error', title: '', detail: '' }

const doUpload = async () => {
  uploadProgress.value = 5
  uploadResult.value = null
  let success = 0
  const errors = []

  for (let i = 0; i < uploadFiles.value.length; i++) {
    const file = uploadFiles.value[i]
    try {
      await docAPI.upload(uploadKbId.value, file)
      success++
    } catch (e) {
      const detail = e.response?.data?.detail || e.message || '未知错误'
      errors.push(`${file.name}: ${detail}`)
    }
    uploadProgress.value = 5 + Math.round(((i + 1) / uploadFiles.value.length) * 90)
  }

  uploadProgress.value = 100
  uploadFiles.value = []

  const fail = errors.length
  if (fail > 0 && success === 0) {
    uploadResult.value = { type: 'error', title: '上传失败', detail: errors.join('\n') }
  } else if (fail > 0) {
    uploadResult.value = { type: 'partial', title: `部分成功`, detail: `${success} 个成功，${fail} 个失败\n\n${errors.join('\n')}` }
  } else {
    uploadResult.value = { type: 'success', title: '上传完成', detail: `成功上传 ${success} 个文件` }
    setTimeout(() => { showUpload.value = false; uploadProgress.value = 0; uploadResult.value = null }, 1500)
  }
  await fetchDocs()
}

// ===== 工具函数 =====
const formatSize = (bytes) => {
  if (bytes >= 1e9) return (bytes / 1e9).toFixed(1) + ' GB'
  if (bytes >= 1e6) return (bytes / 1e6).toFixed(0) + ' MB'
  if (bytes >= 1e3) return (bytes / 1e3).toFixed(0) + ' KB'
  return bytes + ' B'
}

const fmtTime = (dateStr) => {
  const d = new Date(dateStr)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const statusLabel = (s) => {
  const map = { done: '已完成', processing: '索引中', uploading: '上传中', parsing: '解析中', embedding: '向量化中', failed: '失败' }
  return map[s] || s
}

onMounted(() => { fetchKBs(); fetchDocs() })
</script>

<style scoped>
.page { padding: 24px; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.toolbar-left { display: flex; align-items: baseline; gap: 10px; }
.toolbar-right { display: flex; align-items: center; gap: 8px; }
.page-title { font-size: 18px; font-weight: 700; color: #f0f4ff; margin: 0; }
.page-count { font-size: 13px; color: rgba(255,255,255,.35); }

/* ===== 按钮系统 ===== */
.btn { display: inline-flex; align-items: center; gap: 6px; height: 34px; padding: 0 14px; border: 1px solid transparent; border-radius: 8px; font-size: 13px; font-weight: 500; cursor: pointer; transition: all .2s; font-family: inherit; white-space: nowrap; }
.btn svg { width: 16px; height: 16px; flex-shrink: 0; }
.btn-primary { background: linear-gradient(135deg,#4a6cf7,#5b8cf7); color: #fff; border-color: transparent; }
.btn-primary:hover:not(:disabled) { opacity: .9; }
.btn-primary:disabled { opacity: .4; cursor: not-allowed; }
.btn-ghost { background: rgba(255,255,255,.04); color: rgba(255,255,255,.6); border-color: rgba(255,255,255,.08); }
.btn-ghost:hover { background: rgba(255,255,255,.08); color: rgba(255,255,255,.8); }
.btn-danger { background: rgba(239,68,68,.08); color: #f87171; border-color: rgba(239,68,68,.15); }
.btn-danger:hover { background: rgba(239,68,68,.15); }
.btn-sm { height: 30px; padding: 0 10px; font-size: 12px; }
.btn-sm svg { width: 14px; height: 14px; }
.spinning { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ===== 筛选栏 ===== */
.filter-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; flex-wrap: wrap; }
.search-box { position: relative; width: 280px; }
.search-box-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); width: 16px; height: 16px; color: rgba(255,255,255,.25); pointer-events: none; }
.search-box-input { width: 100%; height: 36px; padding: 0 32px; font-size: 13px; color: #e2e8f0; background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.08); border-radius: 8px; outline: none; font-family: inherit; transition: border-color .2s; }
.search-box-input:focus { border-color: rgba(74,140,247,.4); }
.search-box-input::placeholder { color: rgba(255,255,255,.2); }
.search-clear { position: absolute; right: 8px; top: 50%; transform: translateY(-50%); width: 16px; height: 16px; color: rgba(255,255,255,.3); cursor: pointer; }
.filter-chips { display: flex; gap: 6px; flex: 1; overflow-x: auto; }
.filter-chips::-webkit-scrollbar { height: 0; }
.chip { padding: 5px 12px; border-radius: 16px; font-size: 12px; color: rgba(255,255,255,.4); background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.05); cursor: pointer; transition: all .2s; font-family: inherit; white-space: nowrap; }
.chip:hover { color: rgba(255,255,255,.7); background: rgba(255,255,255,.06); }
.chip.active { color: #8bb8ff; background: rgba(74,140,247,.12); border-color: rgba(74,140,247,.2); }
.filter-right { display: flex; gap: 8px; align-items: center; flex-shrink: 0; }
.select-sm { height: 34px; padding: 0 10px; font-size: 12px; color: rgba(255,255,255,.5); background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08); border-radius: 8px; outline: none; cursor: pointer; font-family: inherit; }

/* ===== 表格卡片 ===== */
.table-card { background: rgba(255,255,255,.015); border: 1px solid rgba(255,255,255,.05); border-radius: 12px; overflow: hidden; }
.doc-table { width: 100%; border-collapse: collapse; }
.doc-table th { padding: 11px 14px; font-size: 11.5px; font-weight: 600; color: rgba(255,255,255,.3); text-align: left; border-bottom: 1px solid rgba(255,255,255,.04); text-transform: uppercase; letter-spacing: .5px; white-space: nowrap; background: rgba(255,255,255,.01); }
.doc-table td { padding: 11px 14px; font-size: 13px; color: rgba(255,255,255,.55); border-bottom: 1px solid rgba(255,255,255,.025); white-space: nowrap; }

.doc-table tbody tr { transition: background .15s; cursor: pointer; }
.doc-table tbody tr:hover { background: rgba(255,255,255,.02); }
.doc-table tbody tr.selected { background: rgba(74,140,247,.05); }

.th-check, .td-check { width: 36px; text-align: center; }
.th-check input, .td-check input { accent-color: #4a8cf7; cursor: pointer; width: 14px; height: 14px; }
.th-name { min-width: 240px; }
.th-kb { width: 130px; }
.th-type { width: 70px; }
.th-size { width: 80px; }
.th-chunks { width: 60px; }
.th-status { width: 90px; }
.th-time { width: 140px; }
.th-actions { width: 110px; }

/* ===== 文件单元格 ===== */
.file-cell { display: flex; align-items: center; gap: 10px; }
.file-icon { width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.file-icon svg { width: 18px; height: 18px; }
.file-icon.pdf { background: rgba(239,68,68,.1); color: #f87171; }
.file-icon.docx, .file-icon.doc { background: rgba(74,140,247,.1); color: #4a8cf7; }
.file-icon.md { background: rgba(139,92,246,.1); color: #a78bfa; }
.file-icon.pptx, .file-icon.ppt { background: rgba(245,158,11,.1); color: #fbbf24; }
.file-icon.txt { background: rgba(34,197,94,.1); color: #4ade80; }
.file-info { min-width: 0; }
.file-name { display: block; font-size: 13px; color: rgba(255,255,255,.75); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 300px; }
.file-meta { display: block; font-size: 11px; color: rgba(255,255,255,.25); margin-top: 1px; }

/* ===== 类型/状态徽标 ===== */
.type-badge { font-size: 11px; padding: 2px 8px; border-radius: 4px; background: rgba(255,255,255,.04); color: rgba(255,255,255,.35); font-weight: 500; letter-spacing: .3px; }
.status-badge { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 500; padding: 4px 10px; border-radius: 16px; }
.status-badge.done { color: #4ade80; background: rgba(34,197,94,.08); }
.status-badge.processing, .status-badge.parsing, .status-badge.embedding, .status-badge.uploading { color: #fbbf24; background: rgba(245,158,11,.08); }
.status-badge.failed { color: #f87171; background: rgba(239,68,68,.08); }
.status-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.status-badge.done .status-dot { background: #4ade80; box-shadow: 0 0 6px rgba(34,197,94,.3); }
.status-badge.processing .status-dot,
.status-badge.parsing .status-dot,
.status-badge.embedding .status-dot,
.status-badge.uploading .status-dot { background: #fbbf24; animation: dotPulse 1.5s infinite; }
.status-badge.failed .status-dot { background: #f87171; }
@keyframes dotPulse { 0%,100%{opacity:1;box-shadow:0 0 6px rgba(245,158,11,.3)} 50%{opacity:.3;box-shadow:0 0 2px rgba(245,158,11,.1)} }

/* ===== 操作按钮 ===== */
.action-btns { display: flex; gap: 2px; }
.act-btn { width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; background: none; border: none; color: rgba(255,255,255,.2); cursor: pointer; border-radius: 6px; transition: all .15s; }
.act-btn:hover { background: rgba(255,255,255,.06); color: rgba(255,255,255,.6); }
.act-btn.danger:hover { background: rgba(239,68,68,.1); color: #f87171; }
.act-btn svg { width: 15px; height: 15px; }

/* ===== 空状态 ===== */
.empty-row td { padding: 60px 0 !important; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; }
.empty-img { width: 56px; height: 56px; color: rgba(255,255,255,.08); margin-bottom: 14px; }
.empty-text { font-size: 14px; color: rgba(255,255,255,.3); margin: 0 0 4px; }
.empty-hint { font-size: 12px; color: rgba(255,255,255,.15); margin: 0; }

/* ===== 分页 ===== */
.pagination-bar { display: flex; justify-content: space-between; align-items: center; margin-top: 16px; }
.paginate-info { font-size: 12px; color: rgba(255,255,255,.25); }
.paginate-btns { display: flex; gap: 4px; }
.paginate-btn { height: 32px; border: 1px solid rgba(255,255,255,.08); border-radius: 8px; background: rgba(255,255,255,.03); color: rgba(255,255,255,.4); font-size: 13px; cursor: pointer; transition: all .2s; font-family: inherit; display: flex; align-items: center; justify-content: center; gap: 5px; }
.paginate-btn.prev, .paginate-btn.next { padding: 0 14px; }
.paginate-btn.page { width: 34px; padding: 0; }
.paginate-btn svg { width: 14px; height: 14px; flex-shrink: 0; }
button.paginate-btn[disabled] { opacity: .15; cursor: not-allowed; }
.paginate-btn:not([disabled]):hover { background: rgba(255,255,255,.08); color: rgba(255,255,255,.7); border-color: rgba(255,255,255,.12); }
.paginate-btn.active { background: rgba(74,140,247,.15); border-color: rgba(74,140,247,.3); color: #8bb8ff; font-weight: 600; }

/* ===== 上传结果通知 ===== */
.upload-result { display: flex; align-items: flex-start; gap: 12px; padding: 14px 16px; border-radius: 10px; margin-bottom: 12px; }
.upload-result.success { background: rgba(34,197,94,.08); border: 1px solid rgba(34,197,94,.15); }
.upload-result.partial { background: rgba(245,158,11,.08); border: 1px solid rgba(245,158,11,.15); }
.upload-result.error { background: rgba(239,68,68,.08); border: 1px solid rgba(239,68,68,.15); }
.upload-result-icon { width: 22px; height: 22px; flex-shrink: 0; margin-top: 1px; }
.upload-result-icon svg { width: 22px; height: 22px; }
.upload-result.success .upload-result-icon { color: #4ade80; }
.upload-result.partial .upload-result-icon { color: #fbbf24; }
.upload-result.error .upload-result-icon { color: #f87171; }
.upload-result-body { flex: 1; min-width: 0; }
.upload-result-title { font-size: 13px; font-weight: 600; margin: 0 0 4px; }
.upload-result.success .upload-result-title { color: #4ade80; }
.upload-result.partial .upload-result-title { color: #fbbf24; }
.upload-result.error .upload-result-title { color: #f87171; }
.upload-result-detail { font-size: 12px; color: rgba(255,255,255,.4); margin: 0; white-space: pre-wrap; line-height: 1.6; max-height: 120px; overflow-y: auto; }
.upload-result-close { background: none; border: none; color: rgba(255,255,255,.3); font-size: 20px; cursor: pointer; padding: 0 2px; line-height: 1; flex-shrink: 0; }
.upload-result-close:hover { color: rgba(255,255,255,.6); }

/* ===== 弹窗 ===== */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.55); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal-card { background: #111a35; border: 1px solid rgba(255,255,255,.08); border-radius: 16px; padding: 26px; width: 460px; max-width: 90vw; }
.modal-upload { width: 520px; }
.modal-preview { width: 640px; max-height: 80vh; display: flex; flex-direction: column; }
.modal-title { font-size: 17px; font-weight: 700; color: #e2e8f0; margin: 0 0 18px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 18px; }
.form-group { margin-bottom: 14px; }
.form-label { display: block; font-size: 12.5px; font-weight: 500; color: rgba(255,255,255,.45); margin-bottom: 5px; }
.form-field { width: 100%; height: 38px; padding: 0 12px; font-size: 13px; color: #e2e8f0; background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.08); border-radius: 8px; outline: none; font-family: inherit; }
.form-select { appearance: none; cursor: pointer; }

/* ===== 拖拽区 ===== */
.drop-zone { border: 2px dashed rgba(255,255,255,.1); border-radius: 12px; padding: 30px 20px; text-align: center; cursor: pointer; transition: all .2s; margin-bottom: 14px; }
.drop-zone:hover, .drop-zone.dragover { border-color: rgba(74,140,247,.3); background: rgba(74,140,247,.03); }
.drop-zone.hasFiles { border-style: solid; border-color: rgba(74,140,247,.2); }
.drop-icon { width: 40px; height: 40px; color: rgba(255,255,255,.15); margin: 0 auto 10px; }
.drop-text { font-size: 14px; color: rgba(255,255,255,.4); margin: 0; }
.drop-hint { font-size: 11px; color: rgba(255,255,255,.2); margin: 8px 0 0; }
.drop-file-list { text-align: left; max-height: 120px; overflow-y: auto; }
.drop-file-item { display: flex; align-items: center; gap: 8px; padding: 6px 10px; background: rgba(255,255,255,.03); border-radius: 6px; margin-bottom: 4px; }
.drop-file-name { flex: 1; font-size: 13px; color: rgba(255,255,255,.7); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.drop-file-size { font-size: 11px; color: rgba(255,255,255,.3); flex-shrink: 0; }
.drop-file-remove { background: none; border: none; color: rgba(255,255,255,.3); cursor: pointer; font-size: 18px; padding: 0 4px; }
.drop-file-remove:hover { color: #f87171; }

/* ===== 上传进度 ===== */
.upload-progress-bar { height: 4px; background: rgba(255,255,255,.05); border-radius: 2px; margin-bottom: 12px; overflow: hidden; }
.upload-progress-fill { height: 100%; background: linear-gradient(90deg,#4a8cf7,#00d4ff); border-radius: 2px; transition: width .3s ease; }

/* ===== 预览 ===== */
.preview-header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,.05); margin-bottom: 14px; }
.preview-file-info { display: flex; align-items: center; gap: 10px; }
.preview-name { font-size: 14px; font-weight: 600; color: #e2e8f0; margin: 0; }
.preview-meta { font-size: 11px; color: rgba(255,255,255,.3); }
.modal-close-btn { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: none; border: none; color: rgba(255,255,255,.3); font-size: 24px; cursor: pointer; border-radius: 6px; }
.modal-close-btn:hover { background: rgba(255,255,255,.05); color: rgba(255,255,255,.6); }
.preview-body { flex: 1; overflow-y: auto; max-height: 50vh; }
.preview-body::-webkit-scrollbar { width: 4px; }
.preview-body::-webkit-scrollbar-thumb { background: rgba(255,255,255,.06); border-radius: 2px; }
.preview-content { font-size: 13px; color: rgba(255,255,255,.6); line-height: 1.8; white-space: pre-wrap; word-break: break-all; margin: 0; font-family: 'SF Mono',Menlo,monospace; }

.file-icon.sm { width: 30px; height: 30px; border-radius: 6px; }
.file-icon.sm svg { width: 16px; height: 16px; }
</style>
