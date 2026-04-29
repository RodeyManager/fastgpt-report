<template>
  <div class="demo-page">
    <div class="demo-header">
      <h2>§14 Demo演示</h2>
      <p>交互式文档处理流水线演示：上传文件 → 文档解析 → Markdown转换 → 数据清洗 → 文本分块 → 图片索引</p>
    </div>

    <div
      class="demo-upload-zone"
      :class="{ 'drag-over': isDragOver }"
      @click="triggerUpload"
      @dragover.prevent="isDragOver = true"
      @dragleave.prevent="isDragOver = false"
      @drop.prevent="handleDrop"
    >
      <span class="upload-icon">📄</span>
      <div class="upload-text">拖拽文件到此处 或 点击选择文件</div>
      <div class="upload-hint">支持 PDF / DOCX / CSV / XLSX / TXT / 图片 等格式</div>
      <input ref="fileInput" type="file" style="display:none" @change="handleFileSelect" />
    </div>

    <div v-if="fileInfo" class="demo-file-info">
      <div class="info-card">
        <span class="info-label">文件名：</span>
        <span class="info-value">{{ fileInfo.name }}</span>
      </div>
      <div class="info-card">
        <span class="info-label">大小：</span>
        <span class="info-value">{{ formatSize(fileInfo.size) }}</span>
      </div>
      <div class="info-card">
        <span class="info-label">类型：</span>
        <span class="info-value">{{ fileInfo.ext.toUpperCase() }}</span>
      </div>
    </div>

    <div v-if="uploadedFile" class="demo-steps">
      <button
        v-for="(step, idx) in steps"
        :key="idx"
        class="demo-step-tab"
        :class="{ active: activeStep === idx }"
        @click="activeStep = idx"
      >{{ step.label }}</button>
    </div>

    <div v-if="loading" class="demo-loading">
      <div class="spinner"></div>
      <span>处理中...</span>
    </div>

    <div v-if="errorMsg" class="demo-error">
      <span>⚠</span> {{ errorMsg }}
    </div>

    <template v-if="uploadedFile && !loading">
      <div class="demo-stats-bar">
        <div class="stat-item" v-if="activeStep === 0">
          <span class="stat-value">{{ rawText.length }}</span>
          <span class="stat-label">原始字符数</span>
        </div>
        <div class="stat-item" v-if="activeStep === 1">
          <span class="stat-value">{{ rawText.length }}</span>
          <span class="stat-label">转换前</span>
        </div>
        <div class="stat-item" v-if="activeStep === 1">
          <span class="stat-value">{{ markdownText?.length || 0 }}</span>
          <span class="stat-label">转换后</span>
        </div>
        <div class="stat-item" v-if="activeStep === 2">
          <span class="stat-value">{{ textBeforeClean.length }}</span>
          <span class="stat-label">清洗前</span>
        </div>
        <div class="stat-item" v-if="activeStep === 2">
          <span class="stat-value">{{ cleanedText.length }}</span>
          <span class="stat-label">清洗后</span>
        </div>
        <div class="stat-item" v-if="activeStep === 2">
          <span class="stat-value">{{ textBeforeClean.length > 0 ? ((1 - cleanedText.length / textBeforeClean.length) * 100).toFixed(1) : 0 }}%</span>
          <span class="stat-label">缩减率</span>
        </div>
        <div class="stat-item" v-if="activeStep === 3">
          <span class="stat-value">{{ chunks.length }}</span>
          <span class="stat-label">分块数量</span>
        </div>
        <div class="stat-item" v-if="activeStep === 3">
          <span class="stat-value">{{ avgChunkSize }}</span>
          <span class="stat-label">平均块大小</span>
        </div>
        <div class="stat-item" v-if="activeStep === 3">
          <span class="stat-value">{{ cleanedText.length }}</span>
          <span class="stat-label">总字符数</span>
        </div>
      </div>

      <div class="demo-layout">
        <div class="demo-result-panel">
          <div class="result-label">{{ steps[activeStep]?.label }} 结果</div>

          <!-- Step 0: 文档解析 -->
          <div v-if="activeStep === 0">
            <div v-if="hasMultipleResults" class="compare-view">
              <div class="compare-column" v-if="engineResults.fastgpt">
                <div class="compare-label">FastGPT 默认</div>
                <div class="result-content" :class="{ 'html-content': parseMethod === 'html' }" v-html="engineResults.fastgpt?.html_preview || ''"></div>
                <div class="compare-stat">{{ (engineResults.fastgpt?.raw_text || '').length }} 字符</div>
              </div>
              <div class="compare-column" v-if="engineResults.mineru">
                <div class="compare-label">MinerU</div>
                <div class="result-content" :class="{ 'html-content': parseMethod === 'html' }" v-html="engineResults.mineru?.html_preview || ''"></div>
                <div class="compare-stat">{{ (engineResults.mineru?.raw_text || '').length }} 字符</div>
              </div>
              <div class="compare-column" v-if="engineResults.unstructured">
                <div class="compare-label">Unstructured-API</div>
                <div class="result-content" :class="{ 'html-content': parseMethod === 'html' }" v-html="engineResults.unstructured?.html_preview || ''"></div>
                <div class="compare-stat">{{ (engineResults.unstructured?.raw_text || '').length }} 字符</div>
              </div>
            </div>
            <template v-else>
              <div v-if="parsedResult" class="result-content" :class="{ 'html-content': parseMethod === 'html' }" v-html="parsedResult"></div>
              <div v-else class="empty-state">点击右侧「开始解析」按钮进行文档解析</div>
            </template>
          </div>

          <!-- Step 1: Markdown转换 -->
          <div v-if="activeStep === 1">
            <div v-if="markdownText !== null" style="display:flex;flex-direction:column;gap:16px">
              <div>
                <div style="font-size:0.75rem;color:var(--text-muted);margin-bottom:6px">原始解析输出 ({{ rawText.length }} 字符)</div>
                <div class="result-content demo-fulltext-box" v-if="isDocxHtmlMode" v-html="rawText"></div>
                <div class="result-content demo-fulltext-box" v-else>{{ rawText }}</div>
              </div>
              <div>
                <div style="font-size:0.75rem;color:var(--accent-green);margin-bottom:6px">Markdown 转换结果 ({{ markdownText.length }} 字符)</div>
                <div class="result-content demo-fulltext-box" style="background:rgba(0,255,136,0.04);border-color:rgba(0,255,136,0.15)">{{ markdownText }}</div>
              </div>
              <div v-if="mdConversionNote" style="font-size:0.78rem;color:var(--text-muted);padding:8px 12px;background:rgba(99,102,241,0.05);border-radius:6px;border-left:3px solid var(--accent-blue)">
                {{ mdConversionNote }}
              </div>
            </div>
            <div v-else class="empty-state">请先完成文档解析，再点击「转换为Markdown」</div>
          </div>

          <!-- Step 2: 数据清洗 -->
          <div v-if="activeStep === 2">
            <div v-if="cleanedText !== null" style="display:flex;flex-direction:column;gap:16px">
              <div>
                <div style="font-size:0.75rem;color:var(--text-muted);margin-bottom:6px">清洗前 ({{ textBeforeClean.length }} 字符)</div>
                <div class="result-content demo-fulltext-box">{{ textBeforeClean }}</div>
              </div>
              <div>
                <div style="font-size:0.75rem;color:var(--accent-cyan);margin-bottom:6px">清洗后 ({{ cleanedText.length }} 字符)</div>
                <div class="result-content demo-fulltext-box" style="background:rgba(6,182,212,0.06);border-color:rgba(6,182,212,0.15)">{{ cleanedText }}</div>
              </div>
            </div>
            <div v-else class="empty-state">请先完成 Markdown 转换，再点击「执行清洗」</div>
          </div>

          <!-- Step 3: 文本分块 -->
          <div v-if="activeStep === 3">
            <div v-if="chunks.length > 0">
              <div v-for="(chunk, idx) in chunks" :key="idx" class="demo-chunk-item">
                <div class="chunk-header">
                  <span class="chunk-index">Chunk #{{ idx + 1 }}</span>
                  <span class="chunk-size">{{ chunk.length }} 字符</span>
                </div>
                <div class="chunk-text">{{ chunk }}</div>
              </div>
            </div>
            <div v-else class="empty-state">请先完成数据清洗，再点击「执行分块」</div>
          </div>

          <!-- Step 4: 图片索引 -->
          <div v-if="activeStep === 4">
            <div v-if="imagePreview">
              <img :src="imagePreview" class="demo-image-preview" alt="preview" />
              <div class="result-content">
                <div style="margin-bottom:12px;color:var(--text-primary);font-family:var(--font-body);font-size:0.9rem">
                  图片索引使用 VLM（视觉语言模型）对图片内容进行理解与描述，生成可用于检索的文本向量。
                </div>
                <div v-if="imageDescription" style="margin-top:8px;padding:10px;background:rgba(6,182,212,0.06);border-radius:6px;border-left:3px solid var(--accent-cyan)">
                  <div style="font-size:0.78rem;color:var(--accent-cyan);margin-bottom:4px">VLM 描述结果</div>
                  <div style="font-size:0.85rem;color:var(--text-primary)">{{ imageDescription }}</div>
                  <div v-if="imageMeta" style="font-size:0.75rem;color:var(--text-muted);margin-top:6px">
                    {{ imageMeta.width }}×{{ imageMeta.height }} {{ imageMeta.format }} {{ formatSize(imageMeta.size_bytes) }}
                  </div>
                </div>
                <div v-else style="color:var(--text-muted);font-size:0.82rem">
                  流程：图片上传 → VLM 模型描述 → 文本向量化 → 存入向量数据库 → 支持语义检索
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              上传图片文件以预览索引效果<br />
              <span style="font-size:0.8rem;color:var(--text-muted)">当前文件非图片格式</span>
            </div>
          </div>
        </div>

        <div class="demo-options-panel">
          <!-- Step 0 Options: 文档解析 -->
          <template v-if="activeStep === 0">
            <div class="option-title">解析选项</div>
            <div class="demo-option-item">
              <span>解析引擎：</span>
              <select v-model="selectedEngine">
                <option v-for="e in engines" :key="e.value" :value="e.value">{{ e.label }}</option>
              </select>
            </div>
            <div v-if="!isMineruAvailable && fileInfo" style="font-size:0.78rem;color:var(--text-secondary);padding:2px 0">
              MinerU 仅支持 PDF/DOCX/PPTX/图片格式
            </div>
            <div class="demo-option-item">
              <span>解析方式：</span>
              <select v-model="parseMethod">
                <option v-for="m in parseMethods" :key="m.value" :value="m.value">{{ m.label }}</option>
              </select>
            </div>
            <div v-if="sheetNames.length > 1" class="demo-option-item">
              <span>工作表：</span>
              <select v-model="selectedSheet">
                <option v-for="s in sheetNames" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
            <button class="demo-action-btn" @click="runParse">
              <span>▶</span> 开始解析
            </button>
            <div class="highlight-block" style="font-size:0.82rem;margin-top:8px">
              不同文件类型支持不同的解析策略：PDF 可按页提取文本；DOCX 可获取 HTML 或纯文本；CSV/XLSX 支持表头识别与结构化解析。
            </div>
          </template>

          <!-- Step 1 Options: Markdown转换 -->
          <template v-if="activeStep === 1">
            <div class="option-title">Markdown 转换</div>
            <div class="demo-option-item" style="flex-direction:column;align-items:flex-start;gap:4px">
              <div style="font-size:0.82rem;color:var(--text-secondary)">当前文件类型: <code style="color:var(--accent-cyan)">{{ fileInfo?.ext?.toUpperCase() }}</code></div>
              <div style="font-size:0.82rem;color:var(--text-secondary)">转换方式: <code style="color:var(--accent-green)">{{ mdConversionMethod }}</code></div>
              <div style="font-size:0.82rem;color:var(--text-secondary)">输出格式: <code :style="{ color: isMarkdownOutput ? 'var(--accent-green)' : 'var(--accent-orange)' }">{{ isMarkdownOutput ? 'Markdown' : '纯文本(无MD转换)' }}</code></div>
            </div>
            <button class="demo-action-btn" @click="runMarkdownConvert">
              <span>▶</span> 转换为 Markdown
            </button>
            <div class="highlight-block" style="font-size:0.82rem;margin-top:8px">
              <div style="font-weight:600;color:var(--text-primary);margin-bottom:6px">转换链路说明</div>
              <div>Markdown 转换由后端 FastAPI 服务完成。支持 DOCX (HTML→MD)、CSV/XLSX (表格→MD)、MD (原样保留)、PDF (纯文本) 等多种转换策略。</div>
            </div>
          </template>

          <!-- Step 2 Options: 数据清洗 -->
          <template v-if="activeStep === 2">
            <div class="option-title">清洗选项</div>
            <div class="demo-option-item">
              <input type="checkbox" v-model="cleanOptions.trim" />
              <span>去除首尾空白</span>
            </div>
            <div class="demo-option-item">
              <input type="checkbox" v-model="cleanOptions.remove_chinese_space" />
              <span>移除中文字符间空格</span>
            </div>
            <div class="demo-option-item">
              <input type="checkbox" v-model="cleanOptions.normalize_newline" />
              <span>规范化换行符</span>
            </div>
            <div class="demo-option-item">
              <input type="checkbox" v-model="cleanOptions.collapse_whitespace" />
              <span>合并连续空白</span>
            </div>
            <div class="demo-option-item">
              <input type="checkbox" v-model="cleanOptions.remove_empty_lines" />
              <span>移除空行</span>
            </div>
            <button class="demo-action-btn" @click="runCleaning">
              <span>▶</span> 执行清洗
            </button>
            <div class="highlight-block" style="font-size:0.82rem;margin-top:8px">
              FastGPT 的清洗流程会将文档原始输出转换为更干净、更适合分块的文本格式。
            </div>
          </template>

          <!-- Step 3 Options: 文本分块 -->
          <template v-if="activeStep === 3">
            <div class="option-title">分块参数</div>
            <div class="demo-slider-group">
              <label>块大小 <span>{{ chunkParams.chunkSize }}</span></label>
              <input type="range" v-model.number="chunkParams.chunkSize" min="100" max="8000" step="100" />
            </div>
            <div class="demo-slider-group">
              <label>重叠率 <span>{{ (chunkParams.overlapRatio * 100).toFixed(0) }}%</span></label>
              <input type="range" v-model.number="chunkParams.overlapRatio" min="0" max="0.4" step="0.05" />
            </div>
            <div class="demo-slider-group">
              <label>段落深度 <span>{{ chunkParams.paragraphChunkDeep }}</span></label>
              <input type="range" v-model.number="chunkParams.paragraphChunkDeep" min="1" max="5" step="1" />
            </div>
            <button class="demo-action-btn" @click="runChunking">
              <span>▶</span> 执行分块
            </button>
            <div class="highlight-block" style="font-size:0.82rem;margin-top:8px">
              递归多级分块策略：依次尝试 Markdown 标题 → 段落 → 标点 → 固定长度，确保语义完整性。
            </div>
          </template>

          <!-- Step 4 Options: 图片索引 -->
          <template v-if="activeStep === 4">
            <div class="option-title">图片索引信息</div>
            <div v-if="fileInfo" class="demo-option-item" style="flex-direction:column;align-items:flex-start;gap:4px">
              <div>文件名: <span style="color:var(--accent-cyan)">{{ fileInfo.name }}</span></div>
              <div>文件大小: <span style="color:var(--accent-cyan)">{{ formatSize(fileInfo.size) }}</span></div>
              <div>文件类型: <span style="color:var(--accent-cyan)">{{ fileInfo.type || '未知' }}</span></div>
            </div>
            <button
              v-if="isImageFile && !imageDescription"
              class="demo-action-btn"
              @click="runImageIndex"
            >
              <span>▶</span> 生成图片描述
            </button>
            <div class="highlight-block" style="font-size:0.82rem;margin-top:8px">
              <div style="font-weight:600;color:var(--text-primary);margin-bottom:6px">VLM 训练模式</div>
              <div>图片通过视觉语言模型自动生成描述文本，支持：</div>
              <div style="margin-top:4px">• 自动识别图中文字 (OCR)</div>
              <div>• 场景与物体描述</div>
              <div>• 图表数据解读</div>
              <div>• 生成可检索的语义向量</div>
            </div>
          </template>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:3002'

