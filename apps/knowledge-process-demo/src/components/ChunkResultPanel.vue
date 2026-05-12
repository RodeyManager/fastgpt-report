<template>
  <div class="chunk-result-panel">
    <!-- 单结果模式 -->
    <template v-if="!compareMode">
      <div v-if="result && result.chunks && result.chunks.length > 0">
        <!-- 统计条 -->
        <div class="stats-bar">
          <div class="stat-cell">
            <span class="stat-num">{{ result.chunks.length }}</span>
            <span class="stat-label">分块数量</span>
          </div>
          <div class="stat-cell">
            <span class="stat-num">{{ avgChunkSize(result.chunks) }}</span>
            <span class="stat-label">平均大小</span>
          </div>
          <div class="stat-cell">
            <span class="stat-num">{{ result.chars }}</span>
            <span class="stat-label">总字符数</span>
          </div>
          <div class="stat-cell">
            <span class="stat-num">{{ formatDuration(result.duration_ms) }}</span>
            <span class="stat-label">耗时</span>
          </div>
          <div class="stat-cell strategy-badge">
            <span class="stat-num" style="font-size:0.78rem">{{ strategyLabels[result.strategy] || result.strategy }}</span>
            <span class="stat-label">当前算法</span>
          </div>
        </div>

        <!-- 分块大小分布图 -->
        <div class="distribution-bar">
          <div
            v-for="(chunk, idx) in result.chunks"
            :key="idx"
            class="dist-segment"
            :style="segmentStyle(chunk, result.chunks)"
            :title="`Chunk #${idx + 1}: ${chunk.length} 字符`"
          ></div>
        </div>

        <!-- Chunk 卡片流 -->
        <div class="chunk-list">
          <div
            v-for="(chunk, idx) in result.chunks"
            :key="idx"
            class="chunk-card"
            :class="{ expanded: expandedSet.has(idx) }"
          >
            <div class="chunk-card-header" @click="toggleExpand(idx)">
              <div class="chunk-meta">
                <span class="chunk-index">Chunk #{{ idx + 1 }}</span>
                <span class="chunk-size">{{ chunk.length }} 字符</span>
              </div>
              <div class="chunk-actions">
                <span v-if="idx < result.chunks.length - 1" class="chunk-overlap">
                  与下块重叠 {{ computeOverlap(chunk, result.chunks[idx + 1]) }} 字符
                </span>
                <span class="expand-icon">{{ expandedSet.has(idx) ? '▾' : '▸' }}</span>
              </div>
            </div>
            <div class="chunk-card-body">
              <pre class="chunk-text">{{ chunk }}</pre>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        点击「执行分块」查看结果
      </div>
    </template>

    <!-- 对比模式 -->
    <template v-else>
      <div v-if="hasCompareResults">
        <!-- 对比 Tab 栏 -->
        <div class="compare-tabs">
          <button
            v-for="s in compareStrategyList"
            :key="s"
            class="compare-tab"
            :class="{ active: activeCompareStrategy === s }"
            @click="$emit('update:activeCompareStrategy', s)"
          >
            <span class="tab-name">{{ strategyLabels[s] || s }}</span>
            <span class="tab-count">{{ resultsMap[s]?.chunks?.length || 0 }} 块</span>
          </button>
        </div>

        <!-- 对比概览表 -->
        <div class="compare-overview">
          <div class="overview-header">
            <span>算法</span>
            <span>块数</span>
            <span>平均大小</span>
            <span>总字符</span>
            <span>耗时</span>
          </div>
          <div
            v-for="s in compareStrategyList"
            :key="s"
            class="overview-row"
            :class="{ highlight: activeCompareStrategy === s }"
          >
            <span>{{ strategyLabels[s] || s }}</span>
            <span>{{ resultsMap[s]?.chunks?.length || 0 }}</span>
            <span>{{ avgChunkSize(resultsMap[s]?.chunks || []) }}</span>
            <span>{{ resultsMap[s]?.chars || 0 }}</span>
            <span>{{ formatDuration(resultsMap[s]?.duration_ms) }}</span>
          </div>
        </div>

        <!-- 当前选中策略的详细结果 -->
        <div class="compare-detail" v-if="activeResult">
          <div class="stats-bar compact">
            <div class="stat-cell">
              <span class="stat-num">{{ activeResult.chunks.length }}</span>
              <span class="stat-label">分块数量</span>
            </div>
            <div class="stat-cell">
              <span class="stat-num">{{ avgChunkSize(activeResult.chunks) }}</span>
              <span class="stat-label">平均大小</span>
            </div>
            <div class="stat-cell">
              <span class="stat-num">{{ activeResult.chars }}</span>
              <span class="stat-label">总字符数</span>
            </div>
            <div class="stat-cell">
              <span class="stat-num">{{ formatDuration(activeResult.duration_ms) }}</span>
              <span class="stat-label">耗时</span>
            </div>
          </div>

          <div class="distribution-bar">
            <div
              v-for="(chunk, idx) in activeResult.chunks"
              :key="idx"
              class="dist-segment"
              :style="segmentStyle(chunk, activeResult.chunks)"
              :title="`Chunk #${idx + 1}: ${chunk.length} 字符`"
            ></div>
          </div>

          <div class="chunk-list">
            <div
              v-for="(chunk, idx) in activeResult.chunks"
              :key="idx"
              class="chunk-card"
              :class="{ expanded: expandedSet.has(idx) }"
            >
              <div class="chunk-card-header" @click="toggleExpand(idx)">
                <div class="chunk-meta">
                  <span class="chunk-index">Chunk #{{ idx + 1 }}</span>
                  <span class="chunk-size">{{ chunk.length }} 字符</span>
                </div>
                <div class="chunk-actions">
                  <span v-if="idx < activeResult.chunks.length - 1" class="chunk-overlap">
                    与下块重叠 {{ computeOverlap(chunk, activeResult.chunks[idx + 1]) }} 字符
                  </span>
                  <span class="expand-icon">{{ expandedSet.has(idx) ? '▾' : '▸' }}</span>
                </div>
              </div>
              <div class="chunk-card-body">
                <pre class="chunk-text">{{ chunk }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        请先选择至少两种策略并点击「执行对比」
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  result: { type: Object, default: null },
  resultsMap: { type: Object, default: () => ({}) },
  compareMode: { type: Boolean, default: false },
  strategyLabels: { type: Object, default: () => ({}) },
  activeCompareStrategy: { type: String, default: '' }
})

