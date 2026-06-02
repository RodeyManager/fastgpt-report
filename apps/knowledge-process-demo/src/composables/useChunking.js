import { ref, computed } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

/**
 * 各分块策略的默认参数配置
 */
const DEFAULT_PARAMS = {
  recursive: {
    chunkSize: 500,
    overlapRatio: 0.2,
    paragraphChunkDeep: 2
  },
  fixed: {
    chunkSize: 500
  },
  sliding_window: {
    chunkSize: 500,
    overlapRatio: 0.2
  },
  structure: {
    chunkSize: 500,
    structureType: 'markdown'
  },
  semantic: {
    chunkSize: 500,
    semanticThreshold: 0.75,
    overlapRatio: 0.0
  }
}

/**
 * useChunking —— 分块状态管理与 API 调用封装
 *
 * 提供单策略运行、多策略对比、结果缓存、错误处理等能力。
 */
export function useChunking() {
  // 当前选中的策略（单策略模式）
  const strategy = ref('recursive')

  // 参数对象：按策略名存储，避免切换时丢失已调参数
  const params = ref({
    recursive: { ...DEFAULT_PARAMS.recursive },
    fixed: { ...DEFAULT_PARAMS.fixed },
    sliding_window: { ...DEFAULT_PARAMS.sliding_window },
    structure: { ...DEFAULT_PARAMS.structure },
    semantic: { ...DEFAULT_PARAMS.semantic }
  })

  // 结果缓存：key = 策略名，value = { chunks, chars, strategy, duration_ms }
  const results = ref(new Map())

  // 可用策略列表（从后端拉取）
  const strategies = ref([])

  const loading = ref(false)
  const error = ref('')

  // 当前策略的最近一次结果
  const currentResult = computed(() => {
    return results.value.get(strategy.value) || null
  })

  // 当前策略对应的参数（用于 v-model 绑定）
  const currentParams = computed({
    get() {
      return params.value[strategy.value] || {}
    },
    set(val) {
      // 直接替换整个 params.value，确保 Vue 响应式系统能正确检测到深层变化
      params.value = {
        ...params.value,
        [strategy.value]: { ...params.value[strategy.value], ...val }
      }
    }
  })

  /**
   * 获取后端支持的所有策略列表
   */
  async function fetchStrategies() {
    try {
      const res = await fetch(`${API_BASE}/api/chunk-strategies`)
      if (!res.ok) throw new Error('获取策略列表失败')
      const data = await res.json()
      strategies.value = data.strategies || []
    } catch (err) {
      console.error('[useChunking] fetchStrategies error:', err)
      // 兜底：若后端接口尚未部署，使用硬编码列表
      strategies.value = Object.keys(DEFAULT_PARAMS)
    }
  }

  /**
   * 对指定文本执行单策略分块
   * @param {string} text 待分块文本
   * @param {string} [targetStrategy] 目标策略，默认使用 strategy.value
   */
  async function runChunk(text, targetStrategy = null) {
    const s = targetStrategy || strategy.value
    if (!text) {
      error.value = '待分块文本为空'
      return
    }

    loading.value = true
    error.value = ''

    try {
      const p = params.value[s] || {}
      const body = {
        text,
        strategy: s,
        chunk_size: p.chunkSize ?? 500,
        overlap_ratio: p.overlapRatio ?? 0.0,
        paragraph_chunk_deep: p.paragraphChunkDeep ?? 2,
        semantic_threshold: p.semanticThreshold ?? 0.5,
        structure_type: p.structureType ?? 'markdown'
      }
      console.log('[useChunking] runChunk request body:', body)

      const res = await fetch(`${API_BASE}/api/chunk`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })

      if (!res.ok) {
        const errBody = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error(errBody.detail || `HTTP ${res.status}`)
      }

      const data = await res.json()
      results.value.set(s, data)
      // 触发响应式更新
      results.value = new Map(results.value)
    } catch (err) {
      error.value = err.message
      console.error('[useChunking] runChunk error:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 多策略对比 —— 并行请求多个策略
   * @param {string} text 待分块文本
   * @param {string[]} strategyList 要对比的策略名数组
   */
  async function runCompare(text, strategyList) {
    if (!text) {
      error.value = '待分块文本为空'
      return
    }
    if (!strategyList || strategyList.length === 0) {
      error.value = '请至少选择一种对比策略'
      return
    }

    loading.value = true
    error.value = ''

    try {
      const baseParams = params.value[strategy.value] || {}
      const promises = strategyList.map(async (s) => {
        const p = params.value[s] || {}
        const body = {
          text,
          strategy: s,
          // 对比模式下：优先使用该策略自身的参数，若未设置则继承当前界面上的参数值
          chunk_size: p.chunkSize ?? baseParams.chunkSize ?? 500,
          overlap_ratio: p.overlapRatio ?? baseParams.overlapRatio ?? 0.0,
          paragraph_chunk_deep: p.paragraphChunkDeep ?? baseParams.paragraphChunkDeep ?? 2,
          semantic_threshold: p.semanticThreshold ?? baseParams.semanticThreshold ?? 0.5,
          structure_type: p.structureType ?? baseParams.structureType ?? 'markdown'
        }
        console.log('[useChunking] runCompare request body:', body)
        const res = await fetch(`${API_BASE}/api/chunk`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        })
        if (!res.ok) {
          const errBody = await res.json().catch(() => ({ detail: res.statusText }))
          throw new Error(`[${s}] ${errBody.detail || res.statusText}`)
        }
        return res.json()
      })

      const datas = await Promise.all(promises)
      datas.forEach((data) => {
        if (data.strategy) {
          results.value.set(data.strategy, data)
        }
      })
      results.value = new Map(results.value)
    } catch (err) {
      error.value = err.message
      console.error('[useChunking] runCompare error:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 重置指定策略的参数到默认值
   */
  function resetParams(s = null) {
    const target = s || strategy.value
    params.value = {
      ...params.value,
      [target]: { ...DEFAULT_PARAMS[target] }
    }
  }

  /**
   * 清空结果缓存
   */
  function clearResults() {
    results.value = new Map()
  }

  /**
   * 策略显示名称映射
   */
  const strategyLabels = {
    recursive: '递归字符分块',
    fixed: '固定长度分块',
    sliding_window: '滑动窗口分块',
    structure: '基于结构分块',
    semantic: '语义分块'
  }

  return {
    strategy,
    params,
    currentParams,
    results,
    strategies,
    loading,
    error,
    currentResult,
    fetchStrategies,
    runChunk,
    runCompare,
    resetParams,
    clearResults,
    strategyLabels
  }
}
