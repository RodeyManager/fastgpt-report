<template>
  <div class="section-page">
    <div class="section-header">
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

    <template v-if="uploadedFile && !loading">
      <div class="demo-layout">
        <div class="demo-result-panel">
          <div class="result-label">{{ steps[activeStep]?.label }} 结果</div>

          <!-- Step 0: 文档解析 -->
          <div v-if="activeStep === 0">
            <div v-if="parsedResult" class="result-content" :class="{ 'html-content': parseMethod === 'html' }" v-html="parsedResult"></div>
            <div v-else class="empty-state">点击右侧「开始解析」按钮进行文档解析</div>
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
                <div style="color:var(--text-muted);font-size:0.82rem">
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
              <span>解析方式：</span>
              <select v-model="parseMethod">
                <option v-for="m in parseMethods" :key="m.value" :value="m.value">{{ m.label }}</option>
              </select>
            </div>
            <div v-if="selectedSheet !== null" class="demo-option-item">
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
              <div v-if="mdConversionMethod === 'turndown (HTML→MD)'">
                DOCX 经 mammoth 转为 HTML，再通过 turndown 转为 Markdown。转换后的 Markdown 保留标题、列表、表格等结构。
              </div>
              <div v-else-if="mdConversionMethod === '字符串拼接 (表格→MD)'">
                CSV/XLSX 解析后直接拼接为 Markdown 表格格式。系统同时输出 rawText 和 formatText，默认优先使用 formatText。
              </div>
              <div v-else-if="mdConversionMethod === '原样保留'">
                Markdown 文件不需要转换，原样保留。分块器可直接利用标题层级、代码块、表格等 Markdown 结构进行智能拆分。
              </div>
              <div v-else-if="mdConversionMethod === '无转换 (纯文本)'">
                PDF(默认) 和 PPTX 的解析输出为纯文本，不经过 Markdown 转换。分块器无法利用标题/表格/代码块规则，只能按段落和标点切分。<br/><br/>
                <em style="color:var(--accent-cyan)">提示：PDF 可使用 Doc2x / Textin 等第三方解析服务获得 Markdown 输出。</em>
              </div>
              <div v-else>
                根据文件类型选择不同的转换策略。
              </div>
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
              <input type="checkbox" v-model="cleanOptions.removeChineseSpace" />
              <span>移除中文字符间空格</span>
            </div>
            <div class="demo-option-item">
              <input type="checkbox" v-model="cleanOptions.normalizeNewline" />
              <span>规范化换行符</span>
            </div>
            <div class="demo-option-item">
              <input type="checkbox" v-model="cleanOptions.collapseWhitespace" />
              <span>合并连续空白</span>
            </div>
            <div class="demo-option-item">
              <input type="checkbox" v-model="cleanOptions.removeEmptyLines" />
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
            <div class="demo-option-item">
              <span>分块模式：</span>
              <select v-model="chunkMode">
                <option value="auto">自动</option>
                <option value="paragraph">段落优先</option>
                <option value="punctuation">标点切分</option>
              </select>
            </div>
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
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import * as pdfjsLib from 'pdfjs-dist'
import mammoth from 'mammoth'
import Papa from 'papaparse'
import * as XLSX from 'xlsx'
import TurndownService from 'turndown'
import { gfm } from 'joplin-turndown-plugin-gfm'

pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url
).toString()

const fileInput = ref(null)
const activeStep = ref(0)
const uploadedFile = ref(null)
const rawText = ref('')
const parsedResult = ref('')
const markdownText = ref(null)   // null = not yet converted
const mdConversionNote = ref('')
const markdownFormatText = ref('')  // CSV/XLSX formatText (Markdown table)
const cleanedText = ref('')       // empty = not yet cleaned
const textBeforeClean = ref('')   // snapshot before cleaning
const chunks = ref([])
const loading = ref(false)
const fileInfo = ref(null)
const parseMethod = ref('text')
const isDragOver = ref(false)
const imagePreview = ref(null)
const selectedSheet = ref(null)
const sheetNames = ref([])
const xlsxWorkbook = ref(null)

const cleanOptions = ref({
  trim: true,
  removeChineseSpace: true,
  normalizeNewline: true,
  collapseWhitespace: true,
  removeEmptyLines: true
})

const chunkParams = ref({
  chunkSize: 500,
  overlapRatio: 0.2,
  paragraphChunkDeep: 2
})

const chunkMode = ref('auto')

