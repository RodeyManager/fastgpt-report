<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§4 文档解析能力</h2>
      <p>解析Handler责任链、PDF三策略递降、格式转换全矩阵</p>
    </div>

    <!-- 4.1 解析Handler链 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔗</span> 4.1 解析Handler链（责任链模式）</div>
      <div class="highlight-block">
        MaxKB 采用<strong>责任链模式</strong>，按文件扩展名依次匹配 Handler，未命中则回退到 <code>TextSplitHandle</code>。
      </div>
      <div class="code-block">
        <pre><code># apps/knowledge/serializers/document.py (line 68-77)
split_handles = [
    HTMLSplitHandle(),    # .html → BeautifulSoup + markdownify → Markdown
    DocSplitHandle(),     # .docx → python-docx → Markdown
    PdfSplitHandle(),     # .pdf → pypdf (3策略递降)
    XlsxSplitHandle(),    # .xlsx → openpyxl → Markdown表格
    XlsSplitHandle(),     # .xls → xlrd → Markdown表格
    CsvSplitHandle(),     # .csv → csv reader → Markdown表格
    ZipSplitHandle(),     # .zip → 递归委托内部handler
]
# 默认回退: TextSplitHandle (.md/.txt + charset_normalizer)</code></pre>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>📂 基类:</strong> <code>apps/common/handle/base_split_handle.py</code><br>
        <strong>📂 实现:</strong> <code>apps/common/handle/impl/text/</code>
      </div>
    </div>

    <!-- 4.2 PDF三策略递降 -->
    <div class="card">
      <div class="card-title"><span class="icon">📄</span> 4.2 PDF解析 — 三策略递降（核心亮点）</div>
      <div class="highlight-block">
        PDF解析器是MaxKB中最复杂的解析器（559行），采用 <strong>三策略递降方案</strong>，确保各种PDF结构都能正确提取：
      </div>
      <div class="flow-diagram" style="margin:16px 0;">
        <div class="flow-steps" style="flex-direction:column;align-items:stretch;gap:0;">
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(99,102,241,0.12);border-radius:8px 8px 0 0;">
            <span style="background:#6366f1;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;">策略1</span>
            <strong>TOC目录书签提取</strong>
            <code style="margin-left:auto;font-size:12px;">handle_toc()</code>
            <span style="color:#94a3b8;font-size:12px;">使用PDF大纲/书签提取章节结构</span>
          </div>
          <div style="text-align:center;padding:4px;color:#6366f1;font-weight:bold;">↓ 失败</div>
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(139,92,246,0.12);">
            <span style="background:#8b5cf6;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;">策略2</span>
            <strong>内部链接提取</strong>
            <code style="margin-left:auto;font-size:12px;">handle_links()</code>
            <span style="color:#94a3b8;font-size:12px;">利用PDF内部超链接重建文档结构</span>
          </div>
          <div style="text-align:center;padding:4px;color:#8b5cf6;font-weight:bold;">↓ 失败</div>
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(236,72,153,0.12);border-radius:0 0 8px 8px;">
            <span style="background:#ec4899;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;">策略3</span>
            <strong>字体大小分析</strong>
            <code style="margin-left:auto;font-size:12px;">handle_pdf_content()</code>
            <span style="color:#94a3b8;font-size:12px;">统计字体大小众数 → 正文基准</span>
          </div>
        </div>
      </div>
      <div class="two-col" style="margin-top:12px;">
        <div>
          <div class="card-title" style="font-size:14px;">📐 字体大小分析算法</div>
          <ol style="padding-left:20px;margin:0;line-height:2;color:#cbd5e1;">
            <li>遍历所有页面收集字体大小</li>
            <li>使用 <code>Counter</code> 统计众数作为正文字体大小</li>
            <li>比较各文本字体与正文基准：
              <ul style="padding-left:16px;margin:0;">
                <li>差值 &gt; 2 → 二级标题 (H2)</li>
                <li>差值 &gt; 0.5 → 三级标题 (H3)</li>
              </ul>
            </li>
            <li>图片引用插入为 <code>![image](image_{page}_{index})</code></li>
          </ol>
        </div>
        <div>
          <div class="card-title" style="font-size:14px;">📂 源码信息</div>
          <table class="data-table">
            <tbody>
              <tr><td><strong>文件路径</strong></td><td><code>apps/common/handle/impl/text/pdf_split_handle.py</code></td></tr>
              <tr><td><strong>代码行数</strong></td><td>559行</td></tr>
              <tr><td><strong>解析引擎</strong></td><td>pypdf</td></tr>
              <tr><td><strong>策略数量</strong></td><td>3策略递降</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 4.3 DOCX解析 -->
    <div class="card">
      <div class="card-title"><span class="icon">📝</span> 4.3 DOCX解析</div>
      <div class="two-col">
        <div>
          <div class="card-title" style="font-size:14px;">标题检测策略</div>
          <div class="code-block">
            <pre><code># 标题检测策略:
