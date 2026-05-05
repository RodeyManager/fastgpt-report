<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§3 文档上传机制</h2>
      <p>MaxKB 文档导入通道、文件存储策略与支持的文件格式全解析</p>
    </div>

    <!-- 上传通道 -->
    <div class="card">
      <div class="card-title"><span class="icon">📡</span> 3.1 上传通道</div>
      <p style="margin-bottom:12px;color:var(--text-secondary);">MaxKB 提供 <strong>4 种文档导入通道</strong>，覆盖文档分割、QA 问答、表格、Web 爬虫等场景：</p>
      <table class="data-table">
        <thead>
          <tr><th>通道</th><th>端点</th><th>解析器</th><th>输入格式</th></tr>
        </thead>
        <tbody>
          <tr v-for="ch in channels" :key="ch.name">
            <td><strong>{{ ch.name }}</strong></td>
            <td><code>{{ ch.endpoint }}</code></td>
            <td>{{ ch.parser }}</td>
            <td>{{ ch.formats }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 文件存储机制 -->
    <div class="card">
      <div class="card-title"><span class="icon">🗄️</span> 3.2 文件存储机制</div>
      <div class="code-block">
        <pre><code># apps/knowledge/models/knowledge.py - File模型
class File(AppModelMixin):
    file_name = models.CharField(max_length=256)
    sha256_hash = models.CharField(max_length=64)  # SHA256去重
    loid = models.IntegerField()                     # PostgreSQL Large Object ID
    source_type = models.CharField(max_length=5)
    source_id = models.UUIDField()</code></pre>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>存储策略：</strong>
        <ul style="margin:8px 0 0 16px;line-height:1.8;">
          <li v-for="s in storageStrategies" :key="s">{{ s }}</li>
        </ul>
      </div>
      <div class="highlight-block" style="margin-top:8px;">
        📂 源码路径: <code>apps/knowledge/models/knowledge.py</code> (File类)<br>
        📂 OSS服务: <code>apps/oss/serializers/file.py</code>
      </div>
    </div>

    <!-- 上传数据流 -->
    <div class="card">
      <div class="card-title"><span class="icon">◈</span> 上传数据流</div>
      <div class="flow-diagram">
        <div class="flow-steps">
          <div class="flow-step primary">用户上传<br><small>文件 / URL</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">SHA256 去重<br><small>计算哈希值</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">ZIP 压缩<br><small>压缩文件内容</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">Large Object<br><small>PostgreSQL LO</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step primary">解析链处理<br><small>split_handles</small></div>
        </div>
      </div>
    </div>

    <!-- 支持的文件格式 -->
    <div class="card">
      <div class="card-title"><span class="icon">📄</span> 3.3 支持的文件格式</div>
      <table class="data-table">
        <thead>
          <tr><th>格式</th><th>扩展名</th><th>解析库</th><th>复杂度</th></tr>
        </thead>
        <tbody>
          <tr v-for="f in fileFormats" :key="f.format">
            <td><strong>{{ f.format }}</strong></td>
            <td><code>{{ f.ext }}</code></td>
            <td>{{ f.parser }}</td>
            <td>{{ f.complexity }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 4种上传通道
const channels = ref([
  { name: '文档分割上传', endpoint: '/document/split', parser: 'split_handles 链', formats: 'PDF/DOCX/HTML/XLSX/XLS/CSV/ZIP/TXT/MD' },
  { name: 'QA问答导入', endpoint: '/document/qa', parser: 'parse_qa_handle_list', formats: 'XLSX/XLS/CSV/MD/ZIP' },
  { name: '表格导入', endpoint: '/document/table', parser: 'parse_table_handle_list', formats: 'XLSX/XLS/CSV' },
  { name: 'Web导入', endpoint: '/document/web', parser: 'Fork 爬虫', formats: 'URL + CSS选择器' }
])

// 存储策略
const storageStrategies = ref([
  '使用 PostgreSQL Large Objects 存储（loid字段）',
  '文件内容 ZIP 压缩后存储',
  'SHA256 去重：相同文件共享同一个 Large Object',
  '删除时检查引用计数，安全释放'
])

// 支持的文件格式
const fileFormats = ref([
  { format: 'PDF', ext: '.pdf', parser: 'pypdf', complexity: '⭐⭐⭐ (3种策略)' },
  { format: 'Word', ext: '.docx, .doc', parser: 'python-docx', complexity: '⭐⭐' },
  { format: 'HTML', ext: '.html, .htm', parser: 'BeautifulSoup + markdownify', complexity: '⭐' },
  { format: 'Excel', ext: '.xlsx', parser: 'openpyxl', complexity: '⭐⭐' },
  { format: 'Excel(旧)', ext: '.xls', parser: 'xlrd', complexity: '⭐' },
  { format: 'CSV', ext: '.csv', parser: 'stdlib csv', complexity: '⭐' },
  { format: 'Markdown', ext: '.md', parser: '直接读取', complexity: '⭐' },
  { format: '纯文本', ext: '.txt', parser: 'charset_normalizer', complexity: '⭐' },
  { format: 'ZIP压缩包', ext: '.zip', parser: '递归解压+委托内部handler', complexity: '⭐⭐⭐' }
])
</script>
