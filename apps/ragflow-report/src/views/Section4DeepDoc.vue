<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§4 文档解析 DeepDoc</h2>
      <p>RAGFlow 深度文档理解引擎 — 6 种 PDF 解析策略、自研 ONNX 模型链与 OCR 流水线</p>
    </div>

    <!-- Card 1: 解析架构 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔄</span> 解析架构总览</div>
      <div class="flow-diagram">
        <div class="flow-steps">
          <div class="flow-step primary">chunk()<br><small>filename, binary</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step accent">文件类型检测<br><small>按扩展名分发</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">多格式解析器<br><small>见下方分支</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step success">输出<br><small>sections[] + tables[] + figures[]</small></div>
        </div>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>格式分发矩阵：</strong>
        <code>.pdf</code> → PARSERS（6 种策略可选） ·
        <code>.docx</code> → DocxParser ·
        <code>.xlsx</code> → ExcelParser ·
        <code>.pptx</code> → PptParser ·
        <code>.html</code> → HtmlParser ·
        <code>.md</code> → MarkdownParser ·
        <code>.json</code> → JsonParser ·
        <code>.txt</code> → TxtParser ·
        <code>.eml</code> → EmailParser
      </div>
    </div>

    <!-- Card 2: PDF 解析策略 -->
    <div class="card">
      <div class="card-title"><span class="icon">📄</span> PDF 解析策略（7 种）</div>
      <table class="data-table">
        <thead>
          <tr><th>策略名</th><th>核心引擎</th><th>关键能力</th><th>适用场景</th></tr>
        </thead>
        <tbody>
          <tr v-for="s in pdfStrategies" :key="s.name">
            <td><strong>{{ s.name }}</strong></td>
            <td><code>{{ s.engine }}</code></td>
            <td>{{ s.capability }}</td>
            <td>{{ s.scenario }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Card 3: DeepDoc 解析流水线 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔧</span> DeepDoc 解析流水线（6 步）</div>
      <div class="flow-diagram">
        <div class="flow-steps">
          <div class="flow-step" v-for="(step, idx) in pipelineSteps" :key="step.name">
            <strong>{{ step.name }}</strong><br><small>{{ step.desc }}</small>
            <span v-if="idx < pipelineSteps.length - 1" class="flow-arrow">→</span>
          </div>
        </div>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>流水线细节：</strong>
        <ol style="margin:6px 0 0 18px;padding:0;line-height:1.8;">
          <li v-for="d in pipelineDetails" :key="d">{{ d }}</li>
        </ol>
      </div>
    </div>

    <!-- Card 4: AI/ML 模型矩阵 -->
    <div class="card">
      <div class="card-title"><span class="icon">🧠</span> AI/ML 模型矩阵</div>
      <table class="data-table">
        <thead>
          <tr><th>模型文件</th><th>功能</th><th>架构</th><th>输出</th></tr>
        </thead>
        <tbody>
          <tr v-for="m in aiModels" :key="m.file">
            <td><code>{{ m.file }}</code></td>
            <td><strong>{{ m.func }}</strong></td>
            <td>{{ m.arch }}</td>
            <td>{{ m.output }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Card 5: OCR 流水线 -->
    <div class="card">
      <div class="card-title"><span class="icon">👁️</span> OCR 流水线</div>
      <div class="flow-diagram">
        <div class="flow-steps">
          <div class="flow-step primary">TextDetector<br><small>DB 模型</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">预处理<br><small>Resize + Normalize</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step accent">ONNX 推理<br><small>det.onnx</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">DBPostProcess<br><small>阈值 + Box</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">排序 &amp; 裁剪<br><small>y→x 排序</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step primary">TextRecognizer<br><small>CTC 模型</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step accent">48×320 ONNX<br><small>rec.onnx</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step success">CTCLabelDecode<br><small>texts[]</small></div>
        </div>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>OCR 加速：</strong>支持多 GPU 批量 OCR（<code>gpu_id</code> 列表轮转），每页独立调度，可并行处理数百页 PDF。
      </div>
    </div>

    <!-- Card 6: 优势与不足 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚖️</span> 优势与不足</div>
      <div class="pros-cons-grid">
        <div class="pros">
          <div class="pros-cons-title">✅ 优势</div>
          <ul class="feature-list">
            <li v-for="p in pros" :key="p">{{ p }}</li>
          </ul>
        </div>
        <div class="cons">
          <div class="pros-cons-title">⚠️ 不足</div>
          <ul class="feature-list">
            <li v-for="c in cons" :key="c">{{ c }}</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 引用 -->
    <div class="source-ref-list">
      <span class="source-ref">ragflow/app/rag/app/parse.py</span>
      <span class="source-ref">ragflow/rag/app/naive.py</span>
      <span class="source-ref">deepdoc/ocr/ocr.py</span>
      <span class="source-ref">deepdoc/ocr/text_recognizer.py</span>
      <span class="source-ref">deepdoc/vision/layout_recognizer.py</span>
      <span class="source-ref">deepdoc/vision/table_structure_recognizer.py</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// PDF 解析策略
const pdfStrategies = ref([
  { name: 'deepdoc', engine: '自研 ONNX Runtime', capability: 'OCR + 布局检测 + 表格结构识别', scenario: '默认策略，高精度复杂文档' },
  { name: 'plaintext', engine: 'pypdf / pdfplumber', capability: '快速提取内嵌文本', scenario: '纯文字 PDF，速度优先' },
  { name: 'vision', engine: 'Vision LLM (GPT-4V 等)', capability: '视觉大模型端到端理解', scenario: '复杂版面、手写体、公式' },
  { name: 'mineru', engine: 'MinerU API', capability: '高精度版面还原 + 公式', scenario: '学术论文、技术文档' },
  { name: 'docling', engine: 'IBM Docling', capability: '结构化文档转换', scenario: '企业文档批量处理' },
  { name: 'paddleocr', engine: 'PaddleOCR-VL', capability: '视觉语言 OCR', scenario: '中文场景优化' },
  { name: 'tcadp', engine: '腾讯云文档解析', capability: '云端高精度解析', scenario: '需要云端能力的场景' }
])

// DeepDoc 流水线步骤
const pipelineSteps = ref([
  { name: '__images__', desc: '页面渲染' },
  { name: '_layouts_rec_', desc: '布局检测' },
  { name: '_table_transformer_job_', desc: '表格结构' },
  { name: '_text_merge_', desc: '文字合并' },
  { name: '_naive_vertical_merge_', desc: '纵向合并' },
  { name: '_extract_table_figure_', desc: '提取表格图片' }
])

// 流水线详细说明
const pipelineDetails = ref([
  '__images__：pdfplumber 提取页面 → 渲染为图像 → OCR 文字 + PDF 内嵌文字合并',
  '_layouts_rec_：YOLOv10 布局检测 → 10 种布局类型（标题/段落/表格/图片/页眉页脚等）',
  '_table_transformer_job_：TSR 表格结构识别模型 → 行/列/表头/合并单元格解析',
  '_text_merge_：KMeans 列检测 → XGBoost 纵向合并（同一列内相邻文本块）',
  '_naive_vertical_merge_：标点感知纵向合并（句号/逗号/括号等决定是否合并）',
  '_extract_table_figure_：表格区域 OCR + TSR → HTML 输出；图片裁剪 → img_id；跨页内容合并'
])

// AI/ML 模型矩阵
const aiModels = ref([
  { file: 'det.onnx', func: '文本检测', arch: 'DB (Differentiable Binarization)', output: '文本区域 boxes[]' },
  { file: 'rec.onnx', func: '文字识别', arch: 'CRNN + CTC', output: '识别文字 texts[]' },
  { file: 'layout.onnx', func: '布局检测', arch: 'YOLOv10', output: '10 种布局类型 + bbox' },
  { file: 'tsr.onnx', func: '表格结构识别', arch: 'Table Structure Recognition', output: '行/列/表头/合并单元格' },
  { file: 'updown_concat_xgb.model', func: '文字合并', arch: 'XGBoost 二分类', output: '是否纵向合并 (0/1)' },
  { file: 'ocr.res', func: 'CTC 字符字典', arch: '字符映射表', output: '索引 → 字符映射' }
])

// 优势
const pros = ref([
  '6 种 PDF 解析策略灵活可选，覆盖从快速提取到高精度版面还原',
  '自研 ONNX 模型离线可用，无需外部 API 调用',
  '支持多 GPU 批量 OCR 加速，处理数百页文档效率高',
  '10 种布局类型检测，精准区分标题、段落、表格、图片等',
  '表格自动旋转 + 跨页合并，复杂表格也能完整提取',
  '多格式支持（PDF/DOCX/XLSX/PPTX/HTML/MD/JSON/TXT/EML）'
])

// 不足
const cons = ref([
  '默认 deepdoc 策略速度较慢（需 ONNX 推理 + OCR）',
  '模型文件较大（布局检测 + TSR + OCR 约数百 MB）',
  '手写体识别能力有限，依赖外部 Vision LLM 策略',
  '复杂多栏排版可能遗漏跨栏文本',
  '无边框表格识别较弱，依赖 TSR 模型精度',
  '部分格式（如 DOCX）依赖 Apache Tika，增加部署复杂度'
])
</script>
