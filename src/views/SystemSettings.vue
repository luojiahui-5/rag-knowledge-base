<template>
  <div class="page">
    <div class="settings-layout">
      <!-- ===== 左侧导航 ===== -->
      <nav class="settings-nav">
        <a v-for="tab in tabs" :key="tab.key" :class="['nav-tab', { active: activeTab === tab.key }]" @click="activeTab = tab.key">
          <span class="nav-tab-icon" v-html="tab.icon"></span>
          <span>{{ tab.label }}</span>
          <span v-if="tab.getBadge && tab.getBadge()" class="nav-tab-badge">{{ tab.getBadge() }}</span>
        </a>
      </nav>

      <!-- ===== 右侧内容 ===== -->
      <div class="settings-content">

        <!-- ========== LLM 模型 ========== -->
        <div v-if="activeTab === 'llm'">
          <div class="section-header">
            <h3 class="section-title">LLM 模型配置</h3>
            <span :class="['status-indicator', llmStatus]">{{ llmStatus === 'ok' ? '● 已连接' : '○ 未连接' }}</span>
          </div>

          <div class="info-card">
            <div class="info-row">
              <span class="info-label">当前模型</span>
              <span class="info-value highlight">DeepSeek Chat (deepseek-chat)</span>
            </div>
            <div class="info-row">
              <span class="info-label">API 地址</span>
              <span class="info-value mono">https://api.deepseek.com/v1/chat/completions</span>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">API Key</label>
            <div class="input-row">
              <input :type="showKey ? 'text' : 'password'" class="form-field flex-1" v-model="llm.apiKey" placeholder="sk-..." />
              <button class="btn btn-ghost btn-sm" @click="showKey = !showKey">{{ showKey ? '隐藏' : '显示' }}</button>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group flex-1">
              <label class="form-label">最大 Token</label>
              <input class="form-field" v-model.number="llm.maxTokens" type="number" />
            </div>
            <div class="form-group flex-1">
              <label class="form-label">Temperature</label>
              <div class="range-wrap">
                <input type="range" min="0" max="1" step="0.1" v-model.number="llm.temperature" class="range-slider" />
                <span class="range-val">{{ llm.temperature }}</span>
              </div>
            </div>
          </div>

          <div class="btn-row">
            <button class="btn btn-primary" @click="saveLLM">保存配置</button>
            <button class="btn btn-outline" @click="testLLM" :disabled="testing">
              <svg v-if="testing" class="spinning" viewBox="0 0 16 16" fill="none"><path d="M2 8a6 6 0 0111.3-2.5M14 8a6 6 0 01-11.3 2.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M14 4v2h-2M2 12v-2h2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              {{ testing ? '测试中...' : '测试连接' }}
            </button>
          </div>
          <div v-if="llmStatus === 'ok'" class="test-success">✓ DeepSeek API 连接正常，响应正常</div>
          <div v-if="testError" class="test-error">{{ testError }}</div>
        </div>

        <!-- ========== Embedding ========== -->
        <div v-if="activeTab === 'embedding'">
          <div class="section-header">
            <h3 class="section-title">Embedding 模型配置</h3>
            <span class="status-indicator ok">● 本地运行中</span>
          </div>

          <div class="info-card">
            <div class="info-row">
              <span class="info-label">当前模型</span>
              <span class="info-value highlight">BGE-Small-ZH-v1.5</span>
            </div>
            <div class="info-row">
              <span class="info-label">向量维度</span>
              <span class="info-value">512</span>
            </div>
            <div class="info-row">
              <span class="info-label">运行方式</span>
              <span class="info-value">本地 CPU / sentence-transformers</span>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Embedding 模型</label>
            <select class="form-field form-select" v-model="embedding.model">
              <option value="BAAI/bge-small-zh-v1.5">BGE-Small-ZH-v1.5 (512d, 轻量)</option>
              <option value="BAAI/bge-large-zh-v1.5">BGE-Large-ZH-v1.5 (1024d, 标准)</option>
              <option value="BAAI/bge-m3">BGE-M3 (1024d, 多语言)</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group flex-1">
              <label class="form-label">Batch Size</label>
              <input class="form-field" v-model.number="embedding.batchSize" type="number" />
            </div>
          </div>
          <button class="btn btn-primary" @click="saveEmbedding">保存配置</button>
        </div>

        <!-- ========== 切片策略 ========== -->
        <div v-if="activeTab === 'chunking'">
          <h3 class="section-title">文档切片策略</h3>

          <div class="form-group">
            <label class="form-label">Chunk Size <span class="label-hint">（每个分块的 token 数）</span></label>
            <div class="range-wrap">
              <input type="range" min="128" max="2048" step="64" v-model.number="chunking.chunkSize" class="range-slider" />
              <span class="range-val">{{ chunking.chunkSize }} tokens</span>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Chunk Overlap <span class="label-hint">（相邻分块的重叠 token 数）</span></label>
            <div class="range-wrap">
              <input type="range" min="0" max="256" step="16" v-model.number="chunking.overlap" class="range-slider" />
              <span class="range-val">{{ chunking.overlap }} tokens</span>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">切分策略</label>
            <select class="form-field form-select" v-model="chunking.strategy">
              <option value="semantic">语义优先（按段落 + 标题边界）</option>
              <option value="fixed">固定长度（严格按 token 数）</option>
              <option value="recursive">递归字符切分</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">分隔符优先级</label>
            <input class="form-field" v-model="chunking.separators" />
          </div>
          <button class="btn btn-primary" @click="saveChunking">保存配置</button>
        </div>

        <!-- ========== 检索参数 ========== -->
        <div v-if="activeTab === 'retrieval'">
          <h3 class="section-title">检索参数</h3>

          <div class="form-row">
            <div class="form-group flex-1">
              <label class="form-label">向量检索 Top-K</label>
              <input class="form-field" v-model.number="retrieval.vectorTopK" type="number" />
            </div>
            <div class="form-group flex-1">
              <label class="form-label">关键词检索 Top-K</label>
              <input class="form-field" v-model.number="retrieval.keywordTopK" type="number" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group flex-1">
              <label class="form-label">语义权重 α</label>
              <div class="range-wrap">
                <input type="range" min="0" max="1" step="0.05" v-model.number="retrieval.alpha" class="range-slider" />
                <span class="range-val">{{ retrieval.alpha }}</span>
              </div>
            </div>
            <div class="form-group flex-1">
              <label class="form-label">最终返回数</label>
              <input class="form-field" v-model.number="retrieval.rerankTopK" type="number" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">相似度阈值</label>
            <div class="range-wrap">
              <input type="range" min="0" max="1" step="0.05" v-model.number="retrieval.threshold" class="range-slider" />
              <span class="range-val">{{ retrieval.threshold }}</span>
            </div>
          </div>
          <button class="btn btn-primary" @click="saveRetrieval">保存配置</button>
        </div>

        <!-- ========== 用户管理 ========== -->
        <div v-if="activeTab === 'users'">
          <div class="section-header">
            <h3 class="section-title">用户管理</h3>
            <span class="page-count">{{ filteredUsers.length }} 个用户</span>
          </div>

          <!-- 搜索 + 筛选 -->
          <div class="user-filter-bar">
            <div class="search-box">
              <svg viewBox="0 0 20 20" fill="none" class="search-box-icon"><circle cx="9" cy="9" r="6" stroke="currentColor" stroke-width="1.5"/><path d="M14 14l3.5 3.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
              <input v-model="userSearch" class="search-box-input" placeholder="搜索用户名、邮箱..." />
            </div>
            <select v-model="roleFilter" class="form-field form-select" style="width:140px">
              <option value="">全部角色</option>
              <option value="admin">管理员</option>
              <option value="editor">编辑者</option>
              <option value="viewer">阅读者</option>
            </select>
            <select v-model="statusFilter" class="form-field form-select" style="width:120px">
              <option value="">全部状态</option>
              <option value="active">正常</option>
              <option value="disabled">已禁用</option>
            </select>
            <button class="btn btn-primary btn-sm" @click="openUserForm()">
              <svg viewBox="0 0 16 16" fill="none"><path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
              添加用户
            </button>
          </div>

          <!-- 表格 -->
          <div class="table-wrap">
            <table class="data-table">
              <thead><tr><th>用户</th><th>账号</th><th>角色</th><th>部门</th><th>状态</th><th>注册时间</th><th>操作</th></tr></thead>
              <tbody>
                <tr v-if="pagedUsers.length === 0">
                  <td colspan="7" class="empty-row">
                    <p class="empty-text">{{ userSearch || roleFilter || statusFilter ? '没有匹配的用户' : '暂无用户数据' }}</p>
                  </td>
                </tr>
                <tr v-for="u in pagedUsers" :key="u.id">
                  <td>
                    <div class="user-cell">
                      <div class="user-avatar-sm" :style="{ background: roleColor(u.role) }">{{ (u.display_name || u.username)?.[0] || '?' }}</div>
                      <div>
                        <span class="user-display-name">{{ u.display_name || u.username }}</span>
                      </div>
                    </div>
                  </td>
                  <td class="td-mono">{{ u.username }}</td>
                  <td><span class="role-badge" :class="u.role">{{ roleLabel(u.role) }}</span></td>
                  <td>{{ u.department || '-' }}</td>
                  <td>
                    <span class="status-light" :class="u.is_active ? 'on' : 'off'"></span>
                    {{ u.is_active ? '正常' : '已禁用' }}
                  </td>
                  <td class="td-mono">{{ fmtDate(u.created_at) }}</td>
                  <td>
                    <div class="action-btns">
                      <button class="act-btn-sm" @click="openUserForm(u)">编辑</button>
                      <button class="act-btn-sm" @click="openResetPwd(u)">重置密码</button>
                      <button class="act-btn-sm" :class="u.is_active ? 'danger' : 'success'" @click="toggleUserStatus(u)">{{ u.is_active ? '禁用' : '启用' }}</button>
                      <button class="act-btn-sm danger" @click="confirmDeleteUser(u)">删除</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 分页 -->
          <div class="pagination-bar" v-if="userPages > 1">
            <span class="paginate-info">{{ userStart }}-{{ userEnd }} / {{ filteredUsers.length }}</span>
            <div class="paginate-btns">
              <button class="paginate-btn" :disabled="userPage <= 1" @click="userPage--">上一页</button>
              <button v-for="p in userPageNums" :key="p" :class="['paginate-btn', { active: p === userPage }]" @click="userPage = p">{{ p }}</button>
              <button class="paginate-btn" :disabled="userPage >= userPages" @click="userPage++">下一页</button>
            </div>
          </div>

          <!-- 添加/编辑弹窗 -->
          <div v-if="showUserModal" class="modal-overlay" @click.self="showUserModal = false">
            <div class="modal-card">
              <h3 class="modal-title">{{ editingUser ? '编辑用户' : '添加用户' }}</h3>
              <div class="form-row">
                <div class="form-group flex-1">
                  <label class="form-label">用户名 <span class="required">*</span></label>
                  <input class="form-field" v-model="userForm.username" placeholder="登录账号" maxlength="30" />
                </div>
                <div class="form-group flex-1">
                  <label class="form-label">显示名称</label>
                  <input class="form-field" v-model="userForm.display_name" placeholder="对外显示名称" maxlength="30" />
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">邮箱 <span class="required">*</span></label>
                <input class="form-field" v-model="userForm.email" placeholder="user@company.com" />
              </div>
              <div v-if="!editingUser" class="form-group">
                <label class="form-label">初始密码 <span class="required">*</span></label>
                <input class="form-field" v-model="userForm.password" type="password" placeholder="至少 6 位" minlength="6" />
              </div>
              <div class="form-row">
                <div class="form-group flex-1">
                  <label class="form-label">角色</label>
                  <AppSelect v-model="userForm.role" :options="roleOptions" placeholder="选择角色" />
                </div>
                <div class="form-group flex-1">
                  <label class="form-label">部门</label>
                  <AppSelect v-model="userForm.department" :options="deptOptions" placeholder="选择部门" />
                </div>
              </div>
              <div v-if="userError" class="modal-error">{{ userError }}</div>
              <div class="modal-actions">
                <button class="btn btn-ghost" @click="showUserModal = false">取消</button>
                <button class="btn btn-primary" :disabled="userSaving" @click="saveUser">{{ userSaving ? '保存中...' : '确认' }}</button>
              </div>
            </div>
          </div>

          <!-- 重置密码弹窗 -->
          <div v-if="showPwdModal" class="modal-overlay" @click.self="showPwdModal = false">
            <div class="modal-card modal-sm">
              <h3 class="modal-title">重置密码</h3>
              <p class="reset-pwd-user">用户：<strong>{{ pwdTarget?.display_name || pwdTarget?.username }}</strong></p>
              <div class="form-group">
                <label class="form-label">新密码</label>
                <input class="form-field" v-model="newPassword" type="password" placeholder="至少 6 位" />
              </div>
              <div v-if="pwdError" class="modal-error">{{ pwdError }}</div>
              <div class="modal-actions">
                <button class="btn btn-ghost" @click="showPwdModal = false">取消</button>
                <button class="btn btn-primary" :disabled="!newPassword || pwdSaving" @click="doResetPwd">{{ pwdSaving ? '重置中...' : '确认重置' }}</button>
              </div>
            </div>
          </div>

          <!-- 删除确认弹窗 -->
          <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
            <div class="modal-card delete-dialog">
              <div class="delete-dialog-icon">
                <svg viewBox="0 0 28 28" fill="none">
                  <circle cx="14" cy="14" r="13" stroke="url(#delGrad)" stroke-width="2"/>
                  <path d="M14 9v6M14 18.5h0" stroke="url(#delGrad)" stroke-width="2.5" stroke-linecap="round"/>
                  <defs><linearGradient id="delGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#f87171"/><stop offset="100%" stop-color="#ef4444"/></linearGradient></defs>
                </svg>
              </div>
              <h3 class="delete-dialog-title">确认删除用户</h3>
              <div class="delete-dialog-user">
                <div class="delete-dialog-avatar" :style="{ background: roleColor(deleteTarget.role) }">{{ (deleteTarget.display_name || deleteTarget.username)?.[0] || '?' }}</div>
                <div>
                  <p class="delete-dialog-name">{{ deleteTarget.display_name || deleteTarget.username }}</p>
                  <p class="delete-dialog-meta">{{ deleteTarget.email }} · {{ roleLabel(deleteTarget.role) }}</p>
                </div>
              </div>
              <p class="delete-dialog-warn">此操作将<strong>永久删除</strong>该用户及其所有关联数据，不可恢复。</p>
              <div class="delete-dialog-actions">
                <button class="btn btn-ghost" @click="deleteTarget = null">取消</button>
                <button class="btn btn-danger" @click="doDeleteUser">
                  <svg viewBox="0 0 16 16" fill="none"><path d="M3 4h10M6 4V2h4v2M5 4v9a1 1 0 001 1h4a1 1 0 001-1V4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  删除用户
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- ========== 系统信息 ========== -->
        <div v-if="activeTab === 'info'">
          <h3 class="section-title">系统信息</h3>
          <div class="info-grid">
            <div class="info-card">
              <div class="info-row"><span class="info-label">系统版本</span><span class="info-value">1.0.0</span></div>
              <div class="info-row"><span class="info-label">前端框架</span><span class="info-value">Vue 3 + Vite + Tailwind CSS</span></div>
              <div class="info-row"><span class="info-label">后端框架</span><span class="info-value">FastAPI + SQLAlchemy</span></div>
            </div>
            <div class="info-card">
              <div class="info-row"><span class="info-label">数据库</span><span class="info-value">SQLite (开发) / PostgreSQL (生产)</span></div>
              <div class="info-row"><span class="info-label">LLM 引擎</span><span class="info-value highlight">DeepSeek Chat</span></div>
              <div class="info-row"><span class="info-label">Embedding</span><span class="info-value">BGE-Small-ZH-v1.5 (本地)</span></div>
            </div>
            <div class="info-card">
              <div class="info-row"><span class="info-label">知识库数</span><span class="info-value">{{ sysInfo.kbCount }}</span></div>
              <div class="info-row"><span class="info-label">文档总数</span><span class="info-value">{{ sysInfo.docCount }}</span></div>
              <div class="info-row"><span class="info-label">用户数</span><span class="info-value">{{ users.length }}</span></div>
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
import { ref, reactive, computed, onMounted } from 'vue'
import AppSelect from '../components/AppSelect.vue'

