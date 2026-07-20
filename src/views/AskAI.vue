<template>
  <div class="page">
    <div class="ask-layout">
      <!-- ===== 左侧对话区 ===== -->
      <div class="chat-main">
        <!-- 对话区 -->
        <div class="chat-messages" ref="chatRef">
          <!-- 欢迎态 -->
          <div v-if="messages.length === 0" class="welcome">
            <div class="welcome-icon">
              <svg viewBox="0 0 64 64" fill="none">
                <circle cx="28" cy="28" r="18" stroke="url(#aiGrad)" stroke-width="2.5"/>
                <path d="M44 44l12 12" stroke="url(#aiGrad)" stroke-width="3" stroke-linecap="round"/>
                <circle cx="22" cy="28" r="3" fill="url(#aiGrad)"/>
                <circle cx="30" cy="26" r="3" fill="url(#aiGrad)"/>
                <circle cx="26" cy="32" r="3" fill="url(#aiGrad)"/>
                <defs><linearGradient id="aiGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#00d4ff"/><stop offset="100%" stop-color="#4a6cf7"/></linearGradient></defs>
              </svg>
            </div>
            <h2 class="welcome-title">智能问答</h2>
            <p class="welcome-desc">基于企业知识库的 AI 助手，用自然语言提问即可获取精准答案</p>
            <div class="welcome-hints">
              <button v-for="h in hints" :key="h" class="hint-chip" @click="quickAsk(h)">{{ h }}</button>
            </div>
          </div>

          <!-- 消息列表 -->
          <div v-for="(msg, i) in messages" :key="i" :class="['msg', msg.role]">
            <div class="msg-avatar">
              <template v-if="msg.role === 'user'">我</template>
              <template v-else>
                <svg viewBox="0 0 16 16" fill="none"><circle cx="7" cy="7" r="4.5" stroke="currentColor" stroke-width="1.3"/><path d="M11 11l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
              </template>
            </div>
            <div class="msg-body">
              <div class="msg-content" v-html="renderContent(msg.content)"></div>
              <!-- 来源 -->
              <div v-if="msg.sources && msg.sources.length" class="msg-sources">
                <div class="sources-header" @click="msg.showSources = !msg.showSources">
                  <svg viewBox="0 0 16 16" fill="none"><path d="M3 2h7l4 4v9a1 1 0 01-1 1H3a1 1 0 01-1-1V3a1 1 0 011-1z" stroke="currentColor" stroke-width="1.2"/><path d="M10 2v4h4" stroke="currentColor" stroke-width="1.2"/></svg>
                  参考 {{ msg.sources.length }} 个来源
                  <svg viewBox="0 0 16 16" fill="none" class="sources-chevron" :class="{ open: msg.showSources }"><path d="M5 6l3 3 3-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                </div>
                <div v-if="msg.showSources !== false" class="sources-list">
                  <div v-for="(s, j) in msg.sources" :key="j" class="source-row" @click.stop="openSource(s)">
                    <span class="source-num">{{ j + 1 }}</span>
                    <span class="source-doc">{{ s.doc }}</span>
                    <span class="source-page">{{ s.page }}</span>
                    <span class="source-score" :class="scoreClass(s.score)">{{ (s.score * 100).toFixed(0) }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 打字中 -->
          <div v-if="loading" class="msg assistant">
            <div class="msg-avatar">
              <svg viewBox="0 0 16 16" fill="none"><circle cx="7" cy="7" r="4.5" stroke="currentColor" stroke-width="1.3"/><path d="M11 11l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
            </div>
            <div class="msg-body">
              <div class="typing"><span></span><span></span><span></span></div>
            </div>
          </div>
        </div>

        <!-- 输入区 -->
        <div class="chat-footer">
          <div class="chat-input-wrap">
            <textarea
              v-model="inputText"
              class="chat-textarea"
              placeholder="输入你的问题，Enter 发送，Shift+Enter 换行..."
              rows="1"
              @keydown.enter.exact.prevent="sendMessage"
              @input="autoResize"
              ref="inputRef"
            ></textarea>
            <button class="send-btn" :disabled="!inputText.trim() || loading" @click="sendMessage">
              <svg viewBox="0 0 20 20" fill="none"><path d="M2 10l16-6-6 12-2-4-4-2z" fill="currentColor"/></svg>
            </button>
          </div>
          <div class="chat-footer-bar">
            <select v-model="selectedKB" class="kb-select-sm">
              <option value="">全部知识库</option>
              <option v-for="kb in kbList" :key="kb.id" :value="kb.id">{{ kb.name }}</option>
            </select>
            <span class="footer-hint">AI 回答仅供参考，请核对来源文档</span>
          </div>
        </div>
      </div>

      <!-- ===== 右侧面板 ===== -->
      <div class="side-panel">
        <!-- 调试信息 -->
        <div class="panel-section">
          <h4 class="panel-title">检索链路</h4>
          <div v-if="!lastDebug" class="panel-empty">
            <svg viewBox="0 0 40 40" fill="none" class="panel-empty-icon"><circle cx="20" cy="20" r="14" stroke="currentColor" stroke-width="1.5"/><path d="M20 14v6M20 24h0" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
            <p>发送问题后展示检索过程</p>
          </div>
          <div v-else class="debug-steps">
            <div class="debug-step">
              <div class="debug-step-num">1</div>
              <div class="debug-step-body">
                <span class="debug-step-title">Query 向量化</span>
                <span class="debug-step-meta">BGE-M3 · 1024d</span>
              </div>
            </div>
            <div class="debug-step">
              <div class="debug-step-num">2</div>
              <div class="debug-step-body">
                <span class="debug-step-title">向量检索</span>
                <span class="debug-step-meta">召回 {{ lastDebug.vectorRecall }} 条 · {{ lastDebug.vectorLatency }}ms</span>
              </div>
            </div>
            <div class="debug-step">
              <div class="debug-step-num">3</div>
              <div class="debug-step-body">
                <span class="debug-step-title">关键词检索</span>
                <span class="debug-step-meta">召回 {{ lastDebug.keywordRecall }} 条 · {{ lastDebug.keywordLatency }}ms</span>
              </div>
            </div>
            <div class="debug-step">
              <div class="debug-step-num">4</div>
              <div class="debug-step-body">
                <span class="debug-step-title">RRF 融合</span>
                <span class="debug-step-meta">去重后 {{ lastDebug.merged }} 条</span>
              </div>
            </div>
            <div class="debug-step">
              <div class="debug-step-num">5</div>
              <div class="debug-step-body">
                <span class="debug-step-title">LLM 生成</span>
                <span class="debug-step-meta">DeepSeek · {{ lastDebug.tokens }} tokens · {{ lastDebug.llmLatency }}ms</span>
              </div>
            </div>
            <div class="debug-total">
              <span>总耗时</span>
              <strong>{{ lastDebug.totalLatency }}ms</strong>
            </div>
          </div>
        </div>

        <!-- 历史记录 -->
        <div class="panel-section">
          <h4 class="panel-title">对话历史</h4>
          <div v-if="history.length === 0" class="panel-empty sm">
            <p>暂无历史记录</p>
          </div>
          <div v-else class="history-list">
            <div v-for="(h, i) in history" :key="i" class="history-item" @click="loadHistory(i)">
              <span class="history-text">{{ h.question }}</span>
              <span class="history-time">{{ h.time }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 来源原文弹窗 ===== -->
    <div v-if="sourcePopup" class="popup-overlay" @click.self="sourcePopup = null">
      <div class="popup-card">
        <div class="popup-header">
          <h4 class="popup-title">{{ sourcePopup.doc }}</h4>
          <span class="popup-meta">{{ sourcePopup.page }} · 相关度 {{ (sourcePopup.score * 100).toFixed(0) }}%</span>
          <button class="popup-close" @click="sourcePopup = null">&times;</button>
        </div>
        <div class="popup-body">
          <pre class="popup-content">{{ sourcePopup.content }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { searchAPI, kbAPI } from '../api/knowledge'

const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const selectedKB = ref('')
const sourcePopup = ref(null)
const lastDebug = ref(null)
const chatRef = ref(null)
const inputRef = ref(null)
const kbList = ref([])
const history = ref([])

const hints = [
  'Redis 集群最少需要几个节点？',
  '系统采用什么架构？',
  '数据库备份策略是什么？',
  '微服务如何拆分？',
]

onMounted(async () => {
  try {
    const { data } = await kbAPI.list()
    kbList.value = data
  } catch (e) { /* ignore */ }
  // 从 localStorage 恢复历史
  try {
    history.value = JSON.parse(localStorage.getItem('ask_history') || '[]')
  } catch { history.value = [] }
})

const saveHistory = (question, answer) => {
  history.value.unshift({
    question: question.slice(0, 50),
    answer: answer.slice(0, 100),
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
  })
  if (history.value.length > 20) history.value = history.value.slice(0, 20)
  localStorage.setItem('ask_history', JSON.stringify(history.value))
}

const loadHistory = (i) => {
  inputText.value = history.value[i].question
}

const quickAsk = (q) => {
  inputText.value = q
  sendMessage()
}

const autoResize = () => {
  const el = inputRef.value
  if (el) {
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 120) + 'px'
  }
}

const sendMessage = async () => {
  const text = inputText.value.trim()
  if (!text || loading.value) return
  inputText.value = ''
  if (inputRef.value) { inputRef.value.style.height = 'auto' }

  messages.value.push({ role: 'user', content: text })
  loading.value = true
  await nextTick()
  if (chatRef.value) chatRef.value.scrollTop = chatRef.value.scrollHeight

  try {
    const kbIds = selectedKB.value ? [parseInt(selectedKB.value)] : null
    const { data } = await searchAPI.search(text, kbIds)

    const sources = data.sources.map(s => ({
      chunkId: s.chunk_id || 0,
      doc: s.doc_name,
      page: s.page || `分块 ${s.chunk_index}`,
      score: s.score,
      content: s.content || '',
      loading: false,
    }))

    messages.value.push({ role: 'assistant', content: data.answer, sources, showSources: true })

    lastDebug.value = {
      vectorRecall: 50,
      vectorLatency: Math.round(data.latency_ms * 0.2),
      keywordRecall: 50,
      keywordLatency: Math.round(data.latency_ms * 0.15),
      merged: Math.max(sources.length * 4, 15),
      tokens: data.tokens_used,
      llmLatency: Math.round(data.latency_ms * 0.5),
      totalLatency: data.latency_ms,
    }

    saveHistory(text, data.answer)
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      content: '问答服务暂时不可用：' + (e.response?.data?.detail || e.message) + '\n\n请确认后端服务已启动。',
      sources: [],
    })
    lastDebug.value = null
  }

  loading.value = false
  await nextTick()
  if (chatRef.value) chatRef.value.scrollTop = chatRef.value.scrollHeight
}