const fileInput = ref(null)
const activeStep = ref(0)
const uploadedFile = ref(null)
const rawText = ref('')
const formatText = ref('')
const parsedResult = ref('')
const markdownText = ref(null)
const mdConversionNote = ref('')
const cleanedText = ref('')
const textBeforeClean = ref('')
const chunks = ref([])
const loading = ref(false)
const errorMsg = ref('')
const fileInfo = ref(null)
const parseMethod = ref('text')
const isDragOver = ref(false)
const imagePreview = ref(null)
const imageDescription = ref('')
const imageMeta = ref(null)
const selectedSheet = ref(null)
const sheetNames = ref([])

const cleanOptions = ref({
  trim: true,
  remove_chinese_space: true,
  normalize_newline: true,
  collapse_whitespace: true,
  remove_empty_lines: true
})

const chunkParams = ref({
  chunkSize: 500,
  overlapRatio: 0.2,
  paragraphChunkDeep: 2
})

const steps = [
  { label: '文档解析' },
  { label: 'Markdown转换' },
  { label: '数据清洗' },
  { label: '文本分块' },
  { label: '图片索引' }
]

const IMAGE_EXTS = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp']

const isImageFile = computed(() => {
  return fileInfo.value ? IMAGE_EXTS.includes(fileInfo.value.ext) : false
})