const activeTab = ref('llm')
const showKey = ref(false)
const toast = ref(null)

const showT = (msg, type = 'success') => {
  toast.value = { message: msg, type }
  setTimeout(() => toast.value = null, 2500)
}

// ===== LLM =====
const llm = reactive({ apiKey: 'sk-8b35bd845c8f4c1c9cd561a51c48ce8e', maxTokens: 4096, temperature: 0.3 })
const llmStatus = ref('ok')
const testing = ref(false)
const testError = ref('')

const saveLLM = () => showT('LLM 配置已保存')
const testLLM = async () => {
  testing.value = true; testError.value = ''
  try {
    const resp = await fetch('https://api.deepseek.com/v1/chat/completions', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${llm.apiKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: 'deepseek-chat', messages: [{ role: 'user', content: 'Hello' }], max_tokens: 10 }),
    })
    if (resp.ok) { llmStatus.value = 'ok'; showT('DeepSeek API 连接成功') }
    else { llmStatus.value = 'error'; testError.value = `HTTP ${resp.status}: ${await resp.text().then(t => t.slice(0, 200))}` }
  } catch (e) { llmStatus.value = 'error'; testError.value = e.message }
  testing.value = false
}

// ===== Embedding =====
const embedding = reactive({ model: 'BAAI/bge-small-zh-v1.5', batchSize: 32 })
const saveEmbedding = () => showT('Embedding 配置已保存')