// 5 steps now
const steps = [
  { label: '文档解析' },
  { label: 'Markdown转换' },
  { label: '数据清洗' },
  { label: '文本分块' },
  { label: '图片索引' }
]

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
  } else if (['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp'].includes(ext)) {
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

// Markdown conversion info based on file type
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

function getExt(filename) {
  return filename.split('.').pop().toLowerCase()
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

async function processFile(file) {
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
  markdownFormatText.value = ''
  parsedResult.value = ''

  if (fileInfo.value.ext === 'xlsx' || fileInfo.value.ext === 'xls') {
    parseMethod.value = 'table'
  } else {
    const firstMethod = parseMethods.value[0]?.value || 'text'
    parseMethod.value = firstMethod
  }

  // Don't auto-parse; wait for user to click button
}

// === Manual trigger buttons ===

async function runParse() {
  if (!uploadedFile.value) return
  loading.value = true
  try {
    const ext = fileInfo.value.ext
    if (ext === 'pdf') await parsePDF(uploadedFile.value)
    else if (ext === 'docx' || ext === 'doc') await parseDocx(uploadedFile.value)
    else if (ext === 'csv') await parseCSV(uploadedFile.value)
    else if (ext === 'xlsx' || ext === 'xls') await parseXLSX(uploadedFile.value)
    else if (['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp'].includes(ext)) {
      rawText.value = `[图片文件: ${fileInfo.value.name}]`
      parsedResult.value = `<div style="text-align:center"><img src="${imagePreview.value}" style="max-width:100%;border-radius:8px" /></div>`
    }
    else await parseText(uploadedFile.value)
  } catch (err) {
    parsedResult.value = `<div style="color:var(--accent-red)">解析失败: ${err.message}</div>`
    rawText.value = ''
  }
  loading.value = false
}

function runMarkdownConvert() {
  if (!rawText.value) {
    markdownText.value = ''
    mdConversionNote.value = '请先完成文档解析'
    return
  }
  const ext = fileInfo.value.ext
  if (['csv', 'xlsx', 'xls'].includes(ext) && markdownFormatText.value) {
    // CSV/XLSX already have formatText from parser
    markdownText.value = markdownFormatText.value
    mdConversionNote.value = 'CSV/XLSX 解析后直接输出 Markdown 表格格式 (formatText)。这是 FastGPT 的「格式选择门」机制：getFormatText=true 时优先使用 formatText。'
  } else if (['docx', 'doc'].includes(ext)) {
    markdownText.value = htmlToMarkdown(rawText.value)
    mdConversionNote.value = '模拟 FastGPT DOCX 解析链路：mammoth 转 HTML → turndown(GFM) 转 Markdown → simpleMarkdownText 后处理。保留标题、列表、表格结构。'
  } else if (ext === 'md') {
    markdownText.value = rawText.value
    mdConversionNote.value = 'Markdown 文件原样保留，无需转换。分块器可直接利用标题层级、代码块、表格等结构进行智能拆分。'
  } else if (ext === 'html') {
    markdownText.value = htmlToMarkdown(rawText.value)
    mdConversionNote.value = 'HTML 通过 turndown(GFM) + simpleMarkdownText 转换为 Markdown，保留链接、列表、表格等语义结构。'
  } else {
    markdownText.value = rawText.value
    mdConversionNote.value = '此文件类型解析输出为纯文本，不经过 Markdown 转换。分块器只能按段落和标点切分，无法利用 Markdown 结构规则。PDF 可使用 Doc2x/Textin 等第三方解析服务获得 Markdown。'
  }
}

function runCleaning() {
  const source = markdownText.value !== null ? markdownText.value : rawText.value
  if (!source) {
    cleanedText.value = ''
    return
  }
  textBeforeClean.value = source
  cleanedText.value = simpleText(source)
}

function getTextValidLength(text) {
  return text.replace(/\s/g, '').length
}

const strIsMdTable = (str) => {
  if (!str.includes('|')) return false
  const lines = str.split('\n')
  if (lines.length < 2) return false
  const headerLine = lines[0].trim()
  if (!headerLine.startsWith('|') || !headerLine.endsWith('|')) return false
  const separatorLine = lines[1].trim()
  const separatorRegex = /^(\|[\s:]*-+[\s:]*)+\|$/
  if (!separatorRegex.test(separatorLine)) return false
  for (let i = 2; i < lines.length; i++) {
    const dataLine = lines[i].trim()
    if (dataLine && (!dataLine.startsWith('|') || !dataLine.endsWith('|'))) return false
  }
  return true
}

const markdownTableSplit = (props) => {
  let { text = '', chunkSize, maxSize = defaultMaxChunkSize } = props
  const splitText2Lines = text.split('\n').filter(line => line.trim())
  if (splitText2Lines.length < 2) return { chunks: [text], chars: text.length }

  const header = splitText2Lines[0]
  const headerSize = header.split('|').length - 2
  const mdSplitString = `| ${new Array(headerSize > 0 ? headerSize : 1).fill(0).map(() => '---').join(' | ')} |`
  const defaultChunk = `${header}\n${mdSplitString}\n`
  let chunk = defaultChunk
  const chunks = []

  for (let i = 2; i < splitText2Lines.length; i++) {
    const chunkLength = getTextValidLength(chunk)
    const nextLineLength = getTextValidLength(splitText2Lines[i])
    if (chunkLength + nextLineLength > chunkSize) {
      if (chunkLength > maxSize) {
        const newChunks = commonSplit({ ...props, text: chunk.replace(defaultChunk, '').trim() }).chunks
        chunks.push(...newChunks)
      } else {
        chunks.push(chunk)
      }
      chunk = defaultChunk
    }
    chunk += `${splitText2Lines[i]}\n`
  }
  if (chunk) chunks.push(chunk)
  return { chunks, chars: chunks.reduce((sum, c) => sum + c.length, 0) }
}

function commonSplit(props) {
  let {
    text = '',
    chunkSize,
    paragraphChunkDeep = 5,
    paragraphChunkMinSize = 100,
    maxSize = defaultMaxChunkSize,
    overlapRatio = 0.15,
    customReg = []
  } = props

  const splitMarker = 'SPLIT_HERE_SPLIT_HERE'
  const codeBlockMarker = 'CODE_BLOCK_LINE_MARKER'
  const overlapLen = Math.round(chunkSize * overlapRatio)

  // Protect code blocks
  text = text.replace(/(```[\s\S]*?```|~~~[\s\S]*?~~~)/g, function(match) {
    return match.replace(/\n/g, codeBlockMarker)
  })
  text = text.replace(/(\r?\n|\r){3,}/g, '\n\n\n')

  const customRegLen = customReg.length
  const markdownIndex = paragraphChunkDeep - 1
  const forbidOverlapIndex = customRegLen + markdownIndex + 4

  const markdownHeaderRules = ((deep) => {
    if (!deep || deep === 0) return []
    const maxDeep = Math.min(deep, 8)
    const rules = []
    for (let i = 1; i <= maxDeep; i++) {
      const hashSymbols = '#'.repeat(i)
      rules.push({ reg: new RegExp(`^(${hashSymbols}\\s[^\\n]+\\n)`, 'gm'), maxLen: chunkSize })
    }
    return rules
  })(paragraphChunkDeep)

  const stepReges = [
    ...customReg.map(r => ({ reg: r.replace(/\\n/g, '\n'), maxLen: maxSize })),
    ...markdownHeaderRules,
    { reg: /([\n](```[\s\S]*?```|~~~[\s\S]*?~~~))/g, maxLen: maxSize },
    { reg: /(\n\|(?:[^\n|]*\|)+\n\|(?:[:\-\s]*\|)+\n(?:\|(?:[^\n|]*\|)*\n)*)/g, maxLen: chunkSize },
    { reg: /(\n{2,})/g, maxLen: chunkSize },
    { reg: /([\n])/g, maxLen: chunkSize },
    { reg: /([。]|([a-zA-Z])\.\s)/g, maxLen: chunkSize },
    { reg: /([！]|!\s)/g, maxLen: chunkSize },
    { reg: /([？]|\?\s)/g, maxLen: chunkSize },
    { reg: /([；]|;\s)/g, maxLen: chunkSize },
    { reg: /([，]|,\s)/g, maxLen: chunkSize }
  ]

  const checkIsCustomStep = (step) => step < customRegLen
  const checkIsMarkdownSplit = (step) => step >= customRegLen && step <= markdownIndex + customRegLen
  const checkForbidOverlap = (step) => step <= forbidOverlapIndex

  const getSplitTexts = ({ text, step }) => {
    if (step >= stepReges.length) return [{ text, title: '', chunkMaxSize: chunkSize }]
    const isCustomStep = checkIsCustomStep(step)
    const isMarkdownSplit = checkIsMarkdownSplit(step)
    const { reg, maxLen } = stepReges[step]
    const replaceText = (() => {
      if (typeof reg === 'string') {
        let tmpText = text
        reg.split('|').forEach(itemReg => {
          tmpText = tmpText.replaceAll(itemReg,
            isCustomStep ? splitMarker : isMarkdownSplit ? `${splitMarker}$1` : `$1${splitMarker}`
          )
        })
        return tmpText
      }
      return text.replace(reg,
        isCustomStep ? splitMarker : isMarkdownSplit ? `${splitMarker}$1` : `$1${splitMarker}`
      )
    })()
    const splitTexts = replaceText.split(splitMarker).filter(part => part.trim())
    return splitTexts.map(t => {
      const matchTitle = isMarkdownSplit ? t.match(reg)?.[0] || '' : ''
      const chunkMaxSize = (() => {
        if (isCustomStep) return maxLen
        return t.match(reg) === null ? chunkSize : maxLen
      })()
      return { text: isMarkdownSplit ? t.replace(matchTitle, '') : t, title: matchTitle, chunkMaxSize }
    }).filter(item => !!item.title || !!item.text?.trim())
  }

  const getOneTextOverlapText = ({ text, step }) => {
    if (checkForbidOverlap(step) || overlapLen === 0 || step >= stepReges.length) return ''
    const maxOverlapLen = chunkSize * 0.4
    const splitTexts = getSplitTexts({ text, step })
    let overlayText = ''
    for (let i = splitTexts.length - 1; i >= 0; i--) {
      const currentText = splitTexts[i].text
      const newText = currentText + overlayText
      const newTextLen = getTextValidLength(newText)
      if (newTextLen > overlapLen) {
        if (newTextLen > maxOverlapLen) {
          return getOneTextOverlapText({ text: newText, step: step + 1 }) || overlayText
        }
        return newText
      }
      overlayText = newText
    }
    return overlayText
  }

  const splitTextRecursively = ({ text = '', step, lastText, parentTitle = '' }) => {
    const isMarkdownStep = checkIsMarkdownSplit(step)
    const isCustomStep = checkIsCustomStep(step)
    const forbidConcat = isCustomStep

    if (step >= stepReges.length) {
      const combinedText = lastText + text
      const combinedLength = getTextValidLength(combinedText)
      if (combinedLength < maxSize) return [combinedText]
      const chunks = []
      for (let i = 0; i < combinedText.length; i += chunkSize - overlapLen) {
        chunks.push(combinedText.slice(i, i + chunkSize))
      }
      return chunks
    }

    const splitTexts = getSplitTexts({ text, step })
    const chunks = []

    for (let i = 0; i < splitTexts.length; i++) {
      const item = splitTexts[i]
      const maxLen = item.chunkMaxSize
      const lastTextLen = getTextValidLength(lastText)
      const currentText = item.text
      const newText = lastText + currentText
      const newTextLen = getTextValidLength(newText)

      if (strIsMdTable(currentText) && newTextLen > maxLen) {
        if (lastTextLen > 0) { chunks.push(lastText); lastText = '' }
        const { chunks: tableChunks } = markdownTableSplit({ text: currentText, chunkSize: chunkSize * 1.2 })
        chunks.push(...tableChunks)
        continue
      }

      if (isMarkdownStep) {
        const innerChunks = splitTextRecursively({ text: newText, step: step + 1, lastText: '', parentTitle: parentTitle + item.title })
        if (innerChunks.length === 0) { chunks.push(`${parentTitle}${item.title}`); continue }
        chunks.push(...innerChunks.map(chunk =>
          step === markdownIndex + customRegLen ? `${parentTitle}${item.title}${chunk}` : chunk
        ))
        continue
      }

      if (newTextLen > maxLen) {
        const minChunkLen = maxLen * 0.8
        const maxChunkLen = maxLen * 1.2
        if (newTextLen < maxChunkLen) {
          chunks.push(newText)
          lastText = getOneTextOverlapText({ text: newText, step })
          continue
        }
        if (lastTextLen > minChunkLen) {
          chunks.push(lastText)
          lastText = getOneTextOverlapText({ text: lastText, step })
          i--
          continue
        }
        const innerChunks = splitTextRecursively({ text: currentText, step: step + 1, lastText, parentTitle: parentTitle + item.title })
        const lastChunk = innerChunks[innerChunks.length - 1]
        if (!lastChunk) continue
        if (getTextValidLength(lastChunk) < minChunkLen) {
          chunks.push(...innerChunks.slice(0, -1))
          lastText = lastChunk
          continue
        }
        chunks.push(...innerChunks)
        lastText = getOneTextOverlapText({ text: lastChunk, step })
        continue
      }

      if (forbidConcat) { chunks.push(currentText); continue }
      lastText = newText
    }

    if (lastText && chunks[chunks.length - 1] && !chunks[chunks.length - 1].endsWith(lastText)) {
      if (getTextValidLength(lastText) < chunkSize * 0.4) {
        chunks[chunks.length - 1] = chunks[chunks.length - 1] + lastText
      } else {
        chunks.push(lastText)
      }
    } else if (lastText && chunks.length === 0) {
      chunks.push(lastText)
    }
    return chunks
  }

  try {
    const chunks = splitTextRecursively({ text, step: 0, lastText: '', parentTitle: '' })
      .map(chunk => chunk?.replaceAll(codeBlockMarker, '\n')?.trim() || '')
    const chars = chunks.reduce((sum, chunk) => sum + chunk.length, 0)
    return { chunks, chars }
  } catch (err) {
    return { chunks: [text], chars: text.length }
  }
}

// Entry point matching FastGPT's splitText2Chunks
function splitText2Chunks(props) {
  let { text = '' } = props
  const splitWithCustomSign = text.split(CUSTOM_SPLIT_SIGN)
  const splitResult = splitWithCustomSign.map(item => {
    if (strIsMdTable(item)) return markdownTableSplit({ ...props, text: item })
    return commonSplit({ ...props, text: item })
  })
  return {
    chunks: splitResult.map(r => r.chunks).flat().map(chunk => fastGPTSimpleText(chunk)),
    chars: splitResult.reduce((sum, r) => sum + r.chars, 0)
  }
}

function runChunking() {
  if (!cleanedText.value) { chunks.value = []; return }
  const result = splitText2Chunks({
    text: cleanedText.value,
    chunkSize: chunkParams.value.chunkSize,
    overlapRatio: chunkParams.value.overlapRatio,
    paragraphChunkDeep: chunkParams.value.paragraphChunkDeep,
    maxSize: defaultMaxChunkSize
  })
  chunks.value = result.chunks
}

// === FastGPT-compatible HTML→Markdown (turndown + GFM) ===

function createTurndownService() {
  const td = new TurndownService({
    headingStyle: 'atx',
    bulletListMarker: '-',
    codeBlockStyle: 'fenced',
    fence: '```',
    emDelimiter: '_',
    strongDelimiter: '**',
    linkStyle: 'inlined',
    linkReferenceStyle: 'full'
  })
  td.remove(['i', 'script', 'iframe', 'style'])
  td.use(gfm)
  td.addRule('media', {
    filter: ['video', 'source', 'audio'],
    replacement: (content, node) => {
      const src = node.getAttribute('src')
      return src ? `[${src}](${src})` : ''
    }
  })
  return td
}

const turndownService = createTurndownService()

function htmlToMarkdown(html) {
  if (!html) return ''
  const md = turndownService.turndown(html)
  return simpleMarkdownText(md)
}

// === FastGPT simpleText (exact port from tools.ts) ===

function fastGPTSimpleText(text = '') {
  text = text.trim()
  text = text.replace(/([\u4e00-\u9fa5])[\s&&[^\n]]+([\u4e00-\u9fa5])/g, '$1$2')
  text = text.replace(/\r\n|\r/g, '\n')
  text = text.replace(/\n{3,}/g, '\n\n')
  text = text.replace(/[\s&&[^\n]]{2,}/g, ' ')
  text = text.replace(/[\x00-\x08]/g, ' ')
  return text
}

// === FastGPT simpleMarkdownText (exact port from markdown.ts) ===

function simpleMarkdownText(rawText) {
  rawText = fastGPTSimpleText(rawText)

  rawText = rawText.replace(/\[([^\]]+)\]\((.+?)\)/g, (match, linkText, url) => {
    const cleanedLinkText = linkText.replace(/\n/g, ' ').trim()
    if (!url) return ''
    return `[${cleanedLinkText}](${url})`
  })

  const reg1 = /\\([#`!*()+\-_[\]{}\\.])/g
  if (reg1.test(rawText)) {
    rawText = rawText.replace(reg1, '$1')
  }

  rawText = rawText.replace(/\\\\n/g, '\\n')

  const headingPatterns = ['####', '###', '##', '#', '```', '~~~']
  headingPatterns.forEach((item) => {
    const reg = new RegExp(`\\n\\s*${item.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`, 'g')
    if (reg.test(rawText)) {
      rawText = rawText.replace(new RegExp(`(\\n)( *)(${item.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'g'), '$1$3')
    }
  })

  return rawText.trim()
}

// === Parsers ===

async function parsePDF(file) {
  const arrayBuffer = await file.arrayBuffer()
  const pdf = await pdfjsLib.getDocument({ data: new Uint8Array(arrayBuffer) }).promise
  let fullText = ''
  let html = ''

  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i)
    const content = await page.getTextContent()
    const viewport = page.getViewport({ scale: 1 })
    const pageHeight = viewport.height
    const headerThreshold = pageHeight * 0.95
    const footerThreshold = pageHeight * 0.05

    // Filter out headers and footers (top 5% and bottom 5% of page)
    const pageTexts = content.items.filter(token => {
      if (!token.transform) return true
      return token.transform[5] < headerThreshold && token.transform[5] > footerThreshold
    })

    // Merge empty tokens (transfer hasEOL to previous token)
    for (let j = 0; j < pageTexts.length; j++) {
      const item = pageTexts[j]
      if (item.str === '' && pageTexts[j - 1]) {
        pageTexts[j - 1].hasEOL = item.hasEOL
        pageTexts.splice(j, 1)
        j--
      }
    }

    // Build page text with paragraph detection
    const pageText = pageTexts.map(token => {
      const paragraphEnd = token.hasEOL && /([。？！.?!\n\r]|(\r\n))$/.test(token.str)
      return paragraphEnd ? token.str + '\n' : token.str
    }).join('')

    fullText += pageText
    html += `<div style="margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid var(--border-color)"><span style="color:var(--accent-cyan);font-size:0.75rem">第 ${i} 页</span><div style="margin-top:4px">${escapeHtml(pageText)}</div></div>`
  }

  rawText.value = fullText
  parsedResult.value = html
}

async function parseDocx(file) {
  const arrayBuffer = await file.arrayBuffer()
  if (parseMethod.value === 'html') {
    // Match FastGPT: mammoth convertToHtml → html2md (turndown + simpleMarkdownText)
    const result = await mammoth.convertToHtml({ arrayBuffer }, {
      ignoreEmptyParagraphs: false
    })
    const html = result.value
    // rawText stores the HTML for display; markdownText will be computed on demand
    rawText.value = html
    parsedResult.value = html
  } else {
    const result = await mammoth.extractRawText({ arrayBuffer })
    rawText.value = result.value
    parsedResult.value = `<pre style="white-space:pre-wrap;word-break:break-all">${escapeHtml(result.value)}</pre>`
  }
}

async function parseCSV(file) {
  const text = await file.text()

  // Match FastGPT: parse without header option, get raw 2D array
  const csvArr = Papa.parse(text).data
  if (!csvArr || csvArr.length === 0) {
    rawText.value = text
    parsedResult.value = `<pre style="white-space:pre-wrap;word-break:break-all">${escapeHtml(text)}</pre>`
    return
  }

  const header = csvArr[0]

  // formatText: Markdown table (FastGPT exact format)
  const formatText = `| ${header.join(' | ')} |
| ${header.map(() => '---').join(' | ')} |
${csvArr.slice(1).map(row =>
    `| ${row.map(item => String(item ?? '').replace(/\n/g, '\\n')).join(' | ')} |`
  ).join('\n')}`

  rawText.value = text  // rawText = original CSV content
  markdownFormatText.value = formatText  // formatText = MD table

  // For display, render as HTML table (first 50 rows)
  const headers = header.map(String)
  const rows = csvArr.slice(1, 51)
  parsedResult.value = renderTable(headers, rows.map(r => {
    const obj = {}
    headers.forEach((h, i) => { obj[h] = r[i] ?? '' })
    return obj
  }))
}

const CUSTOM_SPLIT_SIGN = '-----CUSTOM_SPLIT_SIGN-----'
const defaultMaxChunkSize = 8000

async function parseXLSX(file) {
  const arrayBuffer = await file.arrayBuffer()
  const workbook = XLSX.read(arrayBuffer, { type: 'array' })
  xlsxWorkbook.value = workbook
  sheetNames.value = workbook.SheetNames
  if (selectedSheet.value === null || !workbook.SheetNames.includes(selectedSheet.value)) {
    selectedSheet.value = workbook.SheetNames[0]
  }
  renderAllXLSXSheets(workbook)
}

function renderAllXLSXSheets(workbook) {
  // Match FastGPT: iterate ALL sheets
  const allSheets = workbook.SheetNames.map(name => {
    const sheet = workbook.Sheets[name]
    const data = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' })
    return { name, data }
  })

  // rawText: all sheets as CSV joined by newline
  const raw = allSheets.map(({ data }) =>
    data.map(row => row.join(',')).join('\n')
  ).join('\n')

  // formatText: all sheets as MD tables joined by CUSTOM_SPLIT_SIGN
  const formatText = allSheets.map(({ data }) => {
    const header = data[0]
    if (!header) return ''
    return `| ${header.join(' | ')} |
| ${header.map(() => '---').join(' | ')} |
${data.slice(1).map(row =>
      `| ${row.map(cell => String(cell ?? '').replace(/\n/g, '\\n')).join(' | ')} |`
    ).join('\n')}`
  }).filter(Boolean).join(CUSTOM_SPLIT_SIGN)

  rawText.value = raw
  markdownFormatText.value = formatText

  // Display: show first sheet as HTML table
  const firstSheet = allSheets[0]
  if (firstSheet && firstSheet.data.length > 0) {
    const headers = firstSheet.data[0].map(String)
    const rows = firstSheet.data.slice(1, 51)
    parsedResult.value = renderTable(headers, rows.map(r => {
      const obj = {}
      headers.forEach((h, i) => { obj[h] = r[i] ?? '' })
      return obj
    }))
  }
}

async function parseText(file) {
  const text = await file.text()
  rawText.value = text
  parsedResult.value = `<pre style="white-space:pre-wrap;word-break:break-all">${escapeHtml(text)}</pre>`
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function renderTable(headers, rows) {
  let html = '<table class="data-table"><thead><tr>'
  headers.forEach(h => { html += `<th>${escapeHtml(String(h))}</th>` })
  html += '</tr></thead><tbody>'
  rows.forEach(row => {
    html += '<tr>'
    headers.forEach(h => {
      const val = row[h] ?? ''
      html += `<td>${escapeHtml(String(val))}</td>`
    })
    html += '</tr>'
  })
  html += '</tbody></table>'
  return html
}

function simpleText(text) {
  let result = text
  if (cleanOptions.value.trim) {
    result = result.trim()
  }
  if (cleanOptions.value.removeChineseSpace) {
    result = result.replace(/([\u4e00-\u9fa5])[\s&&[^\n]]+([\u4e00-\u9fa5])/g, '$1$2')
  }
  if (cleanOptions.value.normalizeNewline) {
    result = result.replace(/\r\n|\r/g, '\n')
  }
  if (cleanOptions.value.removeEmptyLines) {
    result = result.replace(/\n{3,}/g, '\n\n')
  }
  if (cleanOptions.value.collapseWhitespace) {
    result = result.replace(/[\s&&[^\n]]{2,}/g, ' ')
  }
  result = result.replace(/[\x00-\x08]/g, ' ')
  return result
}

// (old chunk functions removed — replaced by FastGPT textSplitter above)

// Watch parse method change → re-parse
watch(parseMethod, async () => {
  if (!uploadedFile.value) return
  loading.value = true
  try {
    const ext = fileInfo.value.ext
    if (ext === 'docx' || ext === 'doc') {
      await parseDocx(uploadedFile.value)
    } else if (ext === 'csv') {
      await parseCSV(uploadedFile.value)
    }
  } catch (err) {
    parsedResult.value = `<div style="color:var(--accent-red)">解析失败: ${err.message}</div>`
  }
  loading.value = false
})

watch(selectedSheet, (val) => {
  if (val && xlsxWorkbook.value) {
    renderAllXLSXSheets(xlsxWorkbook.value)
  }
})

// Image preview
watch(uploadedFile, (file) => {
  if (!file) { imagePreview.value = null; return }
  const ext = getExt(file.name)
  if (['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp'].includes(ext)) {
    const reader = new FileReader()
    reader.onload = (e) => { imagePreview.value = e.target.result }
    reader.readAsDataURL(file)
  } else {
    imagePreview.value = null
  }
})
</script>