const selectedEngine = ref('fastgpt')
const engineResults = ref({})
const MINERU_SUPPORTED_EXTS = ['pdf', 'docx', 'doc', 'pptx', 'png', 'jpg', 'jpeg', 'gif', 'webp']
const UNSTRUCTURED_SUPPORTED_EXTS = ['pdf', 'docx', 'doc', 'pptx', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'csv', 'xlsx', 'xls', 'txt', 'md', 'html']

const isMineruAvailable = computed(() => {
  if (!fileInfo.value) return false
  return MINERU_SUPPORTED_EXTS.includes(fileInfo.value.ext.toLowerCase())
})

const isUnstructuredAvailable = computed(() => {
  if (!fileInfo.value) return false
  return UNSTRUCTURED_SUPPORTED_EXTS.includes(fileInfo.value.ext.toLowerCase())
})

const engines = computed(() => {
  const list = [{ value: 'fastgpt', label: 'FastGPT 默认' }]
  if (isMineruAvailable.value) {
    list.push({ value: 'mineru', label: 'MinerU' })
  }
  if (isUnstructuredAvailable.value) {
    list.push({ value: 'unstructured', label: 'Unstructured-API' })
  }
  return list
})

const hasMultipleResults = computed(() => {
  return Object.keys(engineResults.value).filter(k => engineResults.value[k]).length > 1
})