const emit = defineEmits(['update:activeCompareStrategy'])

const expandedSet = ref(new Set())

const hasCompareResults = computed(() => {
  return Object.keys(props.resultsMap).length > 0
})

const compareStrategyList = computed(() => {
  return Object.keys(props.resultsMap)
})

const activeResult = computed(() => {
  return props.resultsMap[props.activeCompareStrategy] || null
})

function avgChunkSize(chunks) {
  if (!chunks || chunks.length === 0) return 0
  return Math.round(chunks.reduce((s, c) => s + c.length, 0) / chunks.length)
}

function formatDuration(ms) {
  if (ms === undefined || ms === null) return '-'
  if (ms < 1000) return `${ms.toFixed(1)}ms`
  return `${(ms / 1000).toFixed(2)}s`
}

function toggleExpand(idx) {
  const next = new Set(expandedSet.value)
  if (next.has(idx)) {
    next.delete(idx)
  } else {
    next.add(idx)
  }
  expandedSet.value = next
}

function computeOverlap(a, b) {
  if (!a || !b) return 0
  // 简单计算：从 a 尾部和 b 头部找最长公共子串（限制在 200 字符内）
  const limit = 200
  const tail = a.slice(-limit)
  const head = b.slice(0, limit)
  let max = 0
  for (let i = Math.min(tail.length, head.length); i > 0; i--) {
    if (tail.slice(-i) === head.slice(0, i)) {
      max = i
      break
    }
  }
  return max
}

function segmentStyle(chunk, allChunks) {
  if (!allChunks || allChunks.length === 0) return {}
  const maxLen = Math.max(...allChunks.map(c => c.length))
  const minLen = Math.min(...allChunks.map(c => c.length))
  const ratio = maxLen === minLen ? 0.5 : (chunk.length - minLen) / (maxLen - minLen)
  // 根据长度映射颜色深度：短=青色，长=蓝紫色
  const hue = 180 + ratio * 60 // 180(cyan) ~ 240(blue)
  const alpha = 0.4 + ratio * 0.5
  return {
    flex: `${chunk.length}`,
    background: `hsla(${hue}, 80%, 60%, ${alpha})`
  }
}
</script>

