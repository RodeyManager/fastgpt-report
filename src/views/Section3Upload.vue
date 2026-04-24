<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§3 文档上传与解析</h2>
      <p>多格式文件上传、安全校验、S3存储与智能解析引擎全流程</p>
    </div>

    <div class="source-ref-list">
      <div class="ref-title">&#128204; 核心源码</div>
      <div class="source-ref-item"><span class="ref-file">packages/service/worker/readFile/index.ts</span> <span class="ref-desc">Worker分发器(extension→parser)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/worker/readFile/extension/pdf.ts</span> <span class="ref-desc">PDF解析(pdfjs-dist)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/worker/readFile/extension/docx.ts</span> <span class="ref-desc">DOCX解析(mammoth+图片提取)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/worker/readFile/extension/pptx.ts</span> <span class="ref-desc">PPTX解析(XML提取)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/worker/readFile/extension/csv.ts</span> <span class="ref-desc">CSV解析(papaparse)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/worker/readFile/extension/xlsx.ts</span> <span class="ref-desc">Excel解析(node-xlsx)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/worker/readFile/extension/html.ts</span> <span class="ref-desc">HTML解析(turndown)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/worker/readFile/extension/rawText.ts</span> <span class="ref-desc">TXT/MD解析(iconv-lite)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/worker/htmlStr2Md/utils.ts</span> <span class="ref-desc">HTML→Markdown引擎</span></div>
    </div>

    <!-- 支持的文件类型 -->
    <div class="card">
      <div class="card-title"><span class="icon">📁</span> 支持的文件类型</div>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <span v-for="(t,i) in fileTypes" :key="t" class="tag" :class="tagColors[i%3]">{{ t }}</span>
      </div>
    </div>

    <!-- 上传处理流程 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔄</span> 上传处理流程</div>
      <div class="flow-diagram">
        <div class="flow-steps">
          <div v-for="(s,i) in flowSteps" :key="i" style="display:flex;align-items:center">
            <div class="flow-step" :class="{primary:i===3}">
              <div style="font-weight:600;font-size:.85rem">{{ s.title }}</div>
              <div style="font-size:.72rem;color:var(--text-muted);margin-top:4px">{{ s.desc }}</div>
            </div>
            <span v-if="i<flowSteps.length-1" class="flow-arrow">→</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 文件解析引擎对比 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚙️</span> 文件解析引擎对比</div>
      <table class="data-table">
        <thead><tr><th>文件类型</th><th>解析库</th><th>解析方法</th></tr></thead>
        <tbody>
          <tr v-for="e in engines" :key="e.ext">
            <td><code>{{ e.ext }}</code></td>
            <td v-html="e.libHtml"></td>
            <td>{{ e.method }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 第三方PDF解析 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔌</span> 第三方PDF解析服务</div>
      <table class="data-table">
        <thead><tr><th>服务</th><th>调用方式</th></tr></thead>
        <tbody>
          <tr v-for="s in pdfServices" :key="s.name">
            <td><code>{{ s.name }}</code></td>
            <td>{{ s.desc }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 对象存储 -->
    <div class="card">
      <div class="card-title"><span class="icon">🗄️</span> 对象存储</div>
      <ul class="feature-list">
        <li>S3 兼容存储：MinIO / AWS S3 / 腾讯 COS / 阿里 OSS</li>
        <li>密钥路径：<code>dataset/{datasetId}/{filename}_{nanoid}.{ext}</code></li>
      </ul>
    </div>

    <!-- 文本提取→Markdown转换→分块链路 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚡</span> 文本提取 → Markdown转换 → 分块 完整链路</div>
      <p style="color:var(--text-secondary);font-size:0.88rem;margin-bottom:16px;">每种文档类型经解析后，部分格式会转为 Markdown 再进入分块算法。commonSplit 分块器对 Markdown 有特殊处理能力（标题拆分、表格保持、代码块保护），因此 Markdown 格式的文件能获得更精确的结构化拆分。</p>
      <table class="data-table">
        <thead>
          <tr>
            <th>文件类型</th>
            <th>解析器</th>
            <th>中间格式</th>
            <th>HTML→MD转换</th>
            <th>到达分块格式</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>PDF</code> (默认)</td>
            <td>pdfjs-dist</td>
            <td>纯文本(Token拼接)</td>
            <td><span class="tag tag-red">✗</span></td>
            <td>纯文本</td>
          </tr>
          <tr>
            <td><code>PDF</code> (自定义)</td>
            <td>Doc2x / Textin / 外部API</td>
            <td>Markdown</td>
            <td><span class="tag tag-green">✓ 已是MD</span></td>
            <td><strong style="color:var(--accent-green)">Markdown</strong></td>
          </tr>
          <tr>
            <td><code>DOCX</code></td>
            <td>mammoth → HTML</td>
            <td>HTML → turndown</td>
            <td><span class="tag tag-green">✓ turndown</span></td>
            <td><strong style="color:var(--accent-green)">Markdown</strong></td>
          </tr>
          <tr>
            <td><code>PPTX</code></td>
            <td>decompress + XML</td>
            <td>纯文本(&lt;a:t&gt;提取)</td>
            <td><span class="tag tag-red">✗</span></td>
            <td>纯文本</td>
          </tr>
          <tr>
            <td><code>CSV</code></td>
            <td>papaparse</td>
            <td>直接拼接Markdown表格</td>
            <td><span class="tag tag-cyan">字符串拼接</span></td>
            <td><strong style="color:var(--accent-green)">Markdown表格</strong></td>
          </tr>
          <tr>
            <td><code>XLSX</code></td>
            <td>node-xlsx</td>
            <td>Markdown表格(多sheet拼接)</td>
            <td><span class="tag tag-cyan">字符串拼接</span></td>
            <td><strong style="color:var(--accent-green)">Markdown表格</strong></td>
          </tr>
          <tr>
            <td><code>HTML</code></td>
            <td>原始读取</td>
            <td>HTML → turndown</td>
            <td><span class="tag tag-green">✓ turndown</span></td>
            <td><strong style="color:var(--accent-green)">Markdown</strong></td>
          </tr>
          <tr>
            <td><code>TXT</code></td>
            <td>buffer.toString</td>
            <td>原始文本</td>
            <td><span class="tag tag-red">✗</span></td>
            <td>纯文本</td>
          </tr>
          <tr>
            <td><code>MD</code></td>
            <td>buffer.toString</td>
            <td>原始Markdown</td>
            <td><span class="tag tag-green">✓ 原样保留</span></td>
            <td><strong style="color:var(--accent-green)">Markdown</strong></td>
          </tr>
          <tr>
            <td><code>URL/链接</code></td>
            <td>cheerio → turndown</td>
            <td>HTML → turndown</td>
            <td><span class="tag tag-green">✓ turndown</span></td>
            <td><strong style="color:var(--accent-green)">Markdown</strong></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 转换链路分类 -->
    <div class="card">
      <div class="card-title"><span class="icon">📊</span> 转换链路分类</div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:12px">
        <div style="border-left:3px solid var(--accent-green);padding:12px 16px;background:rgba(0,255,136,0.03);border-radius:0 8px 8px 0;">
          <strong style="color:var(--accent-green);">✓ 转为Markdown (6种)</strong><br/>
          <span style="font-size:0.82rem;color:var(--text-secondary);line-height:1.8;">
            <code>DOCX</code> (mammoth→turndown)<br/>
            <code>HTML</code> (turndown)<br/>
            <code>CSV</code> (直接拼接MD表格)<br/>
            <code>XLSX</code> (直接拼接MD表格)<br/>
            <code>MD</code> (原样保留)<br/>
            <code>URL</code> (cheerio→turndown)
          </span>
        </div>
        <div style="border-left:3px solid var(--accent-orange);padding:12px 16px;background:rgba(255,165,0,0.03);border-radius:0 8px 8px 0;">
          <strong style="color:var(--accent-orange);">⚠ 纯文本 (2种)</strong><br/>
          <span style="font-size:0.82rem;color:var(--text-secondary);line-height:1.8;">
            <code>PDF</code> (默认, pdfjs-dist Token提取)<br/>
            <code>PPTX</code> (XML &lt;a:t&gt;节点提取)<br/><br/>
            <em style="color:var(--text-muted)">无Markdown结构，分块器无法利用标题/表格/代码块规则</em>
          </span>
        </div>
        <div style="border-left:3px solid var(--accent-cyan);padding:12px 16px;background:rgba(0,188,212,0.03);border-radius:0 8px 8px 0;">
          <strong style="color:var(--accent-cyan);">💡 格式选择门机制</strong><br/>
          <span style="font-size:0.82rem;color:var(--text-secondary);line-height:1.8;">
            CSV/XLSX 同时输出 <code>rawText</code>(原始) 和 <code>formatText</code>(MD表格)<br/><br/>
            当 <code>getFormatText=true</code> (默认)，系统优先使用 <code>formatText</code>，使表格数据获得更好的结构化分块
          </span>
        </div>
      </div>
    </div>

    <!-- 转换链路核心源码 -->
    <div class="source-ref-list">
      <div class="ref-title">📌 转换链路核心源码</div>
      <div class="source-ref-item"><span class="ref-file">packages/service/common/file/read/utils.ts</span> <span class="ref-desc">格式选择门(getFormatText ? formatText : rawText)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/worker/htmlStr2Md/utils.ts</span> <span class="ref-desc">HTML→Markdown转换(turndown+simpleMarkdownText)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/worker/readFile/type.ts</span> <span class="ref-desc">ReadFileResponse定义(rawText+formatText+imageList)</span></div>
    </div>

    <div class="card">
      <div class="card-title"><span class="icon">&#9881;</span> 文件解析Worker调度源码</div>
      <div class="code-block">
        <span class="lang-tag">TypeScript</span>
        <pre><span class="code-comment">// packages/service/worker/readFile/index.ts</span>
<span class="code-keyword">switch</span> (extension) {
  <span class="code-keyword">case</span> <span class="code-string">'pdf'</span>:  <span class="code-keyword">return</span> readPdfFile(params);
  <span class="code-keyword">case</span> <span class="code-string">'docx'</span>: <span class="code-keyword">return</span> readDocsFile(params);
  <span class="code-keyword">case</span> <span class="code-string">'pptx'</span>: <span class="code-keyword">return</span> readPptxRawText(params);
  <span class="code-keyword">case</span> <span class="code-string">'xlsx'</span>: <span class="code-keyword">return</span> readXlsxRawText(params);
  <span class="code-keyword">case</span> <span class="code-string">'csv'</span>:  <span class="code-keyword">return</span> readCsvRawText(params);
  <span class="code-keyword">case</span> <span class="code-string">'html'</span>: <span class="code-keyword">return</span> readHtmlRawText(params);
  <span class="code-keyword">default</span>:   <span class="code-keyword">return</span> readFileRawText(params);
}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import * as echarts from 'echarts'

const tagColors = ['tag-blue', 'tag-cyan', 'tag-green']
const fileTypes = ref(['.txt','.md','.html','.pdf','.docx','.pptx','.csv','.xlsx'])

const flowSteps = ref([
  { title: '客户端上传', desc: 'multipart/form-data' },
  { title: 'Multer接收', desc: '磁盘存储 / nanoid' },
  { title: '安全验证', desc: 'magic bytes校验' },
  { title: 'S3存储', desc: '私有桶写入' },
  { title: 'Worker线程解析', desc: 'SharedArrayBuffer' },
  { title: '原始文本输出', desc: '供后续分块' }
])

const engines = ref([
  { ext: 'PDF', lib: 'pdfjs-dist', libHtml: '<code><a href="https://www.npmjs.com/package/pdfjs-dist" target="_blank" style="color:var(--accent-cyan)">pdfjs-dist</a></code>', method: 'Token提取, 页眉页脚过滤(上下5%), 段落检测' },
  { ext: 'DOCX', lib: 'mammoth → turndown', libHtml: '<code><a href="https://www.npmjs.com/package/mammoth" target="_blank" style="color:var(--accent-cyan)">mammoth</a> → <a href="https://www.npmjs.com/package/turndown" target="_blank" style="color:var(--accent-cyan)">turndown</a></code>', method: 'DOCX→HTML→Markdown, 嵌入图片base64提取' },
  { ext: 'PPTX', lib: 'decompress + @xmldom/xmldom', libHtml: '<code><a href="https://www.npmjs.com/package/decompress" target="_blank" style="color:var(--accent-cyan)">decompress</a> + <a href="https://www.npmjs.com/package/@xmldom/xmldom" target="_blank" style="color:var(--accent-cyan)">@xmldom/xmldom</a></code>', method: 'ZIP解压, 幻灯片XML解析' },
  { ext: 'XLSX', lib: 'node-xlsx', libHtml: '<code><a href="https://www.npmjs.com/package/node-xlsx" target="_blank" style="color:var(--accent-cyan)">node-xlsx</a></code>', method: '工作表解析, CSV+Markdown表格' },
  { ext: 'CSV', lib: 'papaparse', libHtml: '<code><a href="https://www.npmjs.com/package/papaparse" target="_blank" style="color:var(--accent-cyan)">papaparse</a></code>', method: 'CSV解析, Markdown表格转换' },
  { ext: 'HTML', lib: 'turndown + GFM插件', libHtml: '<code><a href="https://www.npmjs.com/package/turndown" target="_blank" style="color:var(--accent-cyan)">turndown</a> + GFM插件</code>', method: 'HTML→Markdown, base64图片提取' },
  { ext: 'TXT/MD', lib: 'iconv-lite', libHtml: '<code><a href="https://www.npmjs.com/package/iconv-lite" target="_blank" style="color:var(--accent-cyan)">iconv-lite</a></code>', method: '编码检测, Markdown图片提取' }
])

const pdfServices = ref([
  { name: 'Doc2x API', desc: '预上传 → 解析 → 轮询获取结果' },
  { name: 'Textin / XParse', desc: 'PDF → Markdown 转换服务' },
  { name: '自定义URL', desc: '可配置端点，支持自定义解析服务' }
])
</script>