const parseMethods = computed(() => {
  if (!fileInfo.value) return [{ value: 'text', label: '纯文本' }]
  const ext = fileInfo.value.ext
  const methods = []
  if (ext === 'pdf') {
    methods.push({ value: 'text', label: '文本提取' })
  } else if (ext === 'docx' || ext === 'doc') {
    methods.push({ value: 'html', label: 'HTML转换' })
    methods.push({ value: 'text', label: '纯文本提取' })
  } else if (ext === 'csv') {
    methods.push({ value: 'table', label: '表格解析' })
    methods.push({ value: 'raw', label: '原始文本' })
  } else if (ext === 'xlsx' || ext === 'xls') {
    methods.push({ value: 'table', label: '表格解析' })
  } else if (['txt', 'md', 'json', 'js', 'ts', 'py'].includes(ext)) {
    methods.push({ value: 'text', label: '纯文本' })
  } else if (IMAGE_EXTS.includes(ext)) {
    methods.push({ value: 'image', label: '图片预览' })
  } else {
    methods.push({ value: 'text', label: '纯文本' })
  }
  return methods
})

const avgChunkSize = computed(() => {
  if (chunks.value.length === 0) return 0
  return Math.round(chunks.value.reduce((s, c) => s + c.length, 0) / chunks.value.length)
})

