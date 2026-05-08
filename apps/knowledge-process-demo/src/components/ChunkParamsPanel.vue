<template>
  <div class="chunk-params-panel">
    <!-- 模式切换 -->
    <div class="mode-switch">
      <button
        class="mode-btn"
        :class="{ active: !compareMode }"
        @click="$emit('update:compareMode', false)"
      >
        单策略运行
      </button>
      <button
        class="mode-btn"
        :class="{ active: compareMode }"
        @click="$emit('update:compareMode', true)"
      >
        多策略对比
      </button>
    </div>

    <!-- 单策略选择器 -->
    <template v-if="!compareMode">
      <div class="param-group">
        <label class="param-label">分块策略</label>
        <select
          class="param-select"
          :value="strategy"
          @change="$emit('update:strategy', $event.target.value)"
        >
          <option
            v-for="s in strategies"
            :key="s"
            :value="s"
          >
            {{ strategyLabels[s] || s }}
          </option>
        </select>
      </div>
    </template>

    <!-- 多策略对比选择 -->
    <template v-else>
      <div class="param-group">
        <label class="param-label">选择对比策略</label>
        <div class="compare-checkboxes">
          <label
            v-for="s in strategies"
            :key="s"
            class="compare-item"
            :class="{ checked: selectedCompareStrategies.includes(s) }"
          >
            <input
              type="checkbox"
              :checked="selectedCompareStrategies.includes(s)"
              @change="toggleCompareStrategy(s)"
            />
            <span>{{ strategyLabels[s] || s }}</span>
          </label>
        </div>
      </div>
    </template>

    <!-- 公共参数：块大小 -->
    <div class="param-group">
      <label class="param-label">
        块大小 <span class="param-value">{{ params.chunkSize }}</span>
      </label>
      <input
        type="range"
        class="param-slider"
        :value="params.chunkSize"
        min="100"
        max="8000"
        step="100"
        @input="updateParam('chunkSize', +$event.target.value)"
      />
    </div>

    <!-- 公共参数：重叠率（固定长度分块不显示） -->
    <div class="param-group" v-if="strategy !== 'fixed'">
      <label class="param-label">
        重叠率 <span class="param-value">{{ formatPercent(params.overlapRatio) }}</span>
      </label>
      <input
        type="range"
        class="param-slider"
        :value="params.overlapRatio ?? 0"
        min="0"
        max="0.4"
        step="0.05"
        @input="updateParam('overlapRatio', +$event.target.value)"
      />
    </div>

    <!-- 递归分块专属：段落深度 -->
    <div class="param-group" v-if="strategy === 'recursive' && !compareMode">
      <label class="param-label">
        段落深度 <span class="param-value">{{ params.paragraphChunkDeep }}</span>
      </label>
      <input
        type="range"
        class="param-slider"
        :value="params.paragraphChunkDeep"
        min="1"
        max="5"
        step="1"
        @input="updateParam('paragraphChunkDeep', +$event.target.value)"
      />
    </div>

    <!-- 结构分块专属：结构类型 -->
    <div class="param-group" v-if="strategy === 'structure' && !compareMode">
      <label class="param-label">结构类型</label>
      <select
        class="param-select"
        :value="params.structureType || 'markdown'"
        @change="updateParam('structureType', $event.target.value)"
      >
        <option value="markdown">Markdown 标题</option>
        <option value="html">HTML 标签</option>
      </select>
    </div>

    <!-- 语义分块专属：相似度阈值 -->
    <div class="param-group" v-if="strategy === 'semantic' && !compareMode">
      <label class="param-label">
        相似度阈值 <span class="param-value">{{ params.semanticThreshold }}</span>
      </label>
      <input
        type="range"
        class="param-slider"
        :value="params.semanticThreshold ?? 0.5"
        min="0.1"
        max="0.9"
        step="0.05"
        @input="updateParam('semanticThreshold', +$event.target.value)"
      />
      <div class="param-hint">
        相邻句子相似度低于此值时产生新块；使用 Embedding 模型时建议 0.70~0.85，值越大切分越细。
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-group">
      <button
        class="action-btn primary"
        :disabled="loading"
        @click="handleRun"
      >
        <span v-if="loading" class="spinner-inline"></span>
        <span v-else>▶</span>
        {{ compareMode ? '执行对比' : '执行分块' }}
      </button>
      <button
        class="action-btn secondary"
        @click="$emit('reset')"
      >
        重置参数
      </button>
    </div>

    <!-- 策略简介 -->
    <div class="strategy-desc">
      <div class="desc-title">{{ strategyLabels[strategy] || strategy }}</div>
      <div class="desc-text">{{ descMap[strategy] || '' }}</div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  strategy: { type: String, default: 'recursive' },
  params: { type: Object, default: () => ({}) },
  strategies: { type: Array, default: () => [] },
  strategyLabels: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  compareMode: { type: Boolean, default: false },
  selectedCompareStrategies: { type: Array, default: () => [] }
})