// ===== Chunking =====
const chunking = reactive({ chunkSize: 512, overlap: 64, strategy: 'semantic', separators: '\\n\\n, \\n, 。, . , ；, ; , ，' })
const saveChunking = () => showT('切片策略已保存')

// ===== Retrieval =====
const retrieval = reactive({ vectorTopK: 50, keywordTopK: 50, alpha: 0.7, rerankTopK: 5, threshold: 0.5 })
const saveRetrieval = () => showT('检索参数已保存')

// ===== Users =====
const users = ref([])
const userSearch = ref('')
const roleFilter = ref('')
const statusFilter = ref('')
const userPage = ref(1)
const userPageSize = 8

// User form
const showUserModal = ref(false)
const editingUser = ref(null)
const userForm = reactive({ username: '', display_name: '', email: '', password: '', role: 'viewer', department: '' })
const userError = ref('')
const userSaving = ref(false)

// Reset password
const showPwdModal = ref(false)
const pwdTarget = ref(null)
const newPassword = ref('')
const pwdError = ref('')
const pwdSaving = ref(false)

// Delete
const deleteTarget = ref(null)

const sysInfo = reactive({ kbCount: 0, docCount: 0 })

const fetchUsers = async () => {
  try {
    const token = sessionStorage.getItem('token')
    const resp = await fetch('/api/v1/auth/users', { headers: { Authorization: `Bearer ${token}` } })
    if (resp.ok) {
      users.value = await resp.json()
    }
  } catch (e) { /* ignore */ }
}