const isDocxHtmlMode = computed(() => {
  const ext = fileInfo.value?.ext
  return (ext === 'docx' || ext === 'doc') && parseMethod.value === 'html'
})

const mdConversionMethod = computed(() => {
  if (!fileInfo.value) return '未知'
  const ext = fileInfo.value.ext
  if (ext === 'docx' || ext === 'doc') return 'turndown (HTML→MD)'
  if (ext === 'csv' || ext === 'xlsx' || ext === 'xls') return '字符串拼接 (表格→MD)'
  if (ext === 'html') return 'turndown (HTML→MD)'
  if (ext === 'md') return '原样保留'
  return '无转换 (纯文本)'
})

const isMarkdownOutput = computed(() => {
  const ext = fileInfo.value?.ext
  return ['docx', 'doc', 'csv', 'xlsx', 'xls', 'html', 'md'].includes(ext)
})

function getExt(filename) {
  return filename.split('.').pop().toLowerCase()
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

function triggerUpload() {
  fileInput.value?.click()
}

function handleFileSelect(e) {
  const file = e.target.files?.[0]
  if (file) processFile(file)
}

function handleDrop(e) {
  isDragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) processFile(file)
}

function processFile(file) {
  uploadedFile.value = file
  fileInfo.value = {
    name: file.name,
    size: file.size,
    ext: getExt(file.name),
    type: file.type
  }
  activeStep.value = 0
  chunks.value = []
  cleanedText.value = ''
  textBeforeClean.value = ''
  markdownText.value = null
  mdConversionNote.value = ''
  formatText.value = ''
  parsedResult.value = ''
  rawText.value = ''
  imageDescription.value = ''
  imageMeta.value = null
  sheetNames.value = []
  selectedSheet.value = null
  errorMsg.value = ''
  engineResults.value = {}
  selectedEngine.value = 'fastgpt'

  if (fileInfo.value.ext === 'xlsx' || fileInfo.value.ext === 'xls') {
    parseMethod.value = 'table'
  } else {
    parseMethod.value = parseMethods.value[0]?.value || 'text'
  }

  if (IMAGE_EXTS.includes(fileInfo.value.ext)) {
    const reader = new FileReader()
    reader.onload = (e) => { imagePreview.value = e.target.result }
    reader.readAsDataURL(file)
  } else {
    imagePreview.value = null
  }
}