const emit = defineEmits([
  'update:strategy',
  'update:params',
  'update:compareMode',
  'update:selectedCompareStrategies',
  'run',
  'runCompare',
  'reset'
])

const descMap = {
  recursive: '多级优先级递归下降：依次尝试 Markdown 标题 → 段落 → 标点 → 固定长度，保留语义完整性。',
  fixed: '按固定字符数顺序硬切，无重叠，速度最快，但不保证语义边界。',
  sliding_window: '滑动窗口切分，相邻块之间按设定比例重叠，兼顾边界上下文连续性。',
  structure: '基于文档结构切分：Markdown 按 # 标题层级，HTML 按 h1-h6 / section 标签，保留层级上下文。',
  semantic: '基于本地 Ollama Embedding 模型（默认 qwen3-embedding:4b）计算句子语义相似度，在话题转换处切分；模型不可用时自动降级到 TF-IDF / Jaccard。'
}

function updateParam(key, value) {
  emit('update:params', { ...props.params, [key]: value })
}

function formatPercent(v) {
  if (v === undefined || v === null) return '0%'
  return `${(v * 100).toFixed(0)}%`
}

function toggleCompareStrategy(s) {
  const list = [...props.selectedCompareStrategies]
  const idx = list.indexOf(s)
  if (idx >= 0) {
    list.splice(idx, 1)
  } else {
    list.push(s)
  }
  emit('update:selectedCompareStrategies', list)
}

function handleRun() {
  if (props.compareMode) {
    emit('runCompare')
  } else {
    emit('run')
  }
}
</script>

<style scoped>
.chunk-params-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* 模式切换 */
.mode-switch {
  display: flex;
  gap: 6px;
  padding: 4px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
}

.mode-btn {
  flex: 1;
  padding: 8px 0;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.8rem;
  font-family: var(--font-body);
  cursor: pointer;
  transition: all 0.25s ease;
}

.mode-btn.active {
  background: rgba(6, 182, 212, 0.12);
  color: var(--accent-cyan);
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(6, 182, 212, 0.08);
}

/* 参数组 */
.param-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.param-label {
  font-size: 0.82rem;
  color: var(--text-secondary);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.param-value {
  color: var(--accent-cyan);
  font-family: var(--font-mono);
  font-weight: 500;
  font-size: 0.8rem;
}

.param-select {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 8px 10px;
  color: var(--text-primary);
  font-size: 0.82rem;
  font-family: var(--font-body);
  outline: none;
  transition: border-color 0.2s ease;
}

.param-select:focus {
  border-color: var(--accent-cyan);
}

.param-slider {
  width: 100%;
  accent-color: var(--accent-cyan);
  height: 4px;
  cursor: pointer;
}

.param-hint {
  font-size: 0.72rem;
  color: var(--text-muted);
  line-height: 1.5;
  padding: 4px 6px;
  background: rgba(6, 182, 212, 0.04);
  border-radius: 6px;
  border-left: 2px solid var(--accent-cyan);
}

/* 对比多选 */
.compare-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.compare-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 6px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.compare-item:hover {
  background: var(--bg-primary);
}

.compare-item.checked {
  background: rgba(6, 182, 212, 0.08);
  border-color: rgba(6, 182, 212, 0.2);
  color: var(--accent-cyan);
}

.compare-item input[type="checkbox"] {
  accent-color: var(--accent-cyan);
  width: 14px;
  height: 14px;
  cursor: pointer;
}

/* 操作按钮 */
.action-group {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 14px;
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  font-family: var(--font-body);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
}

.action-btn.primary {
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
  color: #fff;
}

.action-btn.primary:hover:not(:disabled) {
  opacity: 0.92;
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(6, 182, 212, 0.25);
}

.action-btn.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  filter: grayscale(0.3);
}

.action-btn.secondary {
  background: var(--bg-primary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.action-btn.secondary:hover {
  border-color: var(--accent-cyan);
  color: var(--accent-cyan);
}

.spinner-inline {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 策略简介 */
.strategy-desc {
  margin-top: 6px;
  padding: 10px 12px;
  background: rgba(6, 182, 212, 0.04);
  border-radius: 8px;
  border-left: 3px solid var(--accent-cyan);
  line-height: 1.6;
}

.desc-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.desc-text {
  font-size: 0.78rem;
  color: var(--text-secondary);
}
</style>