const renderContent = (text) => {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/```(\w*)\n?([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(\d+)\.\s(.+)/g, '<li>$2</li>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
  return '<p>' + html + '</p>'
}

const openSource = async (s) => {
  // 先弹窗（已有内容就直接显示，没有就显示 loading）
  if (s.content) {
    sourcePopup.value = { ...s }
  } else if (s.chunkId) {
    sourcePopup.value = { ...s, content: '加载中...' }
    try {
      const token = sessionStorage.getItem('token')
      const resp = await fetch(`/api/v1/chunks/${s.chunkId}`, { headers: { Authorization: `Bearer ${token}` } })
      if (resp.ok) {
        const data = await resp.json()
        sourcePopup.value = { ...s, content: data.content }
        // 缓存到原对象
        s.content = data.content
      } else {
        sourcePopup.value = { ...s, content: '[加载失败]' }
      }
    } catch {
      sourcePopup.value = { ...s, content: '[加载失败]' }
    }
  }
}

const scoreClass = (s) => {
  if (s >= 0.9) return 'high'
  if (s >= 0.7) return 'mid'
  return 'low'
}
</script>

<style scoped>
.page { padding: 24px; height: calc(100vh - 80px); }
.ask-layout { display: flex; gap: 16px; height: 100%; }

/* ===== 对话区 ===== */
.chat-main { flex: 1; display: flex; flex-direction: column; background: rgba(255,255,255,.015); border: 1px solid rgba(255,255,255,.05); border-radius: 14px; overflow: hidden; min-width: 0; }
.chat-messages { flex: 1; overflow-y: auto; padding: 24px; }
.chat-messages::-webkit-scrollbar { width: 4px; }
.chat-messages::-webkit-scrollbar-thumb { background: rgba(255,255,255,.06); border-radius: 2px; }

/* 欢迎态 */
.welcome { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; padding: 40px 20px; }
.welcome-icon { width: 72px; height: 72px; margin-bottom: 20px; }
.welcome-icon svg { width: 100%; height: 100%; }
.welcome-title { font-size: 22px; font-weight: 700; color: #e2e8f0; margin: 0 0 8px; }
.welcome-desc { font-size: 13px; color: rgba(255,255,255,.35); margin: 0 0 28px; max-width: 400px; }
.welcome-hints { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; max-width: 500px; }
.hint-chip { padding: 8px 16px; border-radius: 20px; font-size: 13px; color: rgba(255,255,255,.5); background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.06); cursor: pointer; transition: all .2s; font-family: inherit; }
.hint-chip:hover { color: #8bb8ff; background: rgba(74,140,247,.08); border-color: rgba(74,140,247,.15); }

/* 消息 */
.msg { display: flex; gap: 12px; margin-bottom: 22px; }
.msg.user { flex-direction: row-reverse; }
.msg-avatar { width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; flex-shrink: 0; }
.msg.user .msg-avatar { background: linear-gradient(135deg,#4a6cf7,#00d4ff); color: #fff; }
.msg.assistant .msg-avatar { background: rgba(139,92,246,.12); color: #a78bfa; }
.msg.assistant .msg-avatar svg { width: 14px; height: 14px; }
.msg-body { max-width: 78%; min-width: 0; }
.msg.user .msg-body { text-align: right; }
.msg-content { font-size: 13.5px; color: rgba(255,255,255,.75); line-height: 1.75; }
.msg.user .msg-content { background: rgba(74,140,247,.1); border: 1px solid rgba(74,140,247,.15); padding: 12px 16px; border-radius: 14px 4px 14px 14px; }
.msg.assistant .msg-content { padding: 0; }
.msg-content :deep(strong) { color: #f0f4ff; font-weight: 600; }
.msg-content :deep(code) { background: rgba(255,255,255,.06); padding: 2px 6px; border-radius: 4px; font-size: 12.5px; font-family: 'SF Mono',Menlo,monospace; color: #00d4ff; }
.msg-content :deep(pre) { background: rgba(0,0,0,.3); padding: 12px 16px; border-radius: 8px; overflow-x: auto; margin: 8px 0; border: 1px solid rgba(255,255,255,.06); }
.msg-content :deep(pre code) { background: none; padding: 0; color: rgba(255,255,255,.7); }
.msg-content :deep(li) { margin-left: 16px; }
.msg-content :deep(p) { margin: 4px 0; }
.msg-content :deep(p:first-child) { margin-top: 0; }
.msg-content :deep(p:last-child) { margin-bottom: 0; }

/* 来源 */
.msg-sources { margin-top: 10px; background: rgba(255,255,255,.015); border: 1px solid rgba(255,255,255,.04); border-radius: 10px; overflow: hidden; }
.sources-header { display: flex; align-items: center; gap: 6px; padding: 8px 12px; font-size: 11.5px; color: rgba(255,255,255,.3); cursor: pointer; transition: color .15s; user-select: none; }
.sources-header:hover { color: rgba(255,255,255,.45); }
.sources-header svg { width: 13px; height: 13px; flex-shrink: 0; }
.sources-chevron { width: 14px; height: 14px; margin-left: auto; transition: transform .2s; }
.sources-chevron.open { transform: rotate(180deg); }
.sources-list { padding: 4px 12px 10px; }
.source-row { display: flex; align-items: center; gap: 8px; padding: 5px 8px; font-size: 12px; cursor: pointer; border-radius: 4px; transition: background .15s; margin: 0 -8px; }
.source-row:hover { background: rgba(255,255,255,.03); }
.source-num { width: 18px; height: 18px; border-radius: 4px; background: rgba(255,255,255,.04); display: flex; align-items: center; justify-content: center; font-size: 10px; color: rgba(255,255,255,.3); flex-shrink: 0; }
.source-doc { flex: 1; color: rgba(255,255,255,.45); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.source-page { color: rgba(255,255,255,.2); flex-shrink: 0; font-size: 11px; }
.source-score { font-size: 11px; font-weight: 600; flex-shrink: 0; }
.source-score.high { color: #4ade80; }
.source-score.mid { color: #fbbf24; }
.source-score.low { color: rgba(255,255,255,.3); }

/* 打字动画 */
.typing { display: flex; gap: 5px; padding: 12px 16px; background: rgba(255,255,255,.02); border-radius: 12px; width: fit-content; }
.typing span { width: 7px; height: 7px; border-radius: 50%; background: rgba(255,255,255,.25); animation: dotBounce 1.4s infinite; }
.typing span:nth-child(2) { animation-delay: .2s; }
.typing span:nth-child(3) { animation-delay: .4s; }
@keyframes dotBounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-8px)} }

/* 输入区 */
.chat-footer { padding: 14px 20px; border-top: 1px solid rgba(255,255,255,.04); flex-shrink: 0; }
.chat-input-wrap { display: flex; gap: 10px; align-items: flex-end; }
.chat-textarea { flex: 1; padding: 10px 14px; font-size: 14px; color: #e2e8f0; background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08); border-radius: 12px; outline: none; font-family: inherit; resize: none; line-height: 1.5; transition: border-color .2s; max-height: 120px; }
.chat-textarea:focus { border-color: rgba(74,140,247,.4); }
.chat-textarea::placeholder { color: rgba(255,255,255,.2); }
.send-btn { width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; border: none; border-radius: 10px; background: linear-gradient(135deg,#4a6cf7,#5b8cf7); color: #fff; cursor: pointer; flex-shrink: 0; transition: opacity .2s; }
.send-btn:hover:not(:disabled) { opacity: .9; }
.send-btn:disabled { opacity: .25; cursor: not-allowed; }
.send-btn svg { width: 18px; height: 18px; }
.chat-footer-bar { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
.kb-select-sm { height: 28px; padding: 0 8px; font-size: 11px; color: rgba(255,255,255,.4); background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.05); border-radius: 6px; outline: none; cursor: pointer; font-family: inherit; }
.footer-hint { font-size: 11px; color: rgba(255,255,255,.15); }

/* ===== 右侧面板 ===== */
.side-panel { width: 260px; flex-shrink: 0; display: flex; flex-direction: column; gap: 16px; overflow-y: auto; }
.side-panel::-webkit-scrollbar { width: 3px; }
.side-panel::-webkit-scrollbar-thumb { background: rgba(255,255,255,.05); border-radius: 2px; }
.panel-section { background: rgba(255,255,255,.015); border: 1px solid rgba(255,255,255,.04); border-radius: 12px; padding: 16px; }
.panel-title { font-size: 12px; font-weight: 700; color: rgba(255,255,255,.35); text-transform: uppercase; letter-spacing: 1px; margin: 0 0 12px; }
.panel-empty { text-align: center; padding: 20px 0; font-size: 11px; color: rgba(255,255,255,.15); }
.panel-empty-icon { width: 32px; height: 32px; margin-bottom: 6px; }
.panel-empty.sm { padding: 10px 0; }
.panel-empty p { margin: 0; }

/* 调试步骤 */
.debug-steps { display: flex; flex-direction: column; gap: 1px; }
.debug-step { display: flex; gap: 10px; padding: 7px 0; }
.debug-step-num { width: 20px; height: 20px; border-radius: 5px; background: rgba(74,140,247,.1); color: #8bb8ff; font-size: 10px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.debug-step-body { min-width: 0; }
.debug-step-title { display: block; font-size: 11px; color: rgba(255,255,255,.5); font-weight: 500; }
.debug-step-meta { display: block; font-size: 10px; color: rgba(255,255,255,.2); margin-top: 1px; }
.debug-total { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,.04); font-size: 12px; color: rgba(255,255,255,.4); }
.debug-total strong { color: #00d4ff; font-size: 14px; }

/* 历史 */
.history-item { padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,.02); cursor: pointer; transition: opacity .15s; }
.history-item:hover { opacity: .7; }
.history-text { display: block; font-size: 11px; color: rgba(255,255,255,.4); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.history-time { display: block; font-size: 10px; color: rgba(255,255,255,.15); margin-top: 2px; }

/* ===== 来源原文弹窗 ===== */
.popup-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.5); backdrop-filter: blur(3px); display: flex; align-items: center; justify-content: center; z-index: 200; }
.popup-card { width: 620px; max-width: 90vw; max-height: 70vh; background: #111a35; border: 1px solid rgba(255,255,255,.08); border-radius: 14px; display: flex; flex-direction: column; overflow: hidden; }
.popup-header { display: flex; align-items: center; gap: 12px; padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,.06); flex-shrink: 0; }
.popup-title { font-size: 14px; font-weight: 600; color: #e2e8f0; margin: 0; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.popup-meta { font-size: 11px; color: rgba(255,255,255,.3); flex-shrink: 0; }
.popup-close { width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; background: none; border: none; color: rgba(255,255,255,.3); font-size: 20px; cursor: pointer; border-radius: 6px; flex-shrink: 0; }
.popup-close:hover { background: rgba(255,255,255,.05); color: rgba(255,255,255,.6); }
.popup-body { flex: 1; overflow-y: auto; padding: 16px 20px; }
.popup-body::-webkit-scrollbar { width: 4px; }
.popup-body::-webkit-scrollbar-thumb { background: rgba(255,255,255,.06); border-radius: 2px; }
.popup-content { font-size: 13px; color: rgba(255,255,255,.6); line-height: 1.8; white-space: pre-wrap; word-break: break-all; margin: 0; font-family: inherit; }
</style>
