<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§3 文档上传</h2>
      <p>RAGFlow 文档上传流水线、文件格式支持与存储后端详解</p>
    </div>

    <!-- 上传流水线 -->
    <div class="card">
      <div class="card-title"><span class="icon">⬆</span>文档上传流水线</div>
      <div class="flow-diagram">
        <div class="flow-steps">
          <div class="flow-step">check_doc_health<br><small>健康检查</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">filename_type<br><small>MIME 检测</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">duplicate_name<br><small>文件去重</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step primary">MinIO 存储<br><small>对象写入</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">read_potential_broken_pdf<br><small>PDF 修复</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">thumbnail_img<br><small>缩略图</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">DocumentService.insert<br><small>MySQL 入库</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">FileService.add_file_from_kb<br><small>文件关联</small></div>
        </div>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>流水线说明：</strong>上传请求经健康检查后，通过 MIME 检测确定文件类型，去重后写入 MinIO 对象存储。随后对可能损坏的 PDF 执行自动修复，生成缩略图，最后将文档元数据写入 MySQL 并完成知识库文件关联。
      </div>
    </div>

    <!-- 文件格式 + 存储后端 -->
    <div class="two-col">
      <!-- 支持的文件格式 -->
      <div class="card">
        <div class="card-title"><span class="icon">📄</span>支持的文件格式</div>
        <table class="data-table">
          <thead>
            <tr><th>类别</th><th>扩展名</th></tr>
          </thead>
          <tbody>
            <tr v-for="f in fileFormats" :key="f.category">
              <td><strong>{{ f.category }}</strong></td>
              <td><code>{{ f.extensions }}</code></td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 存储后端 -->
      <div class="card">
        <div class="card-title"><span class="icon">💾</span>存储后端</div>
        <table class="data-table">
          <thead>
            <tr><th>后端</th><th>配置标识</th><th>说明</th></tr>
          </thead>
          <tbody>
            <tr v-for="b in storageBackends" :key="b.name">
              <td><strong>{{ b.name }}</strong></td>
              <td><code>{{ b.config }}</code></td>
              <td>{{ b.desc }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 文档生命周期 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔄</span>文档生命周期</div>
      <div class="flow-diagram">
        <div class="flow-steps">
          <div class="flow-step">UNSTART<br><small>run=0</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step" style="font-size:0.75rem;">用户点击 Run</div>
          <div class="flow-arrow">→</div>
          <div class="flow-step primary">RUNNING<br><small>run=1</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step success">DONE<br><small>run=3</small></div>
        </div>
        <div class="flow-steps" style="margin-top:10px; justify-content:center;">
          <div class="flow-step" style="opacity:0.5;">（RUNNING 分支）</div>
          <div class="flow-arrow">→</div>
          <div class="flow-step" style="border-color:var(--warning, #e6a23c);">CANCEL<br><small>run=2</small></div>
          <div style="margin:0 8px; color:var(--text-muted);">/</div>
          <div class="flow-step" style="border-color:var(--danger, #f56c6c); color:var(--danger, #f56c6c);">FAIL<br><small>prog=-1</small></div>
        </div>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>状态流转：</strong>文档上传后处于 <code>UNSTART</code> 状态，用户手动触发 Run 后进入 <code>RUNNING</code>，解析成功转为 <code>DONE</code>；若用户取消或解析失败，则分别进入 <code>CANCEL</code> 或 <code>FAIL</code> 终态。
      </div>
    </div>

    <!-- 优势与不足 -->
    <div class="pros-cons-grid">
      <div class="card">
        <div class="card-title"><span class="icon">✅</span>优势</div>
        <ul class="feature-list">
          <li v-for="p in pros" :key="p">{{ p }}</li>
        </ul>
      </div>
      <div class="card">
        <div class="card-title"><span class="icon">⚠️</span>不足</div>
        <ul class="feature-list">
          <li v-for="c in cons" :key="c">{{ c }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 文件格式分类
const fileFormats = ref([
  { category: 'PDF', extensions: '.pdf' },
  { category: '文档', extensions: '.doc .docx .ppt .pptx .xls .xlsx .csv .txt .md .html .json .py .js ...' },
  { category: '音频', extensions: '.wav .mp3 .aac .flac ...' },
  { category: '视觉', extensions: '.jpg .jpeg .png .gif .svg .webp .mp4 .avi ...' }
])

// 存储后端
const storageBackends = ref([
  { name: 'MinIO', config: 'RAGFLOWMinio', desc: '默认对象存储' },
  { name: 'AWS S3', config: 'RAGFLOWAwsS3', desc: 'Amazon S3 兼容' },
  { name: 'Azure', config: 'RAGFLOWAzureSpnBlob / SasBlob', desc: 'Azure Blob Storage' },
  { name: '阿里云 OSS', config: 'RAGFLOWAliyunOss', desc: '阿里云对象存储' },
  { name: 'Google GCS', config: 'RAGFLOWGcs', desc: 'Google Cloud Storage' },
  { name: 'OpenDAL', config: 'RAGFLOWOpendal', desc: '通用数据访问层' }
])

// 优势
const pros = ref([
  '极广泛文件类型 — 覆盖 PDF、Office 文档、代码、音频、图片等数十种格式',
  '6 种存储后端 — MinIO / S3 / Azure / OSS / GCS / OpenDAL，灵活对接多云环境',
  '自动修复损坏 PDF — 内置 read_potential_broken_pdf 检测并修复破损 PDF 文件',
  '缩略图 + 进度消息 — 上传即生成缩略图，解析过程通过进度消息实时反馈'
])

// 不足
const cons = ref([
  '部分格式依赖 Tika — 如 PPT/PPTX 等格式需额外部署 Apache Tika 服务',
  'MinIO 配置复杂 — 默认存储后端需独立部署并配置访问密钥',
  '无文件大小限制 — 未内置上传大小校验，大文件可能耗尽内存',
  '大文件无断点续传 — 上传中断后需重新上传，缺乏分片续传机制'
])
</script>
