<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§5 数据清洗能力</h2>
      <p>清洗流程四步流水线、关键函数源码、NLP关键词提取、清洗能力综合评估</p>
    </div>

    <!-- 5.1 清洗流程 -->
    <div class="card">
      <div class="card-title"><span class="icon">🧹</span> 5.1 清洗流程（四步流水线）</div>
      <div class="highlight-block">
        MaxKB 数据清洗采用<strong>四步流水线</strong>，从原始文本到格式特有清洗逐级处理，其中代码块保护是核心亮点。
      </div>
      <div class="flow-diagram" style="margin:16px 0;">
        <div class="flow-steps" style="flex-direction:column;align-items:stretch;gap:0;">
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(99,102,241,0.12);border-radius:8px 8px 0 0;">
            <span style="background:#6366f1;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;">Step 1</span>
            <strong>行尾标准化</strong>
            <code style="margin-left:auto;font-size:12px;">\r\n→\n | \r→\n | \0→移除</code>
          </div>
          <div style="text-align:center;padding:4px;color:#6366f1;font-weight:bold;">↓</div>
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(139,92,246,0.12);">
            <span style="background:#8b5cf6;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;">Step 2</span>
            <strong>特殊字符过滤</strong>
            <code style="margin-left:auto;font-size:12px;">\n+→\n | 空格+→空格 | #+→移除 | \t+→移除</code>
          </div>
          <div style="text-align:center;padding:4px;color:#8b5cf6;font-weight:bold;">↓</div>
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(236,72,153,0.12);">
            <span style="background:#ec4899;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;">Step 3</span>
            <strong>代码块保护</strong>
            <code style="margin-left:auto;font-size:12px;">mask_code_blocks() — 防止代码内#被误判为标题</code>
          </div>
          <div style="text-align:center;padding:4px;color:#ec4899;font-weight:bold;">↓</div>
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(245,158,11,0.12);border-radius:0 0 8px 8px;">
            <span style="background:#f59e0b;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;">Step 4</span>
            <strong>格式特有清洗</strong>
            <span style="color:#94a3b8;font-size:12px;">HTML锚点移除 | PDF章节编号清理 | CSV换行转义 | 标题#移除</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 5.2 关键清洗函数源码 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔧</span> 5.2 关键清洗函数源码</div>

      <!-- filter_special_char -->
      <details>
        <summary>📖 filter_special_char() — 特殊字符过滤</summary>
        <div class="code-block">
          <pre><code># apps/common/utils/split_model.py (line 347-364)

replace_map = {
    re.compile('\n+'): '\n',      # 合并多个换行
    re.compile(' +'): ' ',        # 合并多个空格
    re.compile('#+'): "",         # 移除 # 标记
    re.compile("\t+"): ''         # 移除制表符
}

def filter_special_char(content: str):
    """过滤特殊字段"""
    items = replace_map.items()
    for key, value in items:
        content = re.sub(key, value, content)
    return content</code></pre>
        </div>
      </details>

      <!-- mask_code_blocks -->
      <details>
        <summary>📖 mask_code_blocks() — 代码块保护</summary>
        <div class="code-block">
          <pre><code># apps/common/utils/split_model.py (line 160-173)

def mask_code_blocks(text: str) -> str:
    """将代码块内容替换为等长空格,防止代码块内的#被识别为标题"""
    result = list(text)
    for match in re.finditer(r'```[^\n]*\n.*?```', text, re.DOTALL):
        start = match.start()
        end = match.end()
        inner_start = text.index('\n', start) + 1
        closing_fence_start = text.rindex('```', start, end)
        for i in range(inner_start, closing_fence_start):
            if result[i] != '\n':
                result[i] = ' '
    return ''.join(result)</code></pre>
        </div>
      </details>

      <!-- normalize_for_embedding -->
      <details>
        <summary>📖 normalize_for_embedding() — 嵌入前文本预处理</summary>
        <div class="code-block">
          <pre><code># apps/knowledge/vector/base_vector.py

