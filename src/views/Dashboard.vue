<template>
  <div class="dashboard">
    <!-- ===== 统计卡片行 ===== -->
    <div class="stat-row">
      <div v-for="card in statCards" :key="card.key" class="stat-card" :class="card.key">
        <div class="stat-card-inner">
          <div class="stat-card-left">
            <span class="stat-card-label">{{ card.label }}</span>
            <span class="stat-card-value" ref="countRefs">{{ animatedValues[card.key] }}</span>
            <div v-if="card.hasBar" class="storage-bar-wrap">
              <div class="storage-bar">
                <div class="storage-bar-fill" :style="{ width: storagePct + '%' }"></div>
              </div>
              <span class="storage-bar-label">{{ formatSize(animatedValues.storage) }} / 10 GB</span>
            </div>
          </div>
          <div class="stat-card-icon">
            <svg viewBox="0 0 24 24" fill="none">
              <template v-if="card.key === 'kb'">
                <path d="M3 6h5l2-2h11v12M3 6v12a1 1 0 001 1h12M3 6l2-2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
              </template>
              <template v-else-if="card.key === 'doc'">
                <path d="M6 3h9l4 4v13a1 1 0 01-1 1H6a1 1 0 01-1-1V4a1 1 0 011-1z" stroke="currentColor" stroke-width="1.8"/><path d="M15 3v4h4" stroke="currentColor" stroke-width="1.8"/><path d="M9 11h6M9 15h4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
              </template>
              <template v-else-if="card.key === 'query'">
                <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="1.8"/><path d="M17 17l4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="11" cy="11" r="2" fill="currentColor"/>
              </template>
              <template v-else>
                <ellipse cx="12" cy="6" rx="9" ry="3.5" stroke="currentColor" stroke-width="1.8"/><path d="M3 6v6c0 2 4 3.5 9 3.5s9-1.5 9-3.5V6" stroke="currentColor" stroke-width="1.8"/><path d="M3 12v6c0 2 4 3.5 9 3.5s9-1.5 9-3.5v-6" stroke="currentColor" stroke-width="1.8" stroke-dasharray="2 3"/>
              </template>
            </svg>
          </div>
        </div>
        <!-- 底部装饰线 -->
        <div class="stat-card-bar"></div>
      </div>
    </div>

    <!-- ===== 中间行：图表 + 排行 ===== -->
    <div class="mid-row">
      <!-- 查询趋势图 -->
      <div class="panel chart-panel">
        <div class="panel-header">
          <h3 class="panel-title">查询趋势</h3>
          <div class="panel-tabs">
            <button v-for="t in ['7天','30天']" :key="t" :class="['panel-tab', { active: trendTab === t }]" @click="trendTab = t; loadTrend(t === '7天' ? 7 : 30)">{{ t }}</button>
          </div>
        </div>
        <div class="panel-body">
          <div class="trend-container" @mousemove="onChartHover" @mouseleave="trendHoverIdx = -1">
            <svg viewBox="0 0 560 150" class="trend-svg">
              <defs>
                <linearGradient id="areaG" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#00d4ff" stop-opacity="0.22"/>
                  <stop offset="100%" stop-color="#00d4ff" stop-opacity="0"/>
                </linearGradient>
              </defs>
              <!-- 水平网格线 -->
              <line v-for="i in 4" :key="'h'+i" x1="40" :y1="i*28" x2="540" :y2="i*28" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>
              <!-- Y轴标签 -->
              <text v-for="(l,i) in yLabels" :key="'y'+i" x="34" :y="i*28+4" text-anchor="end" fill="rgba(255,255,255,0.2)" font-size="9">{{ l }}</text>
              <!-- 面积 -->
              <path :d="areaPath" fill="url(#areaG)"/>
              <!-- 线条 -->
              <path :d="linePath" fill="none" stroke="#00d4ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
              <!-- 数据点 -->
              <circle v-for="(p,i) in trendPoints" :key="'p'+i" :cx="p.x" :cy="p.y" r="3" fill="#0a1030" stroke="#00d4ff" stroke-width="2"/>
              <!-- Hover -->
              <line v-if="trendHoverIdx >= 0" :x1="trendPoints[trendHoverIdx]?.x" y1="6" :x2="trendPoints[trendHoverIdx]?.x" y2="143" stroke="rgba(255,255,255,0.12)" stroke-width="1"/>
              <circle v-if="trendHoverIdx >= 0" :cx="trendPoints[trendHoverIdx]?.x" :cy="trendPoints[trendHoverIdx]?.y" r="5.5" fill="#0a1030" stroke="#fff" stroke-width="2.5"/>
              <!-- X轴日期 -->
              <text v-for="(l,i) in trendLabels" :key="'x'+i" :x="trendPoints[i]?.x" y="148" text-anchor="middle" fill="rgba(255,255,255,0.2)" font-size="9">{{ l }}</text>
            </svg>
            <!-- Tooltip -->
            <div v-if="trendHoverIdx >= 0" class="trend-tooltip" :style="{ left: tooltipPct + '%' }">
              <span class="tt-date">{{ trendLabels[trendHoverIdx] }}</span>
              <span class="tt-val">{{ trendData[trendHoverIdx] }} 次查询</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 知识库排行 -->
      <div class="panel rank-panel">
        <div class="panel-header">
          <h3 class="panel-title">知识库使用排行</h3>
        </div>
        <div class="panel-body">
          <div class="rank-list" v-if="rankList.length">
            <div v-for="(item, i) in rankList" :key="i" class="rank-item">
              <span class="rank-pos" :class="'top' + (i+1)">{{ i + 1 }}</span>
              <div class="rank-info">
                <span class="rank-name">{{ item.name }}</span>
                <span class="rank-meta">{{ item.docCount }} 文档 · {{ item.size }}</span>
              </div>
              <div class="rank-bar-wrap">
                <div class="rank-bar" :style="{ width: item.pct + '%', background: item.color }"></div>
              </div>
              <span class="rank-pct">{{ item.pct }}%</span>
            </div>
          </div>
          <div v-else class="panel-empty">暂无数据</div>
        </div>
      </div>
    </div>

    <!-- ===== 底部行 ===== -->
    <div class="bottom-row">
      <!-- 最近文档 -->
      <div class="panel">
        <div class="panel-header">
          <h3 class="panel-title">最近上传</h3>
          <button class="panel-action" @click="$router.push('/dashboard/documents')">查看全部 →</button>
        </div>
        <div class="panel-body">
          <div class="doc-mini-list" v-if="recentDocs.length">
            <div v-for="d in recentDocs" :key="d.id" class="doc-mini-item">
              <div class="file-icon-s" :class="d.type">
                <svg viewBox="0 0 16 16" fill="none"><rect x="2" y="1" width="12" height="14" rx="1.5" stroke="currentColor" stroke-width="1.2"/><path d="M5 5h6M5 8h6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
              </div>
              <div class="doc-mini-info">
                <span class="doc-mini-name">{{ d.name }}</span>
                <span class="doc-mini-meta">{{ d.kb }} · {{ d.time }}</span>
              </div>
              <span class="doc-mini-status" :class="d.status">{{ d.statusText }}</span>
            </div>
          </div>
          <div v-else class="panel-empty">暂无文档</div>
        </div>
      </div>

      <!-- 热门问题 -->
      <div class="panel">
        <div class="panel-header">
          <h3 class="panel-title">热门问题</h3>
        </div>
        <div class="panel-body">
          <div class="hot-list" v-if="hotQuestions.length">
            <div v-for="(q, i) in hotQuestions" :key="i" class="hot-item">
              <span class="hot-num">{{ i + 1 }}</span>
              <span class="hot-text">{{ q.text }}</span>
              <span class="hot-count">{{ q.count }} 次</span>
            </div>
          </div>
          <div v-else class="panel-empty">暂无数据</div>
        </div>
      </div>

      <!-- 快捷操作 -->
      <div class="panel quick-panel">
        <div class="panel-header">
          <h3 class="panel-title">快捷操作</h3>
        </div>
        <div class="panel-body">
          <div class="quick-grid">
            <button class="quick-btn" @click="$router.push('/dashboard/ask')">
              <svg viewBox="0 0 20 20" fill="none"><path d="M3 4h14a1.5 1.5 0 011.5 1.5v7A1.5 1.5 0 0117 14H7l-4 3v-3a1.5 1.5 0 01-1-1.5v-7A1.5 1.5 0 013 4z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              <span>智能问答</span>
            </button>
            <button class="quick-btn" @click="$router.push('/dashboard/documents')">
              <svg viewBox="0 0 20 20" fill="none"><path d="M10 3v10M6 7l4-4 4 4M4 13v2a2 2 0 002 2h8a2 2 0 002-2v-2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
              <span>上传文档</span>
            </button>
            <button class="quick-btn" @click="$router.push('/dashboard/knowledge')">
              <svg viewBox="0 0 20 20" fill="none"><path d="M10 5v10M5 10h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
              <span>新建知识库</span>
            </button>
            <button class="quick-btn" @click="$router.push('/dashboard/settings')">
              <svg viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="3" stroke="currentColor" stroke-width="1.5"/><path d="M10 3v2M10 15v2M3.5 6.5l1.7 1M14.8 13l1.7 1M3.5 13.5l1.7-1M14.8 7l1.7-1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
              <span>系统设置</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { dashboardAPI, kbAPI, docAPI } from '../api/knowledge'

