<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§8 检索能力</h2>
      <p>三种检索策略、重排序系统、检索管道完整流程与能力评估</p>
    </div>

    <!-- 8.1 三种检索策略 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔍</span> 8.1 三种检索策略</div>
      <div class="highlight-block">
        MaxKB 在 pgvector 上实现了<strong>三种检索模式</strong>，通过 <code>SearchMode</code> 枚举切换：
        <code>EMBEDDING</code>（向量）、<code>KEYWORDS</code>（全文）、<code>BLEND</code>（混合）。
      </div>
      <table class="data-table">
        <thead>
          <tr><th>策略</th><th>算法</th><th>评分公式</th><th>中文支持</th><th>阈值</th><th>特点</th></tr>
        </thead>
        <tbody>
          <tr v-for="s in strategyData" :key="s.name">
            <td><strong>{{ s.name }}</strong></td>
            <td><code>{{ s.algorithm }}</code></td>
            <td>{{ s.score }}</td>
            <td>{{ s.chinese }}</td>
            <td>{{ s.threshold }}</td>
            <td>{{ s.note }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 检索策略能力矩阵 -->
    <div class="card">
      <div class="card-title"><span class="icon">📊</span> 检索策略能力矩阵</div>
      <div ref="chartRef" style="height:380px;"></div>
    </div>

    <!-- 8.2 中文全文检索 -->
    <div class="card">
      <div class="card-title"><span class="icon">🀄</span> 8.2 中文全文检索支持</div>
      <div class="two-col">
        <div>
          <div class="card-title" style="font-size:14px;">jieba 分词 → tsvector</div>
          <div class="code-block">
            <pre><code># apps/common/utils/ts_vecto_util.py

def to_ts_vector(text: str):
    """jieba全模式分词 → PostgreSQL tsvector"""
    return ' '.join(jieba.lcut(text, cut_all=True))

def to_query(text: str):
    """jieba全模式分词 → 搜索查询"""
    return ' '.join(jieba.lcut(text, cut_all=True))</code></pre>
          </div>
        </div>
        <div>
          <div class="card-title" style="font-size:14px;">全文检索核心参数</div>
          <ul class="feature-list">
            <li>分词器: <code>jieba</code> 全模式</li>
            <li>查询转换: <code>websearch_to_tsquery('simple', query)</code></li>
            <li>排名函数: <code>ts_rank_cd(vector, query, 32)</code></li>
            <li>去重: <code>DISTINCT ON (paragraph_id)</code></li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 8.3 重排序系统 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔄</span> 8.3 重排序系统 (Reranker)</div>
      <div class="highlight-block">
        提供 <strong>8 个重排序提供商</strong>，但仅在<strong>工作流模式</strong>下可用（非默认对话管道）。
      </div>
      <table class="data-table">
        <thead>
          <tr><th>提供商</th><th>实现类</th><th>特点</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in rerankerData" :key="r.provider">
            <td><strong>{{ r.provider }}</strong></td>
            <td><code>{{ r.cls }}</code></td>
            <td>{{ r.feature }}</td>
          </tr>
        </tbody>
      </table>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>重排序流程:</strong><br>
        <code>多个上游检索节点 → 合并文档列表 → reranker.compress_documents() → top_n 过滤 → similarity 阈值过滤 → max_paragraph_char_number 限制</code><br>
        <strong>📂 工作流节点:</strong> <code>apps/application/flow/step_node/reranker_node/</code>
      </div>
    </div>

    <!-- 8.4 检索管道完整流程 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚙️</span> 8.4 检索管道完整流程</div>
      <div class="flow-diagram" style="margin:16px 0;">
        <div class="flow-steps" style="flex-direction:column;align-items:stretch;gap:0;">
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(99,102,241,0.12);border-radius:8px 8px 0 0;">
            <span style="background:#6366f1;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;">1</span>
            <strong>用户查询</strong>
            <code style="margin-left:auto;font-size:12px;">BaseSearchDatasetStep.execute()</code>
          </div>
          <div style="text-align:center;padding:4px;color:#6366f1;font-weight:bold;">↓</div>
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(99,102,241,0.08);">
            <span style="background:#6366f1;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;">2</span>
            <strong>验证 knowledge_id_list</strong>
            <span style="color:#94a3b8;font-size:12px;">必须共享相同嵌入模型</span>
          </div>
          <div style="text-align:center;padding:4px;color:#6366f1;font-weight:bold;">↓</div>
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(99,102,241,0.08);">
            <span style="background:#6366f1;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;">3</span>
            <strong>获取嵌入模型</strong>
            <span style="color:#94a3b8;font-size:12px;">ModelManage缓存, 8h TTL</span>
          </div>
          <div style="text-align:center;padding:4px;color:#6366f1;font-weight:bold;">↓</div>
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(139,92,246,0.12);">
            <span style="background:#8b5cf6;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;">4</span>
            <strong>执行检索</strong>
            <code style="margin-left:auto;font-size:12px;">PGVector.query()</code>
            <span style="color:#94a3b8;font-size:12px;">EMBEDDING / KEYWORDS / BLEND</span>
          </div>
          <div style="text-align:center;padding:4px;color:#8b5cf6;font-weight:bold;">↓</div>
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(139,92,246,0.08);">
            <span style="background:#8b5cf6;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;">5</span>
            <strong>SQL执行 → 原始结果</strong>
            <span style="color:#94a3b8;font-size:12px;">[{paragraph_id, comprehensive_score}]</span>
          </div>
          <div style="text-align:center;padding:4px;color:#8b5cf6;font-weight:bold;">↓</div>
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(236,72,153,0.12);">
            <span style="background:#ec4899;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;">6</span>
            <strong>后处理</strong>
            <span style="color:#94a3b8;font-size:12px;">获取Paragraph → 清理孤立数据 → 附加相似度</span>
          </div>
          <div style="text-align:center;padding:4px;color:#ec4899;font-weight:bold;">↓</div>
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(236,72,153,0.08);border-radius:0 0 8px 8px;">
            <span style="background:#ec4899;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;">7</span>
            <strong>hit_handling_method 判断</strong>
            <span style="color:#94a3b8;font-size:12px;">optimization(排序) / directly_return(≥threshold单条)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 8.5 检索能力评估 -->
    <div class="card">
      <div class="card-title"><span class="icon">⭐</span> 8.5 检索能力评估</div>
      <table class="data-table">
        <thead>
          <tr><th>维度</th><th>能力</th><th>评级</th><th>说明</th></tr>
        </thead>
        <tbody>
          <tr v-for="e in evalData" :key="e.dim">
            <td><strong>{{ e.dim }}</strong></td>
            <td>{{ e.capability }}</td>
            <td>{{ e.rating }}</td>
            <td>{{ e.desc }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

// 8.1 三种检索策略数据
const strategyData = ref([
  {
    name: '向量相似度 (embedding)',
    algorithm: '余弦距离 <=> pgvector',
    score: '1 - cosine_distance',
    chinese: '✅ 语义匹配',
    threshold: '> 0.65',
    note: 'DISTINCT ON 去重，稳定可靠'
  },
  {
    name: '关键词全文 (keywords)',
    algorithm: 'ts_rank_cd 全文检索',
    score: 'ts_rank_cd(search_vector, query)',
    chinese: '✅ jieba分词',
    threshold: '自定义',
    note: 'websearch_to_tsquery，中文支持优秀'
  },
  {
    name: '混合检索 (blend)',
    algorithm: '简单加性融合',
    score: '(1-distance) + ts_similarity',
    chinese: '✅ 语义+关键词',
    threshold: '自定义',
    note: '⚠️ 非归一化加权，量纲不同可改进'
  }
])

// 8.3 重排序提供商数据
const rerankerData = ref([
  { provider: 'Xinference', cls: 'XInferenceReranker', feature: '本地部署' },
  { provider: 'SiliconCloud', cls: 'SiliconCloudReranker', feature: '开源模型' },
  { provider: '百度千帆', cls: 'QfBgeReranker', feature: 'BGE模型' },
  { provider: '阿里百炼', cls: 'AliyunBaiLianReranker', feature: 'DashScope' },
  { provider: 'Ollama', cls: 'OllamaReranker', feature: '⚠️ 余弦相似度模拟' },
  { provider: 'VLLM', cls: 'VllmReranker', feature: 'GPU推理' },
  { provider: 'Docker AI', cls: 'DockerAIReranker', feature: '容器部署' },
  { provider: 'AWS Bedrock', cls: 'BedrockReranker', feature: 'AWS生态' }
])

// 8.5 检索能力评估数据
const evalData = ref([
  { dim: '向量检索', capability: 'pgvector余弦相似度', rating: '✅ 成熟', desc: '稳定可靠' },
  { dim: '全文检索', capability: 'PostgreSQL tsvector + jieba', rating: '✅ 良好', desc: '中文支持优秀' },
  { dim: '混合检索', capability: '简单加性融合', rating: '⚠️ 基础', desc: '非归一化，可改进' },
  { dim: '重排序', capability: '8提供商, 仅工作流', rating: '⚠️ 有限', desc: '默认对话无重排序' },
  { dim: '向量数据库', capability: '仅pgvector', rating: '⚠️ 单一', desc: '无Milvus/ES等选项' },
  { dim: '多语言', capability: 'jieba(中文) + simple(英文)', rating: '✅ 良好', desc: '中英文为主' },
  { dim: '分布式', capability: 'RedisLock + Celery', rating: '✅ 良好', desc: '支持水平扩展' }
])

// ECharts 检索策略能力矩阵
const chartRef = ref(null)

onMounted(() => {
  if (!chartRef.value) return
  const chart = echarts.init(chartRef.value)

  // 检索维度
  const dimensions = ['语义理解', '精确匹配', '中文支持', '混合效果', '可扩展性', '性能']
  const strategies = ['向量检索', '全文检索', '混合检索']

  // 能力评分矩阵 (0-100)
  const scores = [
    [95, 30, 80, 0, 70, 85],   // 向量检索
    [25, 90, 85, 0, 60, 90],   // 全文检索
    [85, 75, 85, 60, 50, 70]   // 混合检索
  ]

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15,23,42,0.95)',
      borderColor: '#334155',
      textStyle: { color: '#e2e8f0' }
    },
    legend: {
      data: strategies,
      top: 0,
      textStyle: { color: '#94a3b8', fontSize: 12 }
    },
    grid: {
      top: 40,
      bottom: 30,
      left: 80,
      right: 30
    },
    xAxis: {
      type: 'value',
      max: 100,
      axisLabel: { color: '#94a3b8', formatter: '{value}%' },
      splitLine: { lineStyle: { color: 'rgba(148,163,184,0.1)' } }
    },
    yAxis: {
      type: 'category',
      data: dimensions,
      axisLabel: { color: '#e2e8f0', fontSize: 12, fontWeight: 'bold' },
      axisLine: { show: false },
      axisTick: { show: false }
    },
    series: strategies.map((name, idx) => ({
      name,
      type: 'bar',
      data: scores[idx],
      barWidth: 12,
      itemStyle: {
        borderRadius: [0, 4, 4, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: ['#6366f1', '#8b5cf6', '#ec4899'][idx] + '80' },
          { offset: 1, color: ['#6366f1', '#8b5cf6', '#ec4899'][idx] }
        ])
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(99,102,241,0.5)'
        }
      }
    }))
  })

  const resizeHandler = () => chart.resize()
  window.addEventListener('resize', resizeHandler)
})
</script>