def normalize_for_embedding(text: str) -> str:
    """嵌入前文本标准化: 移除emoji, 合并空白"""
    import re
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF...]"
    )
    text = emoji_pattern.sub('', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text</code></pre>
        </div>
      </details>
    </div>

    <!-- 5.3 NLP处理: jieba中文关键词提取 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔍</span> 5.3 NLP处理：jieba 中文关键词提取</div>
      <div class="code-block">
        <pre><code># apps/common/utils/split_model.py (line 96-104)

def get_keyword(content: str):
    """获取content中的关键词"""
    stopwords = ['：', '"', '！', '"', '\n', '\\s']
    cutworms = jieba.lcut(content)
    return list(set(list(filter(lambda k: (k not in stopwords) | len(k) > 1, cutworms))))</code></pre>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>实现要点：</strong>使用 jieba 分词后过滤停用词和单字符，去重返回关键词列表，用于后续向量检索增强。
      </div>
    </div>

    <!-- 5.4 清洗能力评估表 -->
    <div class="card">
      <div class="card-title"><span class="icon">📊</span> 5.4 清洗能力评估</div>
      <table class="data-table">
        <thead>
          <tr><th>清洗维度</th><th>实现方式</th><th>评级</th><th>说明</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in cleaningData" :key="r.dimension">
            <td><strong>{{ r.dimension }}</strong></td>
            <td>{{ r.method }}</td>
            <td :style="{ color: r.ratingColor }">{{ r.rating }}</td>
            <td>{{ r.note }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 清洗能力雷达图 -->
    <div class="card">
      <div class="card-title"><span class="icon">📈</span> 清洗规则统计</div>
      <div ref="chartRef" style="height:400px;"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

// 清洗能力评估数据
const cleaningData = ref([
  { dimension: '换行标准化', method: '\\r\\n→\\n', rating: '✅ 完善', ratingColor: '#34d399', note: '跨平台兼容' },
  { dimension: '空白压缩', method: '正则替换 \\n+/ +', rating: '✅ 基础', ratingColor: '#34d399', note: '合并多余空白' },
  { dimension: '代码块保护', method: 'mask_code_blocks', rating: '⭐ 优秀', ratingColor: '#fbbf24', note: '防止误识别' },
  { dimension: 'HTML清洗', method: 'BeautifulSoup锚点移除', rating: '✅ 基础', ratingColor: '#34d399', note: '仅处理锚点' },
  { dimension: 'PDF清洗', method: '字体分析+行拼接', rating: '⭐ 优秀', ratingColor: '#fbbf24', note: '智能行合并' },
  { dimension: 'Emoji移除', method: '嵌入前Unicode正则', rating: '✅ 基础', ratingColor: '#34d399', note: '仅嵌入阶段' },
  { dimension: 'OCR支持', method: '❌ 无', rating: '⚠️ 缺失', ratingColor: '#f87171', note: '图片内文字无法提取' },
  { dimension: '去重/去噪', method: 'SHA256文件去重', rating: '✅ 基础', ratingColor: '#34d399', note: '仅文件级别' },
])

// ECharts 图表
const chartRef = ref(null)

onMounted(() => {
  if (!chartRef.value) return
  const chart = echarts.init(chartRef.value)

  // 清洗规则分类统计数据
  const categories = ['换行标准化', '空白压缩', '代码块保护', 'HTML清洗', 'PDF清洗', 'Emoji移除', 'OCR支持', '去重/去噪']
  const scores = [5, 3, 5, 3, 5, 3, 0, 3]
  const colors = scores.map(v => {
    if (v === 0) return '#f87171'
    if (v >= 5) return '#fbbf24'
    return '#6366f1'
  })

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15,23,42,0.9)',
      borderColor: '#334155',
      textStyle: { color: '#e2e8f0' },
      formatter: (params) => {
        const d = params[0]
        const level = d.value === 0 ? '⚠️ 缺失' : d.value >= 5 ? '⭐ 优秀' : '✅ 基础'
        return `<strong>${d.name}</strong><br/>能力评分: ${d.value} / 5<br/>评级: ${level}`
      }
    },
    grid: {
      top: 30,
      bottom: 50,
      left: 20,
      right: 30,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        color: '#94a3b8',
        fontSize: 11,
        rotate: 20
      },
      axisLine: { lineStyle: { color: '#334155' } },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      max: 5,
      name: '能力评分',
      nameTextStyle: { color: '#94a3b8', fontSize: 12 },
      axisLabel: { color: '#94a3b8' },
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#1e293b' } }
    },
    series: [{
      type: 'bar',
      data: scores.map((v, i) => ({
        value: v,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: colors[i] },
            { offset: 1, color: colors[i] + '44' }
          ]),
          borderRadius: [4, 4, 0, 0]
        }
      })),
      barWidth: '50%',
      label: {
        show: true,
        position: 'top',
        color: '#e2e8f0',
        fontSize: 12,
        formatter: (params) => {
          if (params.value === 0) return '⚠️'
          if (params.value >= 5) return '⭐'
          return '✅'
        }
      },
      emphasis: {
        itemStyle: {
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