async function apiCall(path, options, timeout = 300000) {
  errorMsg.value = ''
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      signal: controller.signal,
    })
    clearTimeout(timeoutId)
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(errBody.detail || `HTTP ${res.status}`)
    }
    return res.json()
  } catch (err) {
    clearTimeout(timeoutId)
    if (err.name === 'AbortError') {
      throw new Error('请求超时，请稍后重试')
    }
    throw err
  }
}

async function runParse() {
  if (!uploadedFile.value) return
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadedFile.value)
    formData.append('method', 'auto')
    formData.append('engine', selectedEngine.value)

    const data = await apiCall('/api/parse', { method: 'POST', body: formData })

    rawText.value = data.raw_text || ''
    formatText.value = data.format_text || ''
    parsedResult.value = data.html_preview || ''
    sheetNames.value = data.sheet_names || []
    if (data.results) {
      engineResults.value[selectedEngine.value] = data
    }

    if (sheetNames.value.length > 0 && !selectedSheet.value) {
      selectedSheet.value = sheetNames.value[0]
    }
  } catch (err) {
    parsedResult.value = `<div style="color:var(--accent-red)">解析失败: ${err.message}</div>`
    rawText.value = ''
    errorMsg.value = err.message
  }
  loading.value = false
}

async function runMarkdownConvert() {
  if (!rawText.value) {
    markdownText.value = ''
    mdConversionNote.value = '请先完成文档解析'
    return
  }

  loading.value = true
  try {
    const data = await apiCall('/api/convert', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        raw_text: rawText.value,
        format_text: formatText.value,
        file_ext: fileInfo.value.ext
      })
    })
    markdownText.value = data.markdown || ''
    mdConversionNote.value = data.note || ''
  } catch (err) {
    markdownText.value = ''
    mdConversionNote.value = '转换失败: ' + err.message
    errorMsg.value = err.message
  }
  loading.value = false
}