// Filters & pagination
const filteredUsers = computed(() => {
  let list = users.value
  if (userSearch.value) {
    const q = userSearch.value.toLowerCase()
    list = list.filter(u => (u.username || '').toLowerCase().includes(q) || (u.email || '').toLowerCase().includes(q) || (u.display_name || '').toLowerCase().includes(q))
  }
  if (roleFilter.value) list = list.filter(u => u.role === roleFilter.value)
  if (statusFilter.value === 'active') list = list.filter(u => u.is_active)
  if (statusFilter.value === 'disabled') list = list.filter(u => !u.is_active)
  return list
})
const userPages = computed(() => Math.max(1, Math.ceil(filteredUsers.value.length / userPageSize)))
const pagedUsers = computed(() => filteredUsers.value.slice((userPage.value - 1) * userPageSize, userPage.value * userPageSize))
const userStart = computed(() => filteredUsers.value.length === 0 ? 0 : (userPage.value - 1) * userPageSize + 1)
const userEnd = computed(() => Math.min(userPage.value * userPageSize, filteredUsers.value.length))
const userPageNums = computed(() => {
  const pages = []
  const s = Math.max(1, userPage.value - 2)
  const e = Math.min(userPages.value, s + 4)
  for (let i = s; i <= e; i++) pages.push(i)
  return pages
})