<style scoped>
.chunk-result-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* 统计条 */
.stats-bar {
  display: flex;
  gap: 12px;
  padding: 12px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  flex-wrap: wrap;
}

.stats-bar.compact {
  padding: 10px 12px;
  gap: 10px;
}

.stat-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  min-width: 60px;
}

.stat-num {
  font-family: var(--font-mono);
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--accent-cyan);
}

.stat-label {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.strategy-badge {
  margin-left: auto;
  padding-left: 12px;
  border-left: 1px solid var(--border-color);
  align-items: flex-end;
}

/* 长度分布图 */
.distribution-bar {
  display: flex;
  height: 10px;
  border-radius: 5px;
  overflow: hidden;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
}

.dist-segment {
  min-width: 2px;
  transition: opacity 0.2s ease;
}

.dist-segment:hover {
  opacity: 0.8;
}

/* Chunk 卡片 */
.chunk-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chunk-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  overflow: hidden;
  transition: border-color 0.25s ease, box-shadow 0.25s ease;
}

.chunk-card:hover {
  border-color: rgba(6, 182, 212, 0.35);
  box-shadow: 0 0 16px rgba(6, 182, 212, 0.06);
}

.chunk-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--bg-tertiary);
  cursor: pointer;
  user-select: none;
}

.chunk-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chunk-index {
  font-size: 0.78rem;
  color: var(--accent-cyan);
  font-weight: 500;
  font-family: var(--font-mono);
}

.chunk-size {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}

.chunk-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chunk-overlap {
  font-size: 0.72rem;
  color: var(--text-muted);
  background: rgba(99, 102, 241, 0.08);
  padding: 2px 8px;
  border-radius: 4px;
}

.expand-icon {
  font-size: 0.7rem;
  color: var(--text-muted);
  transition: color 0.2s ease;
}

.chunk-card-header:hover .expand-icon {
  color: var(--accent-cyan);
}

.chunk-card-body {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.chunk-card.expanded .chunk-card-body {
  max-height: 600px;
  overflow-y: auto;
}

.chunk-text {
  margin: 0;
  padding: 10px 12px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  line-height: 1.65;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-all;
}

/* 对比 Tab */
.compare-tabs {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.compare-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-muted);
  font-size: 0.8rem;
  font-family: var(--font-body);
  cursor: pointer;
  transition: all 0.2s ease;
}

.compare-tab.active {
  background: rgba(6, 182, 212, 0.1);
  border-color: var(--accent-cyan);
  color: var(--accent-cyan);
  font-weight: 500;
}

.tab-count {
  font-size: 0.7rem;
  color: var(--text-muted);
  background: var(--bg-primary);
  padding: 1px 6px;
  border-radius: 4px;
}

.compare-tab.active .tab-count {
  color: var(--accent-cyan);
}

/* 对比概览表 */
.compare-overview {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  overflow: hidden;
}

.overview-header,
.overview-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
  gap: 8px;
  padding: 8px 12px;
  font-size: 0.78rem;
  align-items: center;
}

.overview-header {
  background: var(--bg-tertiary);
  color: var(--text-muted);
  font-weight: 500;
}

.overview-row {
  color: var(--text-secondary);
  border-top: 1px solid var(--border-color);
  transition: background 0.2s ease;
}

.overview-row.highlight {
  background: rgba(6, 182, 212, 0.06);
}

.overview-row span:first-child {
  color: var(--text-primary);
  font-weight: 500;
}

/* 空状态 */
.empty-state {
  padding: 40px 16px;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.85rem;
  line-height: 1.6;
  background: var(--bg-secondary);
  border: 1px dashed var(--border-color);
  border-radius: 12px;
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-bar {
    gap: 10px;
  }
  .overview-header,
  .overview-row {
    grid-template-columns: 2fr 1fr 1fr;
    gap: 6px;
  }
  .overview-header span:nth-child(4),
  .overview-header span:nth-child(5),
  .overview-row span:nth-child(4),
  .overview-row span:nth-child(5) {
    display: none;
  }
}
</style>