# 1. 样式名匹配: 'Heading', 'TOC 标题', '标题' 等
# 2. 字号阈值检测:
title_font_list = [
    [36, 100],   # 一级标题 (36pt以上)
    [26, 36],    # 二级标题
    [24, 26],    # 三级标题
    [22, 24],    # 四级标题
    [18, 22],    # 五级标题
    [16, 18],    # 六级标题
]</code></pre>
          </div>
        </div>
        <div>
          <div class="card-title" style="font-size:14px;">核心特性</div>
          <ul class="feature-list">
            <li>段落 → Markdown标题/正文</li>
            <li>表格 → Markdown表格</li>
            <li>图片提取: XPath查找 <code>.//pic:pic</code> 和 <code>.//w:pict</code>，存储为File对象</li>
            <li>编码: <code>to_md()</code> 方法遍历body元素(段落+表格)</li>
          </ul>
          <div class="highlight-block" style="margin-top:8px;">
            <strong>📂 源码:</strong> <code>apps/common/handle/impl/text/doc_split_handle.py</code> (245行)
          </div>
        </div>
      </div>
    </div>

    <!-- 4.4 格式转换对比表 -->
    <div class="card">
      <div class="card-title"><span class="icon">📊</span> 4.4 格式转换对比</div>
      <table class="data-table">
        <thead>
          <tr><th>格式</th><th>转换方式</th><th>标题检测</th><th>图片处理</th><th>表格处理</th></tr>
        </thead>
        <tbody>
          <tr v-for="f in formatData" :key="f.format">
            <td><strong>{{ f.format }}</strong></td>
            <td>{{ f.convert }}</td>
            <td>{{ f.title }}</td>
            <td>{{ f.image }}</td>
            <td>{{ f.table }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 格式支持可视化 -->
    <div class="card">
      <div class="card-title"><span class="icon">📈</span> 格式能力矩阵</div>
      <div ref="chartRef" style="height:380px;"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

// 格式转换对比数据
const formatData = ref([
  { format: 'PDF', convert: 'pypdf文本提取', title: 'TOC→链接→字体分析', image: '引用占位符', table: '❌ 不支持' },
  { format: 'DOCX', convert: 'python-docx → MD', title: '样式+字号阈值', image: '提取为File对象', table: '✅ Markdown表格' },
  { format: 'HTML', convert: 'BeautifulSoup + markdownify', title: 'ATX标题转换', image: '保留引用', table: '✅ Markdown表格' },
  { format: 'XLSX', convert: 'openpyxl行遍历', title: '每Sheet一文档', image: '单元格图片提取', table: '✅ Markdown表格' },
  { format: 'CSV', convert: 'csv reader', title: '每文件一文档', image: '❌ 不支持', table: '✅ Markdown表格' },
])

// ECharts 图表
const chartRef = ref(null)

onMounted(() => {
  if (!chartRef.value) return
  const chart = echarts.init(chartRef.value)

  // 格式能力矩阵数据
  const formats = ['PDF', 'DOCX', 'HTML', 'XLSX', 'CSV', 'XLS', 'ZIP', 'TXT/MD']
  const capabilities = ['文本提取', '标题检测', '图片处理', '表格支持', '嵌套解析']

  // 能力矩阵 (1=支持, 0.5=部分支持, 0=不支持)
  const matrix = [
    [1, 1, 0.5, 0, 0],   // PDF
    [1, 1, 1, 1, 0],     // DOCX
    [1, 1, 0.5, 1, 0],   // HTML
    [1, 0, 0.5, 1, 0],   // XLSX
    [1, 0, 0, 1, 0],     // CSV
    [1, 0, 0, 1, 0],     // XLS
    [1, 0, 0, 0, 1],     // ZIP
    [1, 0, 0, 0, 0],     // TXT/MD
  ]

  // 构建heatmap数据 [x, y, value]
  const heatData = []
  for (let i = 0; i < formats.length; i++) {
    for (let j = 0; j < capabilities.length; j++) {
      heatData.push([j, i, matrix[i][j]])
    }
  }

  chart.setOption({
    tooltip: {
      position: 'top',
      formatter: (params) => {
        const val = params.value[2]
        const labels = { 1: '✅ 完整支持', 0.5: '⚠️ 部分支持', 0: '❌ 不支持' }
        return `<strong>${formats[params.value[1]]}</strong> → ${capabilities[params.value[0]]}<br/>${labels[val]}`
      }
    },
    grid: {
      top: 30,
      bottom: 60,
      left: 80,
      right: 40,
      containLabel: false
    },
    xAxis: {
      type: 'category',
      data: capabilities,
      position: 'top',
      axisLabel: {
        color: '#94a3b8',
        fontSize: 12
      },
      axisLine: { show: false },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'category',
      data: formats,
      axisLabel: {
        color: '#e2e8f0',
        fontSize: 12,
        fontWeight: 'bold'
      },
      axisLine: { show: false },
      axisTick: { show: false }
    },
    visualMap: {
      min: 0,
      max: 1,
      calculable: false,
      orient: 'horizontal',
      left: 'center',
      bottom: 10,
      inRange: {
        color: ['#1e1b4b', '#6366f1', '#a5f3fc']
      },
      text: ['支持', '不支持'],
      textStyle: { color: '#94a3b8' },
      itemWidth: 14,
      itemHeight: 100
    },
    series: [{
      type: 'heatmap',
      data: heatData,
      label: {
        show: true,
        color: '#fff',
        fontSize: 14,
        formatter: (params) => {
          const v = params.value[2]
          if (v === 1) return '●'
          if (v === 0.5) return '◐'
          return '○'
        }
      },
      itemStyle: {
        borderColor: '#0f172a',
        borderWidth: 2,
        borderRadius: 4
      },
      emphasis: {
        itemStyle: {
          borderColor: '#6366f1',
          borderWidth: 2,
          shadowBlur: 10,
          shadowColor: 'rgba(99,102,241,0.5)'
        }
      }
    }]
  })

  // 响应窗口变化
  const resizeHandler = () => chart.resize()
  window.addEventListener('resize', resizeHandler)
})
</script>