// Form
const openUserForm = (user = null) => {
  editingUser.value = user
  userError.value = ''
  if (user) {
    Object.assign(userForm, { username: user.username, display_name: user.display_name || '', email: user.email, password: '', role: user.role, department: user.department || '' })
  } else {
    Object.assign(userForm, { username: '', display_name: '', email: '', password: '', role: 'viewer', department: '' })
  }
  showUserModal.value = true
}

const saveUser = async () => {
  if (!userForm.username || !userForm.email) { userError.value = '请填写用户名和邮箱'; return }
  if (!editingUser.value) {
    if (!userForm.password) { userError.value = '请设置初始密码'; return }
    if (userForm.password.length < 6) { userError.value = '密码至少 6 位'; return }
  }
  userSaving.value = true; userError.value = ''
  try {
    const token = sessionStorage.getItem('token')
    const url = editingUser.value ? `/api/v1/auth/users/${editingUser.value.id}` : '/api/v1/auth/register'
    const method = editingUser.value ? 'PUT' : 'POST'
    const resp = await fetch(url, {
      method, headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(userForm),
    })
    if (resp.ok) {
      showT(editingUser.value ? '用户已更新' : '用户已创建')
      showUserModal.value = false
      await fetchUsers()
    } else {
      const err = await resp.json().catch(() => ({}))
      // 处理 Pydantic 验证错误（数组格式）
      const detail = err.detail
      if (Array.isArray(detail)) {
        userError.value = detail.map(d => d.msg).join('；')
      } else {
        userError.value = typeof detail === 'string' ? detail : '操作失败'
      }
    }
  } catch (e) { userError.value = e.message }
  userSaving.value = false
}

// Reset password
const openResetPwd = (user) => {
  pwdTarget.value = user
  newPassword.value = ''
  pwdError.value = ''
  showPwdModal.value = true
}

const doResetPwd = async () => {
  if (!newPassword.value || newPassword.value.length < 6) { pwdError.value = '密码至少 6 位'; return }
  pwdSaving.value = true; pwdError.value = ''
  try {
    const token = sessionStorage.getItem('token')
    const resp = await fetch(`/api/v1/auth/users/${pwdTarget.value.id}/reset-password`, {
      method: 'POST', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: newPassword.value }),
    })
    if (resp.ok) {
      showT('密码已重置')
      showPwdModal.value = false
    } else {
      const err = await resp.json().catch(() => ({}))
      pwdError.value = err.detail || '操作失败'
    }
  } catch (e) { pwdError.value = e.message }
  pwdSaving.value = false
}

// Toggle status
const toggleUserStatus = async (user) => {
  try {
    const token = sessionStorage.getItem('token')
    const resp = await fetch(`/api/v1/auth/users/${user.id}`, {
      method: 'PUT', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_active: !user.is_active }),
    })
    if (resp.ok) { user.is_active = !user.is_active; showT(user.is_active ? '用户已启用' : '用户已禁用') }
  } catch (e) { showT('操作失败', 'error') }
}