async function runCleaning() {
  const source = markdownText.value !== null ? markdownText.value : rawText.value
  if (!source) {
    cleanedText.value = ''
    return
  }
  textBeforeClean.value = source

  loading.value = true
  try {
    const data = await apiCall('/api/clean', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: source,
        options: { ...cleanOptions.value }
      })
    })
    cleanedText.value = data.cleaned || ''
  } catch (err) {
    cleanedText.value = source
    errorMsg.value = err.message
  }
  loading.value = false
}

async function runChunking() {
  if (!cleanedText.value) { chunks.value = []; return }

  loading.value = true
  try {
    const data = await apiCall('/api/chunk', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: cleanedText.value,
        chunk_size: chunkParams.value.chunkSize,
        overlap_ratio: chunkParams.value.overlapRatio,
        paragraph_chunk_deep: chunkParams.value.paragraphChunkDeep
      })
    })
    chunks.value = data.chunks || []
  } catch (err) {
    chunks.value = []
    errorMsg.value = err.message
  }
  loading.value = false
}

async function runImageIndex() {
  if (!uploadedFile.value || !isImageFile.value) return

  loading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadedFile.value)

    const data = await apiCall('/api/index-image', { method: 'POST', body: formData })
    imageDescription.value = data.description || ''
    imageMeta.value = {
      width: data.width,
      height: data.height,
      format: data.format,
      size_bytes: data.size_bytes
    }
  } catch (err) {
    imageDescription.value = ''
    errorMsg.value = err.message
  }
  loading.value = false
}

watch(parseMethod, async () => {
  if (!uploadedFile.value || !rawText.value) return
})
</script>

<style scoped>
.demo-page {
  max-width: 1200px;
  margin: 0 auto;
}

.demo-header {
  margin-bottom: 20px;
}

.demo-header h2 {
  font-size: 1.4rem;
  font-weight: 600;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-green));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 6px;
}

.demo-header p {
  font-size: 0.85rem;
  color: var(--text-muted);
  line-height: 1.5;
}

/* Upload Zone */
.demo-upload-zone {
  border: 2px dashed var(--border-light);
  border-radius: 12px;
  padding: 36px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s ease;
  background: var(--bg-secondary);
  margin-bottom: 16px;
}

.demo-upload-zone:hover,
.demo-upload-zone.drag-over {
  border-color: var(--accent-cyan);
  background: rgba(6, 182, 212, 0.04);
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.08);
}

.upload-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 8px;
}

