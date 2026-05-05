<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§6 文本分块策略</h2>
      <p>三阶段分块管道、SplitModel核心引擎、三种策略对比与参数配置</p>
    </div>

    <!-- 6.1 三阶段分块管道 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔄</span> 6.1 三阶段分块管道</div>
      <div class="highlight-block">
        MaxKB 文本分块采用<strong>三阶段流水线</strong>，将原始文件逐步转化为可检索的 chunk 数组：
      </div>
      <div class="flow-diagram" style="margin:16px 0;">
        <div class="flow-steps" style="flex-direction:column;align-items:stretch;gap:0;">
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(99,102,241,0.12);border-radius:8px 8px 0 0;">
            <span style="background:#6366f1;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;">阶段1</span>
            <strong>格式提取</strong>
            <span style="color:#94a3b8;font-size:12px;margin-left:auto;">文件 → 格式Handler → Markdown文本</span>
          </div>
          <div style="text-align:center;padding:4px;color:#6366f1;font-weight:bold;">↓</div>
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(139,92,246,0.12);">
            <span style="background:#8b5cf6;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;">阶段2</span>
            <strong>结构化解析 (SplitModel)</strong>
            <span style="color:#94a3b8;font-size:12px;margin-left:auto;">Markdown → 标题树 → 扁平段落</span>
          </div>
          <div style="text-align:center;padding:4px;color:#8b5cf6;font-weight:bold;">↓</div>
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(236,72,153,0.12);border-radius:0 0 8px 8px;">
            <span style="background:#ec4899;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;">阶段3</span>
            <strong>子分块 (MarkChunkHandle)</strong>
            <span style="color:#94a3b8;font-size:12px;margin-left:auto;">长段落 → 256字符子块 → chunks数组</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 6.2 SplitModel 核心分块引擎 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚙️</span> 6.2 SplitModel 核心分块引擎（501行）</div>
      <div class="highlight-block">
        SplitModel 是 MaxKB 文本分块的核心引擎，支持<strong>三种分块策略</strong>，按语义完整性递降使用：
      </div>

      <!-- 策略A: 标题树递归解析 -->
      <div style="margin-top:16px;">
        <div class="card-title" style="font-size:14px;">
          <span style="background:#6366f1;color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;margin-right:6px;">策略A</span>
          标题树递归解析 <code style="font-size:12px;">parse_to_tree</code>
        </div>
        <div class="code-block">
          <pre><code>def parse_to_tree(self, text: str, index=0):
    """递归解析Markdown标题层级结构"""
    level_content_list = parse_title_level(text, self.content_level_pattern, index)
    if len(level_content_list) == 0:
        # 无标题: 智能分割
        return [to_tree_obj(row, 'block') for row in smart_split_paragraph(text, limit=self.limit)]

    # 构建标题树 → 递归解析下一级标题
    for i in range(len(level_title_content_list)):
        block, cursor = get_level_block(text, level_title_content_list, i, cursor)
        children = self.parse_to_tree(text=block, index=index + 1)
        level_title_content_list[i]['children'] = children</code></pre>
        </div>
        <ol style="padding-left:20px;margin:8px 0;line-height:2;color:#cbd5e1;">
          <li>使用正则匹配标题层级 (# ~ ######)</li>
          <li>代码块内容先被遮蔽 (<code>mask_code_blocks</code>)</li>
          <li>递归构建标题树结构</li>
          <li>叶节点为 block 内容</li>
          <li>树形结构扁平化为段落列表</li>
        </ol>
      </div>

      <!-- 策略B: 智能段落分割 -->
      <div style="margin-top:16px;">
        <div class="card-title" style="font-size:14px;">
          <span style="background:#8b5cf6;color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;margin-right:6px;">策略B</span>
          智能段落分割 <code style="font-size:12px;">smart_split_paragraph</code>
        </div>
        <div class="code-block">
          <pre><code>def smart_split_paragraph(content: str, limit: int):
    """智能分段: 在limit前找到合适的分割点(句号、回车等)"""
    # 分割优先级: 句号(.。)> 感叹号/问号(!！?？)
    split_chars = [('。', 0), ('.', 0), ('！', 0), ('!', 0), ('？', 0), ('?', 0)]
    # 从后往前找分割点 (至少保留一半内容)
    for i in range(end - 1, start + limit // 2, -1):
        for char, offset in split_chars:
            if content[i] == char:
                best_split = i + 1</code></pre>
        </div>
        <ul class="feature-list" style="margin:8px 0;">
          <li>在 limit 范围内寻找自然语句边界</li>
          <li>分割优先级: 句号 → 感叹号 → 问号</li>
          <li>保证至少保留一半内容在前段</li>
          <li>避免在词句中间截断</li>
        </ul>
      </div>

      <!-- 策略C: 字符限制硬分割 -->
      <div style="margin-top:16px;">
        <div class="card-title" style="font-size:14px;">
          <span style="background:#ec4899;color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;margin-right:6px;">策略C</span>
          字符限制硬分割 <code style="font-size:12px;">post_handler_paragraph</code>
        </div>
        <div class="highlight-block">
          根据文本的最大字符分段（最终回退策略）。按换行符分段，超过 <code>limit</code> 的段落继续按字符硬切。
        </div>
      </div>
    </div>

    <!-- 6.3 可配置分块模式 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔧</span> 6.3 可配置分隔符模式</div>
      <table class="data-table">
        <thead>
          <tr><th>分隔符</th><th>正则表达式</th><th>说明</th></tr>
        </thead>
        <tbody>
          <tr v-for="s in separatorData" :key="s.label">
            <td><strong>{{ s.label }}</strong></td>
            <td><code>{{ s.regex }}</code></td>
            <td>{{ s.desc }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 6.4 子分块系统 -->
    <div class="card">
      <div class="card-title"><span class="icon">🧩</span> 6.4 子分块系统 (MarkChunkHandle)</div>
      <div class="two-col">
        <div>
          <div class="card-title" style="font-size:14px;">分块逻辑</div>
          <div class="code-block">
            <pre><code>class MarkChunkHandle(IChunkHandle):
    def handle(self, chunk_list, chunk_size=256):
        split_chunk_pattern = r'.{1,%d}[。| |\.|！|;|；|!|\n]' % chunk_size
        max_chunk_pattern = r'.{1,%d}' % chunk_size
        # 优先在句子边界分割, 否则硬切</code></pre>
          </div>
        </div>
        <div>
          <div class="card-title" style="font-size:14px;">存储模型 (Paragraph)</div>
          <table class="data-table">
            <tbody>
              <tr><td><strong>content</strong></td><td>CharField(max_length=102400) 完整段落内容</td></tr>
              <tr><td><strong>chunks</strong></td><td>ArrayField(CharField) 256字符子块列表</td></tr>
              <tr><td><strong>position</strong></td><td>IntegerField 文档内排序</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 6.5 分块参数汇总 -->
    <div class="card">
      <div class="card-title"><span class="icon">📋</span> 6.5 分块参数汇总</div>
      <table class="data-table">
        <thead>
          <tr><th>参数</th><th>位置</th><th>默认值</th><th>范围</th><th>说明</th></tr>
        </thead>
        <tbody>
          <tr v-for="p in paramData" :key="p.name">
            <td><code>{{ p.name }}</code></td>
            <td>{{ p.location }}</td>
            <td>{{ p.default }}</td>
            <td>{{ p.range }}</td>
            <td>{{ p.desc }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 6.6 分块策略对比雷达图 -->
    <div class="card">
      <div class="card-title"><span class="icon">📊</span> 6.6 分块策略对比</div>
      <div ref="radarChartRef" style="height:400px;"></div>
    </div>

    <!-- 策略对比表 -->
    <div class="card">
      <div class="card-title"><span class="icon">📏</span> 策略维度详细对比</div>
      <table class="data-table">
        <thead>
          <tr><th>维度</th><th>标题树解析</th><th>智能分割</th><th>字符硬分割</th></tr>
        </thead>
        <tbody>
          <tr v-for="c in compareData" :key="c.dim">
            <td><strong>{{ c.dim }}</strong></td>
            <td>{{ c.tree }}</td>
            <td>{{ c.smart }}</td>
            <td>{{ c.hard }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

// 分隔符数据
const separatorData = ref([
  { label: '#', regex: '(?<=^)# .*|(?<=\\n)# .*', desc: '一级标题' },
  { label: '## ~ ######', regex: '(?<=\\n)(?<!#)## (?!#).*', desc: '二至六级标题' },
  { label: '-', regex: '(?<! )- .*', desc: '无序列表' },
  { label: '；', regex: '(?<!；)；(？！；)', desc: '中文分号' },
  { label: '，', regex: '(?<!，)，(？！，)', desc: '中文逗号' },
  { label: '。', regex: '(?<!。)。(？！。)', desc: '中文句号' },
  { label: '换行', regex: '(?<!\\n)\\n(?!\\n)', desc: '单换行' },
  { label: '空行', regex: '(?<!\\n)\\n\\n(?!\\n)', desc: '双换行(段落分隔)' },
  { label: '空格', regex: '(?<! ) (?! )', desc: '单空格' },
])

// 分块参数数据
const paramData = ref([
  { name: 'limit', location: 'SplitModel', default: '100,000', range: '50-100,000', desc: '单段落最大字符数' },
  { name: 'with_filter', location: 'SplitModel', default: 'True', range: 'bool', desc: '启用特殊字符过滤' },
  { name: 'pattern_list', location: 'SplitModel', default: 'H1-H6正则', range: 'List[regex]', desc: '自定义分割模式' },
  { name: 'chunk_size', location: 'MarkChunkHandle', default: '256', range: 'int', desc: '子分块字符数' },
  { name: 'hit_handling_method', location: 'Document', default: 'optimization', range: 'optimization / directly_return', desc: '命中处理方式' },
  { name: 'directly_return_similarity', location: 'Document', default: '0.9', range: '0-2', desc: '直接返回相似度阈值' },
])

// 策略对比表数据
const compareData = ref([
  { dim: '适用场景', tree: '有标题结构的文档', smart: '无标题的长文本', hard: '最终回退' },
  { dim: '语义完整性', tree: '⭐⭐⭐ 优秀', smart: '⭐⭐ 良好', hard: '⭐ 一般' },
  { dim: '上下文保留', tree: '父级链路保留', smart: '句子边界分割', hard: '无保证' },
  { dim: '中文优化', tree: '✅ jieba关键词', smart: '✅ 中英文标点', hard: '❌ 无' },
  { dim: '代码保护', tree: '✅ 代码块遮蔽', smart: '-', hard: '-' },
])

// ECharts 雷达图
const radarChartRef = ref(null)

onMounted(() => {
  if (!radarChartRef.value) return
  const chart = echarts.init(radarChartRef.value)

  chart.setOption({
    tooltip: {
      trigger: 'item'
    },
    legend: {
      data: ['标题树解析', '智能分割', '字符硬分割'],
      bottom: 10,
      textStyle: { color: '#94a3b8', fontSize: 12 },
      itemWidth: 14,
      itemHeight: 10
    },
    radar: {
      indicator: [
        { name: '语义完整性', max: 100 },
        { name: '上下文保留', max: 100 },
        { name: '中文优化', max: 100 },
        { name: '代码保护', max: 100 },
        { name: '灵活性', max: 100 },
        { name: '性能', max: 100 }
      ],
      shape: 'polygon',
      radius: '62%',
      center: ['50%', '46%'],
      axisName: {
        color: '#e2e8f0',
        fontSize: 12
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(99,102,241,0.02)', 'rgba(99,102,241,0.05)', 'rgba(99,102,241,0.08)', 'rgba(99,102,241,0.11)', 'rgba(99,102,241,0.14)']
        }
      },
      splitLine: {
        lineStyle: { color: 'rgba(148,163,184,0.15)' }
      },
      axisLine: {
        lineStyle: { color: 'rgba(148,163,184,0.2)' }
      }
    },
    series: [{
      type: 'radar',
      data: [
        {
          value: [95, 90, 85, 90, 70, 60],
          name: '标题树解析',
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: { width: 2, color: '#6366f1' },
          areaStyle: { color: 'rgba(99,102,241,0.2)' },
          itemStyle: { color: '#6366f1' }
        },
        {
          value: [75, 70, 80, 0, 85, 80],
          name: '智能分割',
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: { width: 2, color: '#8b5cf6' },
          areaStyle: { color: 'rgba(139,92,246,0.15)' },
          itemStyle: { color: '#8b5cf6' }
        },
        {
          value: [40, 30, 0, 0, 90, 95],
          name: '字符硬分割',
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: { width: 2, color: '#ec4899' },
          areaStyle: { color: 'rgba(236,72,153,0.1)' },
          itemStyle: { color: '#ec4899' }
        }
      ]
    }]
  })

  const resizeHandler = () => chart.resize()
  window.addEventListener('resize', resizeHandler)
})
</script>