// Delete user
const confirmDeleteUser = (user) => { deleteTarget.value = user }
const doDeleteUser = async () => {
  try {
    const token = sessionStorage.getItem('token')
    const resp = await fetch(`/api/v1/auth/users/${deleteTarget.value.id}`, {
      method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` },
    })
    if (resp.ok || resp.status === 204) {
      showT(`用户「${deleteTarget.value.display_name || deleteTarget.value.username}」已删除`)
      deleteTarget.value = null
      await fetchUsers()
    } else {
      const err = await resp.json().catch(() => ({}))
      showT(err.detail || '删除失败', 'error')
    }
  } catch (e) { showT('删除失败: ' + e.message, 'error') }
}

// ===== System Info =====
const loadSysInfo = async () => {
  try {
    const token = sessionStorage.getItem('token')
    const [kbResp, docResp] = await Promise.all([
      fetch('/api/v1/knowledge', { headers: { Authorization: `Bearer ${token}` } }),
      fetch('/api/v1/documents', { headers: { Authorization: `Bearer ${token}` } }),
    ])
    if (kbResp.ok) sysInfo.kbCount = (await kbResp.json()).length
    if (docResp.ok) sysInfo.docCount = (await docResp.json()).length
  } catch (e) { /* ignore */ }
}

// ===== Tools =====
const roleLabel = (r) => ({ admin: '超级管理员', editor: '编辑者', viewer: '阅读者' }[r] || r)
const roleColor = (r) => ({ admin: 'linear-gradient(135deg,#ef4444,#f87171)', editor: 'linear-gradient(135deg,#4a8cf7,#818cf8)', viewer: 'linear-gradient(135deg,#6b7280,#9ca3af)' }[r])
const fmtDate = (s) => s ? new Date(s).toLocaleDateString('zh-CN') : '-'

// ===== Tabs =====
const roleOptions = [
  { value: 'admin', label: '超级管理员' },
  { value: 'editor', label: '编辑者' },
  { value: 'viewer', label: '阅读者' },
]
const deptOptions = [
  { value: '', label: '未指定' },
  { value: '技术研发部', label: '技术研发部' },
  { value: '产品部', label: '产品部' },
  { value: '运维部', label: '运维部' },
  { value: '人力资源部', label: '人力资源部' },
  { value: '市场部', label: '市场部' },
  { value: '财务部', label: '财务部' },
]

const tabs = [
  { key: 'llm', label: 'LLM 模型', icon: '<svg viewBox="0 0 16 16" fill="none"><rect x="2" y="3" width="12" height="10" rx="2" stroke="currentColor" stroke-width="1.3"/><path d="M6 8l1.5 1.5L10 7" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>' },
  { key: 'embedding', label: 'Embedding', icon: '<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.3"/><circle cx="8" cy="8" r="2" fill="currentColor"/></svg>' },
  { key: 'chunking', label: '切片策略', icon: '<svg viewBox="0 0 16 16" fill="none"><path d="M3 4h10M3 8h10M3 12h7" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>' },
  { key: 'retrieval', label: '检索参数', icon: '<svg viewBox="0 0 16 16" fill="none"><circle cx="7" cy="7" r="5" stroke="currentColor" stroke-width="1.3"/><path d="M11 11l3 3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>' },
  { key: 'users', label: '用户管理', icon: '<svg viewBox="0 0 16 16" fill="none"><circle cx="6" cy="5" r="3" stroke="currentColor" stroke-width="1.3"/><path d="M1 14c0-2.76 2.24-5 5-5s5 2.24 5 5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>', getBadge: () => users.value.length > 0 ? String(users.value.length) : null },
  { key: 'info', label: '系统信息', icon: '<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.3"/><path d="M8 5v3M8 11h0" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>' },
]

onMounted(() => { fetchUsers(); loadSysInfo() })
</script>

<style scoped>
.page { padding: 24px; }
.settings-layout { display: flex; gap: 20px; align-items: flex-start; }

/* ===== 左侧导航 ===== */
.settings-nav { width: 170px; flex-shrink: 0; display: flex; flex-direction: column; gap: 2px; }
.nav-tab { display: flex; align-items: center; gap: 8px; padding: 9px 12px; border-radius: 8px; font-size: 13px; color: rgba(255,255,255,.4); cursor: pointer; transition: all .2s; }
.nav-tab:hover { color: rgba(255,255,255,.6); background: rgba(255,255,255,.03); }
.nav-tab.active { color: #e2e8f0; background: rgba(74,140,247,.12); }
.nav-tab-icon { width: 16px; height: 16px; display: flex; align-items: center; }
.nav-tab-icon :deep(svg) { width: 16px; height: 16px; }
.nav-tab-badge { margin-left: auto; font-size: 10px; background: rgba(74,140,247,.2); color: #8bb8ff; padding: 1px 7px; border-radius: 10px; font-weight: 600; }

/* ===== 右侧内容 ===== */
.settings-content { flex: 1; background: rgba(255,255,255,.015); border: 1px solid rgba(255,255,255,.05); border-radius: 14px; padding: 24px; min-height: 440px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 8px; }
.section-title { font-size: 16px; font-weight: 700; color: #e2e8f0; margin: 0 0 16px; padding-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,.06); }
.section-header .section-title { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }

.status-indicator { font-size: 12px; font-weight: 500; padding: 4px 10px; border-radius: 12px; }
.status-indicator.ok { color: #4ade80; background: rgba(34,197,94,.08); }
.status-indicator.error { color: #f87171; background: rgba(239,68,68,.08); }

/* ===== 信息卡片 ===== */
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.info-card { background: rgba(255,255,255,.02); border: 1px solid rgba(255,255,255,.04); border-radius: 10px; padding: 14px 16px; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; }
.info-row + .info-row { border-top: 1px solid rgba(255,255,255,.03); }
.info-label { font-size: 12.5px; color: rgba(255,255,255,.35); }
.info-value { font-size: 12.5px; color: rgba(255,255,255,.6); }
.info-value.highlight { color: #8bb8ff; font-weight: 500; }
.info-value.mono { font-family: 'SF Mono', Menlo, monospace; font-size: 11px; }

/* ===== 表单 ===== */
.form-group { margin-bottom: 16px; }
.form-label { display: block; font-size: 12.5px; font-weight: 500; color: rgba(255,255,255,.45); margin-bottom: 5px; }
.form-label .label-hint { font-weight: 400; color: rgba(255,255,255,.2); font-size: 11px; }
.form-label .required { color: #f87171; }
.form-field { width: 100%; height: 40px; padding: 0 12px; font-size: 13px; color: #e2e8f0; background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08); border-radius: 8px; outline: none; font-family: inherit; transition: border-color .2s; }
.form-field:focus { border-color: rgba(74,140,247,.4); }
.form-select { appearance: none; cursor: pointer; }
.form-row { display: flex; gap: 14px; }
.flex-1 { flex: 1; }
.input-row { display: flex; gap: 8px; align-items: center; }

/* ===== Range Slider ===== */
.range-wrap { display: flex; align-items: center; gap: 12px; }
.range-slider { flex: 1; height: 6px; -webkit-appearance: none; appearance: none; background: rgba(255,255,255,.08); border-radius: 3px; outline: none; cursor: pointer; }
.range-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 16px; height: 16px; border-radius: 50%; background: #4a8cf7; cursor: pointer; border: 2px solid #0d1538; }
.range-val { font-size: 13px; font-weight: 600; color: #8bb8ff; min-width: 70px; text-align: right; }

/* ===== 按钮 ===== */
.btn { display: inline-flex; align-items: center; gap: 6px; height: 36px; padding: 0 16px; border-radius: 8px; font-size: 13px; font-weight: 500; cursor: pointer; transition: all .2s; font-family: inherit; border: 1px solid transparent; }
.btn-primary { background: linear-gradient(135deg,#4a6cf7,#5b8cf7); color: #fff; }
.btn-primary:hover:not(:disabled) { opacity: .9; }
.btn-primary:disabled { opacity: .4; cursor: not-allowed; }
.btn-ghost { background: rgba(255,255,255,.04); color: rgba(255,255,255,.6); border-color: rgba(255,255,255,.08); }
.btn-ghost:hover { background: rgba(255,255,255,.08); }
.btn-danger { background: rgba(239,68,68,.1); color: #f87171; border-color: rgba(239,68,68,.2); }
.btn-danger:hover { background: rgba(239,68,68,.2); color: #fca5a5; }
.btn-outline { background: transparent; color: rgba(255,255,255,.5); border-color: rgba(255,255,255,.1); }
.btn-outline:hover:not(:disabled) { background: rgba(255,255,255,.04); color: rgba(255,255,255,.7); }
.btn-sm { height: 30px; padding: 0 10px; font-size: 12px; }
.btn svg { width: 14px; height: 14px; }
.btn-row { display: flex; gap: 10px; margin-top: 8px; }
.spinning { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.test-success { margin-top: 8px; font-size: 12px; color: #4ade80; }
.test-error { margin-top: 8px; font-size: 12px; color: #f87171; background: rgba(239,68,68,.06); padding: 8px 12px; border-radius: 8px; }

/* ===== 用户表格 ===== */
.table-wrap { background: rgba(255,255,255,.015); border: 1px solid rgba(255,255,255,.04); border-radius: 10px; overflow: hidden; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { text-align: left; padding: 10px 14px; font-size: 11.5px; font-weight: 600; color: rgba(255,255,255,.3); text-transform: uppercase; letter-spacing: .5px; border-bottom: 1px solid rgba(255,255,255,.04); background: rgba(255,255,255,.01); }
.data-table td { padding: 10px 14px; font-size: 13px; color: rgba(255,255,255,.55); border-bottom: 1px solid rgba(255,255,255,.025); }
.data-table tr:hover td { background: rgba(255,255,255,.015); }
.td-mono { font-family: 'SF Mono', Menlo, monospace; font-size: 12px; }
.user-cell { display: flex; align-items: center; gap: 8px; }
.user-avatar-sm { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; color: #fff; flex-shrink: 0; }
.role-badge { font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 500; }
.role-badge.admin { background: rgba(239,68,68,.1); color: #f87171; }
.role-badge.editor { background: rgba(74,140,247,.1); color: #8bb8ff; }
.role-badge.viewer { background: rgba(255,255,255,.05); color: rgba(255,255,255,.35); }
.status-light { display: inline-block; width: 6px; height: 6px; border-radius: 50%; margin-right: 6px; }
.status-light.on { background: #4ade80; box-shadow: 0 0 6px rgba(34,197,94,.3); }
.status-light.off { background: #ef4444; }
.action-btns { display: flex; gap: 4px; }
.act-btn-sm { font-size: 12px; color: rgba(255,255,255,.3); background: none; border: none; cursor: pointer; padding: 4px 8px; border-radius: 4px; font-family: inherit; }
.act-btn-sm:hover { background: rgba(255,255,255,.04); color: rgba(255,255,255,.6); }
.act-btn-sm.danger:hover { color: #f87171; background: rgba(239,68,68,.08); }
.act-btn-sm.success:hover { color: #4ade80; background: rgba(34,197,94,.08); }

/* ===== 用户搜索栏 ===== */
.user-filter-bar { display: flex; gap: 10px; align-items: center; margin-bottom: 16px; flex-wrap: wrap; }
.user-filter-bar .search-box { position: relative; flex: 1; min-width: 200px; }
.user-filter-bar .search-box-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); width: 14px; height: 14px; color: rgba(255,255,255,.2); pointer-events: none; }
.user-filter-bar .search-box-input { width: 100%; height: 36px; padding: 0 16px 0 32px; font-size: 13px; color: #e2e8f0; background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08); border-radius: 8px; outline: none; font-family: inherit; }
.user-filter-bar .search-box-input::placeholder { color: rgba(255,255,255,.2); }
.user-filter-bar .search-box-input:focus { border-color: rgba(74,140,247,.4); }
.user-display-name { font-size: 13px; color: rgba(255,255,255,.7); }
.page-count { font-size: 13px; color: rgba(255,255,255,.3); }

/* ===== 分页 ===== */
.pagination-bar { display: flex; justify-content: space-between; align-items: center; margin-top: 14px; }
.paginate-info { font-size: 12px; color: rgba(255,255,255,.25); }
.paginate-btns { display: flex; gap: 4px; }
.paginate-btn { height: 30px; padding: 0 10px; border: 1px solid rgba(255,255,255,.06); border-radius: 6px; background: rgba(255,255,255,.02); color: rgba(255,255,255,.35); font-size: 12px; cursor: pointer; font-family: inherit; transition: all .15s; }
.paginate-btn.active { background: rgba(74,140,247,.12); border-color: rgba(74,140,247,.25); color: #8bb8ff; }
.paginate-btn:disabled { opacity: .2; cursor: default; }
.paginate-btn:not(:disabled):hover { background: rgba(255,255,255,.06); }

/* ===== 删除确认弹窗 ===== */
.delete-dialog { width: 420px; text-align: center; padding: 32px 28px 24px; }
.delete-dialog-icon { width: 56px; height: 56px; margin: 0 auto 16px; }
.delete-dialog-icon svg { width: 100%; height: 100%; }
.delete-dialog-title { font-size: 17px; font-weight: 700; color: #e2e8f0; margin: 0 0 18px; }
.delete-dialog-user { display: flex; align-items: center; gap: 10px; padding: 12px 16px; background: rgba(255,255,255,.025); border: 1px solid rgba(255,255,255,.05); border-radius: 10px; text-align: left; margin-bottom: 14px; }
.delete-dialog-avatar { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; color: #fff; flex-shrink: 0; }
.delete-dialog-name { font-size: 14px; font-weight: 600; color: rgba(255,255,255,.8); margin: 0; }
.delete-dialog-meta { font-size: 12px; color: rgba(255,255,255,.3); margin: 2px 0 0; }
.delete-dialog-warn { font-size: 12.5px; color: rgba(255,255,255,.35); line-height: 1.6; margin: 0 0 20px; }
.delete-dialog-warn strong { color: #f87171; font-weight: 600; }
.delete-dialog-actions { display: flex; gap: 10px; justify-content: center; }

/* ===== 重置密码 ===== */
.reset-pwd-user { font-size: 13px; color: rgba(255,255,255,.4); margin: 0 0 12px; }
.reset-pwd-user strong { color: rgba(255,255,255,.7); }

/* ===== 空行 ===== */
.empty-row td { padding: 40px 0 !important; text-align: center; }
.empty-text { font-size: 13px; color: rgba(255,255,255,.2); margin: 0; }

/* ===== 弹窗 ===== */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.55); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal-card { width: 480px; max-width: 90vw; background: #111a35; border: 1px solid rgba(255,255,255,.08); border-radius: 16px; padding: 26px; }
.modal-title { font-size: 17px; font-weight: 700; color: #e2e8f0; margin: 0 0 18px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 18px; }
.modal-error { font-size: 12px; color: #f87171; background: rgba(239,68,68,.08); padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; }

/* ===== Toast ===== */
.toast { position: fixed; top: 20px; right: 20px; z-index: 200; padding: 12px 20px; border-radius: 10px; font-size: 13px; font-weight: 500; backdrop-filter: blur(12px); box-shadow: 0 8px 32px rgba(0,0,0,.4); animation: toastIn .3s ease; }
.toast.success { background: rgba(34,197,94,.15); border: 1px solid rgba(34,197,94,.25); color: #4ade80; }
.toast.error { background: rgba(239,68,68,.15); border: 1px solid rgba(239,68,68,.25); color: #f87171; }
@keyframes toastIn { from { opacity: 0; transform: translateX(40px); } to { opacity: 1; transform: translateX(0); } }
</style>
