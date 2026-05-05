<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§11 AI 数据 ETL</h2>
      <p>利用内置的数据摄入流水线清洗并处理多格式数据，将其结构化为丰富的语义表示，从而实现卓越的检索效果。</p>
    </div>

    <!-- ETL 流水线流程图 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚙️</span>数据摄入流水线</div>
      <div class="flow-diagram">
        <div class="flow-steps">
          <div class="flow-step primary">
            📁 多格式数据<br><small>PDF / DOCX / PPTX</small><br><small>XLSX / HTML / 图片 / 音频</small>
          </div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">
            🔍 DeepDoc 解析<br><small>OCR + 布局识别</small><br><small>表格结构化</small>
          </div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">
            🧹 数据清洗<br><small>去噪 + 规范化</small><br><small>语言检测</small>
          </div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">
            ✂️ 智能分块<br><small>15 种策略</small><br><small>场景优化</small>
          </div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">
            🔢 向量化<br><small>35+ 模型</small><br><small>Embedding</small>
          </div>
          <div class="flow-arrow">→</div>
          <div class="flow-step primary">
            🗄️ 知识库<br><small>ES / Infinity</small><br><small>向量存储</small>
          </div>
        </div>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>ETL 流程：</strong>从多格式原始文件出发，经过 DeepDoc 深度解析（6 种 PDF 策略 + OCR）、数据清洗（去噪/规范化/语言检测）、智能分块（15 种分块策略按场景自动选择）、向量化（35+ Embedding 模型可选），最终写入向量引擎构建知识库。
      </div>
    </div>

    <!-- 支持的数据格式 -->
    <div class="card">
      <div class="card-title"><span class="icon">📊</span>支持的数据格式与处理方式</div>
      <table class="data-table">
        <thead>
          <tr><th>数据格式</th><th>解析方式</th><th>分块策略</th><th>向量化</th></tr>
        </thead>
        <tbody>
          <tr v-for="f in formats" :key="f.name">
            <td><strong>{{ f.icon }} {{ f.name }}</strong></td>
            <td>{{ f.parse }}</td>
            <td>{{ f.chunk }}</td>
            <td>{{ f.vector }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ETL 核心能力 -->
    <div class="two-col">
      <div class="card">
        <div class="card-title"><span class="icon">🔬</span>DeepDoc 解析引擎</div>
        <ul class="feature-list">
          <li>6 种 PDF 解析策略 — 按文档类型自动选择最优方案</li>
          <li>ONNX Runtime 自定义模型 — 精准版面分析与元素定位</li>
          <li>PaddleOCR 光学识别 — 多语言文字提取，支持手写体</li>
          <li>表格结构化提取 — 保留单元格关系与合并信息</li>
          <li>公式识别 — LaTeX 公式精准还原</li>
        </ul>
      </div>
      <div class="card">
        <div class="card-title"><span class="icon">✂️</span>15 种分块策略</div>
        <ul class="feature-list">
          <li>通用文本分块 — 按段落/标题/语义切分</li>
          <li>表格分块器 — 保留行列结构的表格切分</li>
          <li>图片分块器 — 视觉内容感知的智能分块</li>
          <li>音频分块器 — ASR 转录后按时间戳切分</li>
          <li>按文档类型自动选择 — PDF/DOCX/PPTX 各有专属策略</li>
          <li>自定义分块参数 — 块大小、重叠率可配置</li>
        </ul>
      </div>
    </div>

    <!-- Embedding 生态 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔢</span>Embedding 向量化生态</div>
      <div class="metrics-grid">
        <div class="metric-card" v-for="m in metrics" :key="m.label">
          <div class="metric-value">{{ m.value }}</div>
          <div class="metric-label">{{ m.label }}</div>
        </div>
      </div>
      <div class="highlight-block">
        <strong>35+ 嵌入提供商：</strong>支持 OpenAI、Cohere、BAAI/bge 等主流模型，同时支持本地部署方案（TEI、Ollama、Xinference、VLLM），tiktoken cl100k_base 统一分词，动态维度适配。
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 支持的数据格式
const formats = ref([
  { icon: '📄', name: 'PDF', parse: 'DeepDoc 6 种策略', chunk: '按文档类型自动选择', vector: '35+ 模型可选' },
  { icon: '📝', name: 'DOCX', parse: 'python-docx', chunk: '按段落/标题', vector: '动态维度' },
  { icon: '📊', name: 'PPTX', parse: 'python-pptx', chunk: '按幻灯片', vector: 'cosine 相似度' },
  { icon: '📈', name: 'XLSX', parse: 'openpyxl', chunk: '表格分块器', vector: '支持 TEI 本地部署' },
  { icon: '🌐', name: 'HTML', parse: 'BeautifulSoup5', chunk: '文本分块', vector: '支持 Ollama' },
  { icon: '🖼️', name: '图片', parse: 'OCR + Vision LLM', chunk: '视觉内容分块', vector: '支持 Xinference' },
  { icon: '🎵', name: '音频', parse: 'ASR 转录', chunk: '音频分块器', vector: '支持 VLLM' }
])

// 核心指标
const metrics = ref([
  { value: '35+', label: 'Embedding 提供商' },
  { value: '6', label: 'PDF 解析策略' },
  { value: '15', label: '分块策略' },
  { value: '4', label: '向量引擎' },
  { value: '3+', label: '本地部署方案' },
  { value: '100+', label: '支持文件格式' }
])
</script>