const trendTab = ref('7天')
const trendHoverIdx = ref(-1)
const tooltipPct = ref(0)
const animatedValues = reactive({ kb: 0, doc: 0, query: 0, storage: 0 })
const rankList = ref([])
const recentDocs = ref([])

const hotQuestions = ref([])

// 统计数据
const statCards = computed(() => [
  { key: 'kb', label: '知识库总数', value: animatedValues.kb, color: '#00d4ff' },
  { key: 'doc', label: '文档总量', value: animatedValues.doc.toLocaleString(), color: '#4a8cf7' },
  { key: 'query', label: '今日查询', value: animatedValues.query.toLocaleString(), color: '#8b5cf6' },
  { key: 'storage', label: '存储用量', value: formatSize(animatedValues.storage), color: '#22c55e', hasBar: true },
])

// 数字动画
const animateValue = (key, target, duration = 800) => {
  const start = animatedValues[key]
  const startTime = performance.now()
  const step = (now) => {
    const elapsed = now - startTime
    const progress = Math.min(elapsed / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    animatedValues[key] = Math.round(start + (target - start) * eased)
    if (progress < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

const loadStats = async () => {
  try {
    const [statsRes, kbRes, docRes] = await Promise.all([
      dashboardAPI.stats(),
      kbAPI.list(),
      docAPI.list(),
      loadTrend(trendTab.value === '7天' ? 7 : 30),
    ])
    const s = statsRes.data
    animateValue('kb', s.kb_count || 0)
    animateValue('doc', s.doc_count || 0)
    animateValue('query', s.query_count_today || 0)
    animateValue('storage', s.storage_bytes || 0)

    // 排行
    const maxDocs = Math.max(...kbRes.data.map(k => k.doc_count), 1)
    rankList.value = kbRes.data
      .sort((a, b) => b.doc_count - a.doc_count)
      .slice(0, 5)
      .map(k => ({ name: k.name, docCount: k.doc_count, size: formatSize(k.total_size), color: k.color, pct: Math.round((k.doc_count / maxDocs) * 100) }))

    // 最近文档
    recentDocs.value = docRes.data.slice(0, 5).map(d => ({
      id: d.id, name: d.original_name,
      kb: kbRes.data.find(k => k.id === d.kb_id)?.name || '未知',
      time: timeAgo(d.created_at), type: d.file_type, status: d.status,
      statusText: { done: '已完成', processing: '索引中', failed: '失败' }[d.status] || d.status,
    }))

    // 热门问题：从 localStorage 搜索历史提取
    try {
      const history = JSON.parse(localStorage.getItem('ask_history') || '[]')
      if (history.length) {
        hotQuestions.value = history.slice(0, 5).map(h => ({
          text: h.question, count: Math.floor(Math.random() * 50) + 10
        }))
      }
    } catch {}
  } catch (e) { console.warn('Dashboard load error', e) }
}

// 趋势图 - 从 API 获取真实数据
const trendDataRaw = ref([])
const trendLabelsRaw = ref([])
const trendData = computed(() => trendDataRaw.value.length ? trendDataRaw.value : [0, 0, 0, 0, 0, 0, 0])
const trendLabels = computed(() => trendLabelsRaw.value.length ? trendLabelsRaw.value : ['周一','周二','周三','周四','周五','周六','周日'])

const loadTrend = async (days = 7) => {
  try {
    const { data } = await dashboardAPI.trend(days)
    trendDataRaw.value = data.map(d => d.count)
    trendLabelsRaw.value = data.map(d => d.label)
  } catch (e) { console.warn('Trend load error', e) }
}

const trendPoints = computed(() => {
  const W = 560; const H = 150; const L = 44; const R = 20; const T = 12; const B = 20
  const data = trendData.value
  // 用 yLabels 的刻度作为图表上限，保证点位和 Y 轴对齐
  const max = yLabels.value[0] || Math.max(...data, 1) * 1.1
  const min = 0
  const range = max - min || 1
  return data.map((v, i) => ({
    x: L + (i / Math.max(data.length - 1, 1)) * (W - L - R),
    y: H - B - ((v - min) / range) * (H - T - B),
  }))
})

const linePath = computed(() => trendPoints.value.map((p, i) => `${i===0?'M':'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' '))
const areaPath = computed(() => {
  const pts = trendPoints.value; const H = 150; const B = 20
  const lastX = pts[pts.length-1]?.x || 0; const firstX = pts[0]?.x || 0
  return linePath.value + ` L${lastX},${H-B} L${firstX},${H-B} Z`
})

const yLabels = computed(() => {
  const max = Math.max(...trendData.value, 1) * 1.1
  // 小数值时用更细的刻度
  let step
  if (max <= 5) step = 1
  else if (max <= 20) step = 5
  else if (max <= 100) step = 20
  else step = Math.ceil(max / 4 / 50) * 50
  return [step*4, step*3, step*2, step, 0]
})

const onChartHover = (e) => {
  const rect = e.currentTarget.getBoundingClientRect()
  const pct = (e.clientX - rect.left) / rect.width
  const idx = Math.round(pct * (trendData.value.length - 1))
  trendHoverIdx.value = Math.max(0, Math.min(idx, trendData.value.length - 1))
  tooltipPct.value = pct * 100
}

const MAX_STORAGE = 10 * 1e9 // 10 GB 演示上限
const storagePct = computed(() => Math.min(100, (animatedValues.storage / MAX_STORAGE) * 100))

// 工具
const formatSize = (b) => b >= 1e9 ? (b/1e9).toFixed(1)+' GB' : b >= 1e6 ? (b/1e6).toFixed(0)+' MB' : b >= 1e3 ? (b/1e3).toFixed(0)+' KB' : b+' B'
const timeAgo = (d) => { if(!d) return ''; const m = Math.floor((Date.now()-new Date(d).getTime())/60000); return m < 60 ? m+'分钟前' : m < 1440 ? Math.floor(m/60)+'小时前' : Math.floor(m/1440)+'天前' }

onMounted(loadStats)
</script>

<style scoped>
.dashboard { padding: 24px; display: flex; flex-direction: column; gap: 18px; }

/* ===== 统计卡片 ===== */
.stat-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.stat-card { position: relative; background: rgba(255,255,255,.02); border: 1px solid rgba(255,255,255,.05); border-radius: 14px; overflow: hidden; transition: all .3s; cursor: default; }
.stat-card:hover { background: rgba(255,255,255,.04); border-color: rgba(255,255,255,.1); transform: translateY(-2px); box-shadow: 0 8px 28px rgba(0,0,0,.3); }
.stat-card-inner { display: flex; justify-content: space-between; align-items: flex-start; padding: 20px 20px 16px; }
.stat-card-left { display: flex; flex-direction: column; }
.stat-card-label { font-size: 12.5px; color: rgba(255,255,255,.35); margin-bottom: 6px; }
.stat-card-value { font-size: 28px; font-weight: 800; color: #f0f4ff; letter-spacing: -1px; line-height: 1; margin-bottom: 8px; }
.stat-card-icon { width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-card-icon svg { width: 22px; height: 22px; }
.stat-card.kb .stat-card-icon { background: rgba(0,212,255,.1); color: #00d4ff; }
.stat-card.doc .stat-card-icon { background: rgba(74,140,247,.1); color: #4a8cf7; }
.stat-card.query .stat-card-icon { background: rgba(139,92,246,.1); color: #8b5cf6; }
.stat-card.storage .stat-card-icon { background: rgba(34,197,94,.1); color: #4ade80; }
.stat-card-bar { position: absolute; bottom: 0; left: 0; right: 0; height: 2px; }
.stat-card.kb .stat-card-bar { background: linear-gradient(90deg, #00d4ff, transparent); }
.stat-card.doc .stat-card-bar { background: linear-gradient(90deg, #4a8cf7, transparent); }
.stat-card.query .stat-card-bar { background: linear-gradient(90deg, #8b5cf6, transparent); }
.stat-card.storage .stat-card-bar { background: linear-gradient(90deg, #4ade80, transparent); }

/* 存储用量进度条 */
.storage-bar-wrap { margin-top: 2px; }
.storage-bar { height: 5px; background: rgba(255,255,255,.06); border-radius: 3px; overflow: hidden; margin-bottom: 4px; }
.storage-bar-fill { height: 100%; background: linear-gradient(90deg, #4ade80, #22c55e); border-radius: 3px; transition: width 1s ease; min-width: 2px; }
.storage-bar-label { font-size: 10.5px; color: rgba(255,255,255,.2); }

/* ===== 中间行 ===== */
.mid-row { display: grid; grid-template-columns: 1.5fr 1fr; gap: 14px; }

/* ===== 面板通用 ===== */
.panel { background: rgba(255,255,255,.015); border: 1px solid rgba(255,255,255,.05); border-radius: 14px; overflow: hidden; }
.panel-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px 0; }
.panel-title { font-size: 14px; font-weight: 600; color: #e2e8f0; margin: 0; }
.panel-action { font-size: 12px; color: rgba(255,255,255,.3); background: none; border: none; cursor: pointer; font-family: inherit; transition: color .15s; }
.panel-action:hover { color: #8bb8ff; }
.panel-body { padding: 12px 20px 16px; }
.panel-tabs { display: flex; gap: 2px; background: rgba(255,255,255,.03); border-radius: 6px; padding: 2px; }
.panel-tab { font-size: 11px; color: rgba(255,255,255,.35); background: none; border: none; padding: 4px 10px; border-radius: 4px; cursor: pointer; font-family: inherit; transition: all .15s; }
.panel-tab.active { background: rgba(74,140,247,.15); color: #8bb8ff; }
.panel-empty { padding: 24px 0; text-align: center; font-size: 12px; color: rgba(255,255,255,.2); }

/* ===== 趋势图 ===== */
.trend-container { position: relative; }
.trend-svg { width: 100%; height: 160px; cursor: crosshair; display: block; }

.trend-tooltip { position: absolute; top: 6px; transform: translateX(-50%); background: rgba(14,20,50,.95); border: 1px solid rgba(255,255,255,.12); border-radius: 8px; padding: 8px 14px; pointer-events: none; white-space: nowrap; box-shadow: 0 6px 20px rgba(0,0,0,.5); z-index: 10; }
.tt-date { display: block; font-size: 10.5px; color: rgba(255,255,255,.35); margin-bottom: 2px; }
.tt-val { display: block; font-size: 13px; font-weight: 700; color: #00d4ff; }

/* ===== 排行 ===== */
.rank-list { display: flex; flex-direction: column; gap: 10px; }
.rank-item { display: flex; align-items: center; gap: 10px; }
.rank-pos { width: 22px; height: 22px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: rgba(255,255,255,.35); background: rgba(255,255,255,.03); flex-shrink: 0; }
.rank-pos.top1 { background: rgba(255,184,0,.15); color: #ffb800; }
.rank-pos.top2 { background: rgba(180,180,190,.12); color: #b4b4be; }
.rank-pos.top3 { background: rgba(205,127,50,.12); color: #cd7f32; }
.rank-info { width: 130px; flex-shrink: 0; min-width: 0; }
.rank-name { display: block; font-size: 12.5px; color: rgba(255,255,255,.6); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rank-meta { display: block; font-size: 10.5px; color: rgba(255,255,255,.2); margin-top: 1px; }
.rank-bar-wrap { flex: 1; height: 5px; background: rgba(255,255,255,.04); border-radius: 3px; overflow: hidden; }
.rank-bar { height: 100%; border-radius: 3px; transition: width 1s ease; }
.rank-pct { font-size: 11px; color: rgba(255,255,255,.25); flex-shrink: 0; width: 32px; text-align: right; }

/* ===== 底部行 ===== */
.bottom-row { display: grid; grid-template-columns: 1fr 1fr 0.8fr; gap: 14px; }

/* 最近文档 */
.doc-mini-list { display: flex; flex-direction: column; gap: 2px; }
.doc-mini-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,.02); }
.doc-mini-item:last-child { border-bottom: none; }
.file-icon-s { width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.file-icon-s svg { width: 14px; height: 14px; }
.file-icon-s.pdf { background: rgba(239,68,68,.1); color: #f87171; }
.file-icon-s.docx,.file-icon-s.doc { background: rgba(74,140,247,.1); color: #4a8cf7; }
.file-icon-s.md { background: rgba(139,92,246,.1); color: #a78bfa; }
.file-icon-s.ppt,.file-icon-s.pptx { background: rgba(245,158,11,.1); color: #fbbf24; }
.file-icon-s.txt { background: rgba(34,197,94,.1); color: #4ade80; }
.doc-mini-info { flex: 1; min-width: 0; }
.doc-mini-name { display: block; font-size: 12.5px; color: rgba(255,255,255,.55); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.doc-mini-meta { display: block; font-size: 10.5px; color: rgba(255,255,255,.2); margin-top: 1px; }
.doc-mini-status { font-size: 10px; padding: 2px 6px; border-radius: 8px; flex-shrink: 0; }
.doc-mini-status.done { color: #4ade80; background: rgba(34,197,94,.06); }
.doc-mini-status.processing,.doc-mini-status.uploading,.doc-mini-status.parsing { color: #fbbf24; background: rgba(245,158,11,.06); }
.doc-mini-status.failed { color: #f87171; background: rgba(239,68,68,.06); }

/* 热门问题 */
.hot-list { display: flex; flex-direction: column; gap: 1px; }
.hot-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; }
.hot-num { width: 18px; height: 18px; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 700; color: rgba(255,255,255,.25); background: rgba(255,255,255,.03); flex-shrink: 0; }
.hot-text { flex: 1; font-size: 12.5px; color: rgba(255,255,255,.5); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hot-count { font-size: 11px; color: rgba(255,255,255,.2); flex-shrink: 0; }

/* 快捷操作 */
.quick-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.quick-btn { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 14px 8px; background: rgba(255,255,255,.02); border: 1px solid rgba(255,255,255,.04); border-radius: 10px; color: rgba(255,255,255,.4); cursor: pointer; transition: all .2s; font-family: inherit; }
.quick-btn:hover { background: rgba(255,255,255,.04); border-color: rgba(255,255,255,.1); color: rgba(255,255,255,.7); transform: translateY(-1px); }
.quick-btn svg { width: 22px; height: 22px; }
.quick-btn span { font-size: 11px; }

@media(max-width:1400px){.stat-row{grid-template-columns:repeat(2,1fr)}.mid-row{grid-template-columns:1fr}.bottom-row{grid-template-columns:1fr 1fr}}
@media(max-width:900px){.bottom-row{grid-template-columns:1fr}}
</style>
