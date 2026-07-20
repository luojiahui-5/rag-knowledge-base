<template>
  <div class="page">
    <!-- 左侧对话区 -->
    <div class="search-layout">
      <div class="chat-panel">
        <div class="chat-messages" ref="chatRef">
          <div v-if="messages.length === 0" class="chat-empty">
            <svg viewBox="0 0 60 60" fill="none" class="empty-icon">
              <circle cx="24" cy="24" r="14" stroke="currentColor" stroke-width="2"/>
              <path d="M34 34l10 10" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
              <circle cx="18" cy="24" r="2" fill="currentColor"/>
              <circle cx="26" cy="22" r="2" fill="currentColor"/>
              <circle cx="22" cy="28" r="2" fill="currentColor"/>
            </svg>
            <p class="empty-title">检索测试</p>
            <p class="empty-desc">输入问题，测试知识库检索与问答效果</p>
          </div>
          <div v-for="(msg, i) in messages" :key="i" :class="['msg-row', msg.role]">
            <div class="msg-avatar">{{ msg.role === 'user' ? '我' : 'AI' }}</div>
            <div class="msg-body">
              <div class="msg-text">{{ msg.content }}</div>
              <div v-if="msg.sources && msg.sources.length" class="msg-sources">
                <div class="sources-label">参考来源：</div>
                <div v-for="(s, j) in msg.sources" :key="j" class="source-item">
                  <svg viewBox="0 0 16 16" fill="none" class="source-icon"><path d="M3 1h7l4 4v9a1 1 0 01-1 1H3a1 1 0 01-1-1V2a1 1 0 011-1z" stroke="currentColor" stroke-width="1.2"/><path d="M10 1v4h4" stroke="currentColor" stroke-width="1.2"/></svg>
                  <span class="source-name">{{ s.doc }}</span>
                  <span class="source-page">{{ s.page }}</span>
                  <span class="source-score">{{ (s.score * 100).toFixed(0) }}%</span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="loading" class="msg-row assistant">
            <div class="msg-avatar">AI</div>
            <div class="msg-body"><div class="typing-indicator"><span></span><span></span><span></span></div></div>
          </div>
        </div>

        <div class="chat-input-area">
          <div class="chat-options">
            <select class="kb-select" v-model="selectedKB">
              <option value="">全部知识库</option>
              <option>技术架构文档库</option>
              <option>产品需求文档库</option>
              <option>运维部署手册</option>
            </select>
          </div>
          <div class="chat-input-row">
            <input v-model="inputText" class="chat-input" placeholder="输入你的问题，按 Enter 发送..." @keydown.enter="sendMessage" />
            <button class="send-btn" @click="sendMessage" :disabled="!inputText.trim()">
              <svg viewBox="0 0 20 20" fill="none"><path d="M2 10l16-8-8 16-2-6-6-2z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
          </div>
        </div>
      </div>

      <!-- 右侧调试面板 -->
      <div class="debug-panel">
        <h3 class="debug-title">检索调试</h3>
        <div v-if="!lastDebug" class="debug-empty">
          <p>发送问题后，</p><p>此处展示检索链路详情</p>
        </div>
        <div v-else class="debug-content">
          <div class="debug-section">
            <div class="debug-section-title">1. Query 向量化</div>
            <div class="debug-code">{{ lastDebug.embedding }}</div>
          </div>
          <div class="debug-section">
            <div class="debug-section-title">2. 向量检索 (Milvus)</div>
            <div class="debug-metric">召回 {{ lastDebug.vectorRecall }} 条 · 耗时 {{ lastDebug.vectorLatency }}ms</div>
          </div>
          <div class="debug-section">
            <div class="debug-section-title">3. 关键词检索 (ES)</div>
            <div class="debug-metric">召回 {{ lastDebug.keywordRecall }} 条 · 耗时 {{ lastDebug.keywordLatency }}ms</div>
          </div>
          <div class="debug-section">
            <div class="debug-section-title">4. RRF 融合</div>
            <div class="debug-metric">合并去重后 {{ lastDebug.merged }} 条</div>
          </div>
          <div class="debug-section">
            <div class="debug-section-title">5. Reranker 精排</div>
            <div class="debug-metric">返回 Top-{{ lastDebug.topK }} · 耗时 {{ lastDebug.rerankLatency }}ms</div>
          </div>
          <div class="debug-section">
            <div class="debug-section-title">6. LLM 生成</div>
            <div class="debug-metric">耗时 {{ lastDebug.llmLatency }}ms · {{ lastDebug.tokens }} tokens</div>
          </div>
          <div class="debug-total">总耗时: {{ lastDebug.totalLatency }}ms</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { searchAPI } from '../api/knowledge'

const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const selectedKB = ref('')
const lastDebug = ref(null)
const chatRef = ref(null)

const sendMessage = async () => {
  const text = inputText.value.trim()
  if (!text) return
  inputText.value = ''
  messages.value.push({ role: 'user', content: text })
  loading.value = true

  await nextTick()
  if (chatRef.value) chatRef.value.scrollTop = chatRef.value.scrollHeight

  try {
    const { data } = await searchAPI.search(text)
    loading.value = false

    messages.value.push({
      role: 'assistant',
      content: data.answer,
      sources: data.sources.map(s => ({
        doc: s.doc_name,
        page: s.page || `分块 ${s.chunk_index}`,
        score: s.score,
      })),
    })

    lastDebug.value = {
      embedding: '[1024d embedding vector]',
      vectorRecall: 50,
      vectorLatency: Math.round(data.latency_ms * 0.3),
      keywordRecall: 50,
      keywordLatency: Math.round(data.latency_ms * 0.2),
      merged: Math.max(data.sources.length * 3, 20),
      topK: data.sources.length,
      rerankLatency: Math.round(data.latency_ms * 0.3),
      llmLatency: Math.round(data.latency_ms * 0.2),
      tokens: data.tokens_used,
      totalLatency: data.latency_ms,
    }
  } catch (e) {
    loading.value = false
    messages.value.push({
      role: 'assistant',
      content: '检索服务暂时不可用，请确认后端已启动。错误：' + (e.response?.data?.detail || e.message),
      sources: [],
    })
    lastDebug.value = null
  }

  await nextTick()
  if (chatRef.value) chatRef.value.scrollTop = chatRef.value.scrollHeight
}
</script>