.upload-text {
  font-size: 0.95rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.upload-hint {
  font-size: 0.78rem;
  color: var(--text-muted);
}

/* File Info */
.demo-file-info {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.info-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 0.82rem;
}

.info-label {
  color: var(--text-muted);
}

.info-value {
  color: var(--accent-cyan);
  font-family: var(--font-mono);
}

/* Steps Tabs */
.demo-steps {
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.demo-step-tab {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-muted);
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: var(--font-body);
}

.demo-step-tab:hover {
  background: var(--bg-hover);
  color: var(--text-secondary);
  border-color: var(--border-light);
}

.demo-step-tab.active {
  background: rgba(6, 182, 212, 0.1);
  border-color: var(--accent-cyan);
  color: var(--accent-cyan);
  font-weight: 500;
}

/* Loading */
.demo-loading {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px;
  color: var(--accent-cyan);
  font-size: 0.9rem;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-light);
  border-top-color: var(--accent-cyan);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error */
.demo-error {
  padding: 10px 16px;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  color: var(--accent-red);
  font-size: 0.85rem;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Layout */
.demo-layout {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.compare-view {
  display: flex;
  gap: 16px;
}

.compare-column {
  flex: 1;
  min-width: 0;
}

.compare-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--accent-cyan);
  margin-bottom: 8px;
  padding: 4px 8px;
  background: rgba(99, 102, 241, 0.06);
  border-radius: 6px;
  display: inline-block;
}

.compare-stat {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-top: 4px;
}

@media (max-width: 768px) {
  .compare-view { flex-direction: column; }
}

.demo-result-panel {
  flex: 1;
  min-width: 0;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  overflow: hidden;
}

.demo-options-panel {
  width: 320px;
  flex-shrink: 0;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.result-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.result-content {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px;
  font-family: var(--font-mono);
  font-size: 0.82rem;
  line-height: 1.7;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 500px;
  overflow-y: auto;
}

.result-content.html-content {
  white-space: normal;
  font-family: var(--font-body);
}

.result-content.html-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 8px 0;
}

.result-content.html-content :deep(th),
.result-content.html-content :deep(td) {
  border: 1px solid var(--border-color);
  padding: 6px 10px;
  font-size: 0.8rem;
}

.result-content.html-content :deep(th) {
  background: var(--bg-tertiary);
  color: var(--accent-cyan);
  font-weight: 500;
}

.result-content.html-content :deep(td) {
  color: var(--text-secondary);
}

.demo-fulltext-box {
  max-height: 220px;
  overflow-y: auto;
}

.empty-state {
  padding: 32px 16px;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.85rem;
  line-height: 1.6;
}

/* Options */
.option-title {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text-primary);
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.demo-option-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
  color: var(--text-secondary);
}

.demo-option-item select {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 4px 8px;
  color: var(--text-primary);
  font-size: 0.82rem;
  font-family: var(--font-body);
  outline: none;
}

.demo-option-item select:focus {
  border-color: var(--accent-cyan);
}

.demo-option-item input[type="checkbox"] {
  accent-color: var(--accent-cyan);
  width: 15px;
  height: 15px;
}

.demo-action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: var(--font-body);
  margin-top: 4px;
}

.demo-action-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.2);
}

.demo-action-btn:active {
  transform: translateY(0);
}

.highlight-block {
  padding: 10px 12px;
  background: rgba(6, 182, 212, 0.04);
  border-radius: 8px;
  border-left: 3px solid var(--accent-cyan);
  color: var(--text-secondary);
  line-height: 1.6;
}

.demo-slider-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.demo-slider-group label {
  font-size: 0.82rem;
  color: var(--text-secondary);
  display: flex;
  justify-content: space-between;
}

.demo-slider-group label span {
  color: var(--accent-cyan);
  font-family: var(--font-mono);
  font-weight: 500;
}

.demo-slider-group input[type="range"] {
  width: 100%;
  accent-color: var(--accent-cyan);
  height: 4px;
}

/* Chunks */
.demo-chunk-item {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin-bottom: 8px;
  overflow: hidden;
}

.chunk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 12px;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
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

.chunk-text {
  padding: 10px 12px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  line-height: 1.65;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}

/* Image Preview */
.demo-image-preview {
  max-width: 100%;
  border-radius: 8px;
  margin-bottom: 12px;
  border: 1px solid var(--border-color);
}

/* Stats Bar */
.demo-stats-bar {
  display: flex;
  gap: 16px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.stat-value {
  font-family: var(--font-mono);
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--accent-cyan);
}

.stat-label {
  font-size: 0.72rem;
  color: var(--text-muted);
}

/* Responsive */
@media (max-width: 768px) {
  .demo-layout {
    flex-direction: column;
  }

  .demo-options-panel {
    width: 100%;
  }

  .demo-file-info {
    flex-direction: column;
    gap: 6px;
  }

  .demo-steps {
    gap: 4px;
  }

  .demo-step-tab {
    padding: 6px 10px;
    font-size: 0.78rem;
  }

  .demo-stats-bar {
    gap: 10px;
  }
}
</style>
