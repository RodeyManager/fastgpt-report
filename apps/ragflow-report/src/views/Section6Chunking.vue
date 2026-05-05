<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§6 文本分块</h2>
      <p>RAGFlow 15 种专用分块策略、分块流水线与 Overlap 机制详解</p>
    </div>

    <!-- 分块策略矩阵 -->
    <div class="card">
      <div class="card-title"><span class="icon">🧩</span>分块策略矩阵（15 种）</div>
      <table class="data-table">
        <thead>
          <tr><th>策略</th><th>算法</th><th>支持格式</th><th>适用场景</th></tr>
        </thead>
        <tbody>
          <tr v-for="s in strategies" :key="s.name">
            <td><strong>{{ s.name }}</strong></td>
            <td>{{ s.algorithm }}</td>
            <td><code>{{ s.formats }}</code></td>
            <td>{{ s.scene }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分块流水线 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚙</span>分块流水线</div>
      <div class="flow-diagram">
        <div class="flow-steps">
          <div class="flow-step">文档二进制<br><small>MinIO</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step primary">FACTORY[parser_id].chunk<br><small>策略分块</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">sections[]<br><small>文本段落</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">xxhash.xxh64<br><small>content+doc_id</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">PIL→JPEG→MinIO<br><small>图片上传</small></div>
        </div>
        <div class="flow-steps" style="margin-top:10px; justify-content:center;">
          <div class="flow-step" style="opacity:0.6;">[可选] auto_keywords</div>
          <div style="margin:0 6px; color:var(--text-muted);">+</div>
          <div class="flow-step" style="opacity:0.6;">auto_questions</div>
          <div style="margin:0 6px; color:var(--text-muted);">+</div>
          <div class="flow-step" style="opacity:0.6;">metadata</div>
          <div class="flow-arrow">→</div>
          <div class="flow-step success">LLM 增强<br><small>关键词/问题/元数据</small></div>
        </div>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>流水线说明：</strong>文档二进制从 MinIO 读取后，通过 FACTORY 工厂按 <code>parser_id</code> 选取对应分块器执行 <code>chunk()</code>，生成 sections 数组。每个 chunk 通过 <code>xxhash.xxh64(content + doc_id)</code> 生成唯一 ID。图片经 PIL 转为 JPEG 上传 MinIO。可选启用 LLM 自动提取关键词、问题和元数据。
      </div>
    </div>

    <!-- Overlap 代码 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔄</span>Overlap 重叠机制</div>
      <div class="code-block">
        <div class="code-lang">python</div>
        <pre><code># RAGFlow chunk overlap 核心逻辑（简化）
if tk_nums[-1] &gt;= chunk_token_num * (1 + overlapped_percent / 100):
    sections.append("".join(tokens[-total_tokens:]))
    # 重叠窗口：保留尾部 overlapped_percent% 的 token
    # 与下一个 chunk 的头部重叠，保证语义连续性</code></pre>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>Token 计数：</strong>使用 <code>tiktoken cl100k_base</code> 编码进行 token 计数，确保分块大小精确可控。重叠率范围 0–90%，通过 <code>overlapped_percent</code> 参数调节。
      </div>
    </div>

    <!-- 分块参数 + Chunk 数据模型 -->
    <div class="two-col">
      <!-- 分块参数 -->
      <div class="card">
        <div class="card-title"><span class="icon">🎛</span>分块参数</div>
        <table class="data-table">
          <thead>
            <tr><th>参数</th><th>默认值</th><th>说明</th></tr>
          </thead>
          <tbody>
            <tr v-for="p in params" :key="p.name">
              <td><strong><code>{{ p.name }}</code></strong></td>
              <td><code>{{ p.default }}</code></td>
              <td>{{ p.desc }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Chunk 数据模型 -->
      <div class="card">
        <div class="card-title"><span class="icon">📦</span>Chunk 数据模型</div>
        <table class="data-table">
          <thead>
            <tr><th>字段</th><th>生成方式</th><th>说明</th></tr>
          </thead>
          <tbody>
            <tr v-for="f in chunkFields" :key="f.name">
              <td><strong><code>{{ f.name }}</code></strong></td>
              <td>{{ f.gen }}</td>
              <td>{{ f.desc }}</td>
            </tr>
          </tbody>
        </table>
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

// 15 种分块策略矩阵
const strategies = ref([
  { name: 'naive', algorithm: '分隔符 + token 合并', formats: '全部', scene: '通用场景' },
  { name: 'book', algorithm: 'hierarchical_merge 5 层', formats: 'DOCX/PDF/TXT/HTML', scene: '书籍文档' },
  { name: 'paper', algorithm: '标题频率 + 两栏检测', formats: 'PDF', scene: '学术论文' },
  { name: 'laws', algorithm: 'tree_merge depth=2', formats: 'DOCX/PDF/TXT/MD', scene: '法律文书' },
  { name: 'qa', algorithm: '问答对提取', formats: 'XLSX/CSV/PDF/MD', scene: 'FAQ 文档' },
  { name: 'table', algorithm: '每行 chunk + 类型化', formats: 'XLSX/CSV/TXT', scene: '表格数据' },
  { name: 'manual', algorithm: '层级章节解析', formats: 'PDF/DOCX', scene: '操作手册' },
  { name: 'presentation', algorithm: '每页 chunk', formats: 'PPT/PDF', scene: '演示文稿' },
  { name: 'picture', algorithm: 'OCR + Vision LLM', formats: '图片/视频', scene: '视觉内容' },
  { name: 'one', algorithm: '整个文档为 1 chunk', formats: '全部', scene: '短文档' },
  { name: 'resume', algorithm: '远程 API 解析', formats: 'PDF/DOCX/TXT', scene: '简历文档' },
  { name: 'audio', algorithm: 'ASR → 单 chunk', formats: '音频', scene: '语音内容' },
  { name: 'email', algorithm: '邮件头+体+附件递归', formats: 'EML', scene: '邮件文档' },
  { name: 'tag', algorithm: '内容-标签对提取', formats: 'XLSX/CSV/TXT', scene: '标签数据' },
  { name: 'knowledge_graph', algorithm: 'naive + 实体提取', formats: '全部', scene: '知识图谱' }
])

// 分块参数
const params = ref([
  { name: 'chunk_token_num', default: '512', desc: '每个 chunk 的目标 token 数' },
  { name: 'overlapped_percent', default: '0–90%', desc: '相邻 chunk 的重叠比例' },
  { name: 'delimiter', default: '\\n', desc: '文本分隔符（naive 策略使用）' }
])

// Chunk 数据模型字段
const chunkFields = ref([
  { name: 'id', gen: 'xxhash64', desc: 'chunk 唯一标识（content+doc_id 哈希）' },
  { name: 'doc_id / kb_id', gen: '外键关联', desc: '所属文档与知识库' },
  { name: 'content_with_weight', gen: '分块器输出', desc: '带权重的文本内容' },
  { name: 'content_ltks / content_sm_ltks', gen: '分词器', desc: '全文检索用分词与平滑分词' },
  { name: 'page_num_int', gen: '解析器', desc: '页码定位（PDF/DOCX）' },
  { name: 'position_int', gen: '解析器', desc: '页内坐标定位（x0,y0,x1,y1）' },
  { name: 'important_kwd / important_tks', gen: 'LLM / 规则', desc: '关键词及其 token' },
  { name: 'question_kwd / question_tks', gen: 'LLM', desc: '自动生成问题及其 token' },
  { name: 'doc_type_kwd', gen: '分块器', desc: '文档类型标签' },
  { name: 'img_id', gen: 'MinIO', desc: '关联图片对象 ID' }
])

// 优势
const pros = ref([
  '15 种专用分块器 — 覆盖书籍、论文、法律、表格、简历、音频、邮件等几乎所有文档类型',
  '自动关键词 / 问题 / 元数据 — 可选 LLM 增强提取，提升检索召回率',
  '0–90% Overlap 重叠 — 可调重叠率保证跨 chunk 语义连续性',
  '表格感知分块 — table 策略逐行类型化处理，保留表格结构',
  '页码 + 坐标追踪 — PDF/DOCX 精确定位原文位置，支持溯源高亮'
])

// 不足
const cons = ref([
  'naive 策略可能断句 — 基于分隔符切分，无法保证语义完整性',
  '依赖 LLM 质量 — auto_keywords / auto_questions 依赖 LLM 输出质量，可能产生噪声',
  '非语义级重叠 — 重叠基于 token 数量而非语义边界，可能浪费上下文窗口',
  '复杂表格可能截断 — 大型跨页表格仍可能被强制切分',
  '仅 PDF/DOCX 精确定位 — 页码与坐标追踪仅适用于部分格式'
])
</script>