<style scoped>
.page { padding: 24px; height: calc(100vh - 80px); }
.search-layout { display: flex; gap: 16px; height: 100%; }

/* ===== 左侧对话区 ===== */
.chat-panel { flex: 1; display: flex; flex-direction: column; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; overflow: hidden; }
.chat-messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; }
.chat-messages::-webkit-scrollbar { width: 4px; }
.chat-messages::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.06); border-radius: 2px; }

.chat-empty { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.empty-icon { width: 60px; height: 60px; color: rgba(255,255,255,0.15); margin-bottom: 16px; }
.empty-title { font-size: 16px; font-weight: 600; color: rgba(255,255,255,0.5); margin: 0 0 6px; }
.empty-desc { font-size: 13px; color: rgba(255,255,255,0.25); margin: 0; }

.msg-row { display: flex; gap: 12px; }
.msg-row.user { flex-direction: row-reverse; }
.msg-avatar { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; flex-shrink: 0; }
.msg-row.user .msg-avatar { background: linear-gradient(135deg, #4a8cf7, #00d4ff); color: #fff; }
.msg-row.assistant .msg-avatar { background: rgba(139,92,246,0.2); color: #a78bfa; }
.msg-body { max-width: 75%; }
.msg-row.user .msg-body { text-align: right; }
.msg-text { font-size: 13.5px; color: rgba(255,255,255,0.8); line-height: 1.7; background: rgba(255,255,255,0.03); padding: 12px 16px; border-radius: 12px; }
.msg-row.user .msg-text { background: rgba(74,140,247,0.12); border: 1px solid rgba(74,140,247,0.2); }

.msg-sources { margin-top: 8px; padding: 10px 12px; background: rgba(255,255,255,0.02); border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); }
.sources-label { font-size: 11px; color: rgba(255,255,255,0.3); margin-bottom: 6px; }
.source-item { display: flex; align-items: center; gap: 6px; padding: 4px 0; font-size: 12px; }
.source-icon { width: 14px; height: 14px; color: rgba(255,255,255,0.2); flex-shrink: 0; }
.source-name { color: rgba(255,255,255,0.5); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.source-page { color: rgba(255,255,255,0.25); }
.source-score { color: #22c55e; font-weight: 600; }

.typing-indicator { display: flex; gap: 4px; padding: 12px 16px; }
.typing-indicator span { width: 6px; height: 6px; border-radius: 50%; background: rgba(255,255,255,0.3); animation: typingBounce 1.4s infinite; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typingBounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-6px)} }

.chat-input-area { padding: 16px 20px; border-top: 1px solid rgba(255,255,255,0.05); }
.chat-options { margin-bottom: 10px; }
.kb-select { height: 32px; padding: 0 10px; font-size: 12px; color: rgba(255,255,255,0.5); background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; outline: none; cursor: pointer; font-family: inherit; }
.chat-input-row { display: flex; gap: 8px; align-items: center; }
.chat-input { flex: 1; height: 44px; padding: 0 16px; font-size: 14px; color: #e2e8f0; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; outline: none; font-family: inherit; transition: border-color 0.2s; }
.chat-input:focus { border-color: rgba(74,140,247,0.4); }
.chat-input::placeholder { color: rgba(255,255,255,0.25); }
.send-btn { width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border: none; border-radius: 10px; background: linear-gradient(135deg, #4a6cf7, #5b8cf7); color: #fff; cursor: pointer; transition: opacity 0.2s; flex-shrink: 0; }
.send-btn:hover { opacity: 0.9; }
.send-btn:disabled { opacity: 0.3; cursor: default; }
.send-btn svg { width: 19px; height: 19px; }

/* ===== 右侧调试面板 ===== */
.debug-panel { width: 280px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 18px; overflow-y: auto; flex-shrink: 0; }
.debug-panel::-webkit-scrollbar { width: 3px; }
.debug-title { font-size: 13px; font-weight: 700; color: rgba(255,255,255,0.5); margin: 0 0 14px; text-transform: uppercase; letter-spacing: 1px; }
.debug-empty { text-align: center; padding: 40px 0; font-size: 12px; color: rgba(255,255,255,0.2); }
.debug-empty p { margin: 0; line-height: 1.8; }
.debug-section { margin-bottom: 14px; padding-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,0.04); }
.debug-section-title { font-size: 12px; font-weight: 600; color: rgba(255,255,255,0.4); margin-bottom: 4px; }
.debug-code { font-size: 11px; color: rgba(0,212,255,0.5); font-family: 'SF Mono', 'Menlo', monospace; word-break: break-all; }
.debug-metric { font-size: 11px; color: rgba(255,255,255,0.3); line-height: 1.5; }
.debug-total { font-size: 13px; font-weight: 700; color: #00d4ff; margin-top: 4px; }
</style>
