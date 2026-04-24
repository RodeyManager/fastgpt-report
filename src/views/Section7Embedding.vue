<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§7 文本向量化</h2>
      <p>Embedding模型与向量存储 — 多后端向量数据库适配与检索优化</p>
    </div>

    <div class="source-ref-list">
      <div class="ref-title">&#128204; 核心源码</div>
      <div class="source-ref-item"><span class="ref-file">packages/service/core/ai/embedding/index.ts</span> <span class="ref-desc">向量化核心(getVectorsByText, formatVectors)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/common/vectorDB/controller.ts</span> <span class="ref-desc">向量DB抽象层</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/common/vectorDB/pg/index.ts</span> <span class="ref-desc">pgvector实现(HNSW检索)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/global/core/ai/constants.ts</span> <span class="ref-desc">默认模型配置</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/core/ai/config.ts</span> <span class="ref-desc">AI API配置(getAIApi)</span></div>
    </div>

    <div class="two-col">
      <!-- 默认嵌入模型 -->
      <div class="card">
        <div class="card-title"><span class="icon">🧠</span> 默认嵌入模型</div>
        <div class="highlight-block">
          <strong>text-embedding-3-small</strong> (OpenAI)，支持任何OpenAI兼容模型通过配置接入<br/>
          <strong>API路由：</strong><code>userKey</code> &gt; <code>oneapiUrl</code> &gt; <code>AIPROXY</code> &gt; <code>OPENAI_BASE_URL</code>
        </div>
      </div>

      <!-- 向量格式化逻辑 -->
      <div class="card">
        <div class="card-title"><span class="icon">📐</span> 向量格式化逻辑</div>
        <pre class="code-block"><code>function formatVectors(vector, normalization = false) {
  if (vector.length > 1536)
    return normalize(vector.slice(0, 1536));
  if (vector.length < 1536)
    vector = vector.concat(
      new Array(1536 - vector.length).fill(0)
    );
  return normalization
    ? normalize(vector) : vector;
}</code></pre>
        <ul class="feature-list" style="margin-top: 12px">
          <li><strong>固定1536维度</strong> — 零填充 / 截断对齐</li>
          <li><strong>可选L2归一化</strong> — 归一化提升余弦相似度精度</li>
          <li><strong>嵌入类型：</strong><code>db</code>（存储）vs <code>query</code>（查询）</li>
        </ul>
      </div>
    </div>

    <!-- 向量数据库对比 -->
    <div class="card">
      <div class="card-title"><span class="icon">🗄️</span> 向量数据库对比</div>
      <table class="data-table">
        <thead>
          <tr><th>后端</th><th>连接方式</th><th>量化精度</th><th>HNSW配置</th></tr>
        </thead>
        <tbody>
          <tr v-for="db in vectorDbs" :key="db.name">
            <td><strong>{{ db.name }}</strong></td>
            <td><code>{{ db.conn }}</code></td>
            <td>{{ db.precision }}</td>
            <td>{{ db.hnsw }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 雷达图 -->
    <div class="card">
      <div class="card-title"><span class="icon">📊</span> 向量数据库综合对比</div>
      <div id="chart-vector-db" class="chart-container"></div>
    </div>

    <!-- API路由优先级 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔗</span> API路由优先级</div>
      <ul class="feature-list">
        <li v-for="(r, i) in apiRoutes" :key="i">
          <strong>{{ r.label }}</strong> <code>{{ r.key }}</code> — {{ r.desc }}
        </li>
      </ul>
    </div>

    <!-- 向量化与向量插入源码 -->
    <div class="card">
      <div class="card-title"><span class="icon">&#9881;</span> 向量化与向量插入源码</div>
      <div class="code-block">
        <span class="lang-tag">TypeScript</span>
        <pre><span class="code-comment">// packages/service/core/ai/embedding/index.ts</span>
<span class="code-keyword">async function</span> <span class="code-func">getVectorsByText</span>({ model, input, type }) {
  <span class="code-keyword">const</span> ai = <span class="code-func">getAIApi</span>();
  <span class="code-keyword">const</span> result = <span class="code-keyword">await</span> ai.embeddings.<span class="code-func">create</span>({
    model: model.model,
    input: chunk,
    encoding_format: <span class="code-string">'float'</span>,
    ...(type === <span class="code-string">'db'</span> && model.dbConfig),
    ...(type === <span class="code-string">'query'</span> && model.queryConfig)
  });
  <span class="code-keyword">return</span> {
    vectors: result.data.map(i => <span class="code-func">formatVectors</span>(i.embedding)),
    tokens: result.usage.total_tokens
  };
}

<span class="code-comment">// packages/service/common/vectorDB/pg/index.ts</span>
<span class="code-comment">// PostgreSQL HNSW 向量检索</span>
<span class="code-keyword">const</span> sql = <span class="code-string">`
  SET LOCAL hnsw.ef_search = 100;
  SELECT id, collection_id, vector <#> $1 AS score
  FROM modeldata WHERE dataset_id = ANY($2)
  ORDER BY score LIMIT $3
`</span>;</pre>
      </div>
    </div>

    <!-- ========== 强索引 (Enhanced Indexing) ========== -->

    <!-- Card 1: 强索引核心概念 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚡</span> 强索引（Enhanced Indexing）核心概念</div>
      <div class="highlight-block" style="margin-bottom: 20px;">
        <strong>强索引</strong>是对同一Chunk生成多路精炼文本、分别向量化的检索增强策略。检索时多路并行命中，只要命中任意一路，整个Chunk被召回，显著提升召回率与准确率。
      </div>

      <!-- Tree Diagram -->
      <div class="arch-container" style="padding: 24px 32px; margin: 16px 0;">
        <div style="text-align: center; margin-bottom: 20px;">
          <div style="display: inline-block; background: rgba(139,92,246,0.2); border: 2px solid #8b5cf6; border-radius: 10px; padding: 14px 28px;">
            <div style="font-size: 0.72rem; color: #8b5cf6; font-weight: 600; margin-bottom: 4px;">基础文本单元</div>
            <div style="font-size: 1rem; font-weight: 700; color: #fff;">1 Chunk（原文）</div>
          </div>
        </div>

        <!-- Branch lines -->
        <div style="display: flex; justify-content: center; margin-bottom: 8px;">
          <svg width="600" height="40" viewBox="0 0 600 40" style="max-width: 100%;">
            <line x1="300" y1="0" x2="100" y2="40" stroke="#6366f1" stroke-width="2" stroke-dasharray="4,3" opacity="0.6"/>
            <line x1="300" y1="0" x2="300" y2="40" stroke="#06b6d4" stroke-width="2" stroke-dasharray="4,3" opacity="0.6"/>
            <line x1="300" y1="0" x2="500" y2="40" stroke="#f59e0b" stroke-width="2" stroke-dasharray="4,3" opacity="0.6"/>
          </svg>
        </div>

        <!-- 3 Index Types -->
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; text-align: center;">
          <div style="background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3); border-radius: 8px; padding: 14px;">
            <div style="font-size: 0.72rem; color: #6366f1; font-weight: 600; margin-bottom: 6px;">全文索引 Full-Text</div>
            <div style="font-size: 0.85rem; color: #e2e8f0; font-weight: 600;">→ 向量 1</div>
            <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 6px;">保留完整上下文语义</div>
          </div>
          <div style="background: rgba(6,182,212,0.1); border: 1px solid rgba(6,182,212,0.3); border-radius: 8px; padding: 14px;">
            <div style="font-size: 0.72rem; color: #06b6d4; font-weight: 600; margin-bottom: 6px;">关键句索引 Snippet</div>
            <div style="font-size: 0.85rem; color: #e2e8f0; font-weight: 600;">→ 向量 2</div>
            <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 6px;">压缩噪声、强化核心语义</div>
          </div>
          <div style="background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.3); border-radius: 8px; padding: 14px;">
            <div style="font-size: 0.72rem; color: #f59e0b; font-weight: 600; margin-bottom: 6px;">关键词索引 Keyword</div>
            <div style="font-size: 0.85rem; color: #e2e8f0; font-weight: 600;">→ 向量 3</div>
            <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 6px;">强匹配实体/专有名词</div>
          </div>
        </div>

        <div style="text-align: center; margin-top: 16px; padding: 10px; background: rgba(16,185,129,0.08); border: 1px dashed rgba(16,185,129,0.3); border-radius: 8px;">
          <span style="color: #10b981; font-weight: 600; font-size: 0.85rem;">🔍 检索时多路并行命中 → 只要命中任意一路，整个 Chunk 被召回</span>
        </div>
      </div>

      <ul class="feature-list">
        <li><strong>分块（Chunk）</strong> = 基础文本单元，由文档分割产生</li>
        <li><strong>强索引（Index）</strong> = 对同一 Chunk 额外生成的多段精炼文本，每组单独向量化</li>
        <li><strong>多路并行</strong> = 检索时同时对全文/关键句/关键词/摘要向量做相似度计算，合并去重</li>
      </ul>
    </div>

    <!-- Card 2: 4种强索引方法详解 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔬</span> 四种强索引方法详解</div>
      <table class="data-table">
        <thead>
          <tr>
            <th>方法</th>
            <th>内容</th>
            <th>生成方式</th>
            <th>核心作用</th>
            <th>适用场景</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>
              <span class="tag tag-blue">全文索引</span><br/>
              <span style="font-size: 0.72rem; color: #64748b;">Full-Text</span>
            </td>
            <td>直接用 Chunk 原文</td>
            <td><code>chunk.text</code></td>
            <td>保留完整上下文语义</td>
            <td>长句、模糊意图查询</td>
          </tr>
          <tr>
            <td>
              <span class="tag tag-cyan">关键句索引</span><br/>
              <span style="font-size: 0.72rem; color: #64748b;">Key Sentence</span>
            </td>
            <td>提取 2-3 句核心句子</td>
            <td>句号/分号切句 → 句间相似度 → 选高相关核心句</td>
            <td>压缩噪声、强化核心语义</td>
            <td>短查询精准命中</td>
          </tr>
          <tr>
            <td>
              <span class="tag tag-orange">关键词索引</span><br/>
              <span style="font-size: 0.72rem; color: #64748b;">Keyword</span>
            </td>
            <td>5-10 个术语/实体</td>
            <td>分词 + 停用词过滤 + TF-IDF → Top 关键词</td>
            <td>强匹配实体/专有名词</td>
            <td>产品名、工号、政策编号</td>
          </tr>
          <tr>
            <td>
              <span class="tag tag-purple">摘要索引</span><br/>
              <span style="font-size: 0.72rem; color: #64748b;">Summary</span>
            </td>
            <td>1 句精简摘要（≤100字）</td>
            <td>内置 LLM（如 Qwen-7B）生成</td>
            <td>极致压缩、保留核心意图</td>
            <td>法律/合同/技术手册</td>
          </tr>
        </tbody>
      </table>

      <!-- Stats highlight -->
      <div class="metrics-grid" style="margin-top: 20px;">
        <div class="metric-card" style="border-color: rgba(6,182,212,0.3);">
          <div class="metric-value">+20%</div>
          <div class="metric-label">关键句索引 召回率提升</div>
        </div>
        <div class="metric-card" style="border-color: rgba(6,182,212,0.3);">
          <div class="metric-value">+15%</div>
          <div class="metric-label">关键句索引 准确率提升</div>
        </div>
        <div class="metric-card" style="border-color: rgba(245,158,11,0.3);">
          <div class="metric-value">+10%</div>
          <div class="metric-label">关键词索引 召回率提升</div>
        </div>
        <div class="metric-card" style="border-color: rgba(139,92,246,0.3);">
          <div class="metric-value">+12%</div>
          <div class="metric-label">摘要索引 召回率提升</div>
        </div>
      </div>
    </div>

    <!-- Card 3: 强索引核心优势 -->
    <div class="card">
      <div class="card-title"><span class="icon">🎯</span> 强索引核心优势</div>
      <div class="three-col">
        <!-- 优势1: 召回率高 -->
        <div style="background: rgba(16,185,129,0.06); border: 1px solid rgba(16,185,129,0.2); border-radius: 8px; padding: 20px;">
          <div style="font-size: 0.95rem; font-weight: 700; color: #10b981; margin-bottom: 12px;">📌 召回率高（不漏）</div>
          <ul class="feature-list">
            <li><strong>全文</strong>管整体语义</li>
            <li><strong>关键句</strong>管细节语义</li>
            <li><strong>关键词</strong>管精确实体</li>
            <li><strong>摘要</strong>管长文压缩</li>
          </ul>
          <div class="highlight-block" style="margin-top: 12px; border-left-color: #10b981; background: rgba(16,185,129,0.08); font-size: 0.82rem;">
            短查询 → 命中关键词<br/>
            长查询 → 命中全文<br/>
            模糊查询 → 命中摘要
          </div>
        </div>

        <!-- 优势2: 准确率高 -->
        <div style="background: rgba(99,102,241,0.06); border: 1px solid rgba(99,102,241,0.2); border-radius: 8px; padding: 20px;">
          <div style="font-size: 0.95rem; font-weight: 700; color: #6366f1; margin-bottom: 12px;">🎯 准确率高（不错）</div>
          <ul class="feature-list">
            <li>多向量交叉验证减少偏见</li>
            <li>关键句/摘要过滤噪声让排序更准</li>
            <li><strong>RRF 融合</strong>时同 Chunk 多向量命中 → 分数叠加 → 排最前</li>
          </ul>
          <div class="highlight-block" style="margin-top: 12px; border-left-color: #6366f1; font-size: 0.82rem;">
            同一 Chunk 被多条路径命中 → RRF 分数叠加 → 排序更靠前 → 准确率显著提升
          </div>
        </div>

        <!-- 优势3: 适配复杂文档 -->
        <div style="background: rgba(245,158,11,0.06); border: 1px solid rgba(245,158,11,0.2); border-radius: 8px; padding: 20px;">
          <div style="font-size: 0.95rem; font-weight: 700; color: #f59e0b; margin-bottom: 12px;">📚 适配复杂文档</div>
          <ul class="feature-list">
            <li><strong>技术文档</strong>：关键词 + 关键句</li>
            <li><strong>法律文档</strong>：全文 + 摘要</li>
            <li><strong>手册类</strong>：关键句 + 关键词</li>
          </ul>
          <div class="highlight-block" style="margin-top: 12px; border-left-color: #f59e0b; background: rgba(245,158,11,0.06); font-size: 0.82rem;">
            不同文档类型自动适配最优索引组合，无需人工配置
          </div>
        </div>
      </div>
    </div>

    <!-- Card 4: 配置与默认值 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚙️</span> 配置与默认值</div>
      <div class="two-col">
        <div>
          <div style="font-size: 0.88rem; font-weight: 600; color: #06b6d4; margin-bottom: 12px;">默认索引策略</div>
          <ul class="feature-list">
            <li><span class="tag tag-green" style="margin-right: 6px;">默认开启</span> 全文 + 关键句 + 关键词（3 路）</li>
            <li><span class="tag tag-purple" style="margin-right: 6px;">手动开启</span> 摘要索引（长文档场景推荐）</li>
            <li><span class="tag tag-blue" style="margin-right: 6px;">向量模型</span> 默认 BGE-large（强语义）</li>
            <li><span class="tag tag-orange" style="margin-right: 6px;">检索融合</span> RRF + BGE-Rerank（精排）</li>
          </ul>
        </div>
        <div>
          <div style="font-size: 0.88rem; font-weight: 600; color: #06b6d4; margin-bottom: 12px;">推荐配置组合</div>
          <table class="data-table" style="font-size: 0.82rem;">
            <thead>
              <tr><th>场景</th><th>推荐索引</th></tr>
            </thead>
            <tbody>
              <tr>
                <td>通用知识库</td>
                <td><span class="tag tag-green" style="margin-right: 4px;">全文</span><span class="tag tag-cyan" style="margin-right: 4px;">关键句</span><span class="tag tag-orange">关键词</span></td>
              </tr>
              <tr>
                <td>法律/合同</td>
                <td><span class="tag tag-green" style="margin-right: 4px;">全文</span><span class="tag tag-purple">摘要</span></td>
              </tr>
              <tr>
                <td>产品手册</td>
                <td><span class="tag tag-cyan" style="margin-right: 4px;">关键句</span><span class="tag tag-orange">关键词</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Card 5: 召回率/准确率对比图 -->
    <div class="card">
      <div class="card-title"><span class="icon">📊</span> 强索引召回率与准确率提升对比</div>
      <div id="chart-enhanced-index" class="chart-container"></div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const vectorDbs = ref([
  { name: 'PostgreSQL+pgvector', conn: 'PG_URL', precision: '32位 / 16位 (HALFVEC)', hnsw: 'm=32, ef_construction=128' },
  { name: 'Milvus / Zilliz', conn: 'MILVUS_ADDRESS', precision: '原生', hnsw: 'efConstruction=32, M=64' },
  { name: 'OceanBase', conn: 'OCEANBASE_ADDRESS', precision: '32 / 8 / 1位 (SQ/BQ)', hnsw: 'm=16, ef_construction=200' },
  { name: 'openGauss', conn: 'OPENGAUSS_ADDRESS', precision: '32位', hnsw: 'm=32, ef_construction=128' },
  { name: 'SeekDB', conn: 'SEEKDB_ADDRESS', precision: '原生', hnsw: '复用OceanBase' }
])

const apiRoutes = ref([
  { label: '① 用户自定义 Key.baseUrl', key: 'userKey', desc: '最高优先级，用户级覆盖' },
  { label: '② 系统配置', key: 'systemEnv.oneapiUrl', desc: '运维级 OneAPI 中转地址' },
  { label: '③ AIProxy 代理服务', key: 'AIPROXY_API_ENDPOINT', desc: '内置代理转发，开箱即用' },
  { label: '④ 直接连接（回退）', key: 'OPENAI_BASE_URL', desc: '兜底方案，直连 OpenAI' }
])

onMounted(() => {
  const el = document.getElementById('chart-vector-db')
  if (!el) return
  const chart = echarts.init(el)
  const indicators = [
    { name: '性能', max: 100 },
    { name: '扩展性', max: 100 },
    { name: '精度', max: 100 },
    { name: '易用性', max: 100 },
    { name: '生态', max: 100 }
  ]
  const colors = ['#6366f1', '#06b6d4', '#8b5cf6', '#14b8a6', '#f59e0b']
  const seriesData = [
    { value: [72, 65, 88, 90, 92], name: 'PostgreSQL+pgvector' },
    { value: [92, 95, 95, 70, 78], name: 'Milvus / Zilliz' },
    { value: [78, 82, 85, 75, 65], name: 'OceanBase' },
    { value: [70, 60, 88, 85, 70], name: 'openGauss' },
    { value: [80, 78, 90, 72, 60], name: 'SeekDB' }
  ]
  chart.setOption({
    tooltip: {},
    legend: {
      bottom: 0, textStyle: { color: '#94a3b8', fontSize: 11 },
      itemWidth: 12, itemHeight: 12, itemGap: 14
    },
    radar: {
      indicator: indicators,
      shape: 'polygon',
      splitNumber: 4,
      axisName: { color: '#e2e8f0', fontSize: 12 },
      splitLine: { lineStyle: { color: 'rgba(148,163,184,0.15)' } },
      splitArea: { areaStyle: { color: ['rgba(99,102,241,0.02)', 'rgba(99,102,241,0.05)'] } },
      axisLine: { lineStyle: { color: 'rgba(148,163,184,0.2)' } }
    },
    series: [{
      type: 'radar',
      data: seriesData.map((d, i) => ({
        ...d,
        lineStyle: { color: colors[i], width: 2 },
        areaStyle: { color: colors[i], opacity: 0.08 },
        itemStyle: { color: colors[i] },
        symbol: 'circle', symbolSize: 5
      }))
    }]
  })
  window.addEventListener('resize', () => chart.resize())

  // Enhanced Indexing bar chart
  const el2 = document.getElementById('chart-enhanced-index')
  if (el2) {
    const chart2 = echarts.init(el2)
    chart2.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: 'rgba(15,23,42,0.95)',
        borderColor: 'rgba(99,102,241,0.3)',
        textStyle: { color: '#e2e8f0', fontSize: 12 }
      },
      legend: {
        bottom: 0,
        textStyle: { color: '#94a3b8', fontSize: 11 },
        itemWidth: 12, itemHeight: 12, itemGap: 20
      },
      grid: {
        left: '3%', right: '4%', bottom: '12%', top: '10%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: ['全文 (Baseline)', '关键句', '关键词', '摘要'],
        axisLabel: { color: '#94a3b8', fontSize: 11 },
        axisLine: { lineStyle: { color: 'rgba(148,163,184,0.2)' } }
      },
      yAxis: {
        type: 'value',
        name: '提升百分比 (%)',
        nameTextStyle: { color: '#94a3b8', fontSize: 11 },
        axisLabel: { color: '#94a3b8', fontSize: 11 },
        splitLine: { lineStyle: { color: 'rgba(148,163,184,0.1)' } }
      },
      series: [
        {
          name: '召回率提升',
          type: 'bar',
          barWidth: '30%',
          data: [
            { value: 0, itemStyle: { color: '#64748b' } },
            { value: 20, itemStyle: { color: '#06b6d4' } },
            { value: 10, itemStyle: { color: '#f59e0b' } },
            { value: 12, itemStyle: { color: '#8b5cf6' } }
          ],
          label: {
            show: true, position: 'top',
            color: '#e2e8f0', fontSize: 12, fontWeight: 600,
            formatter: (p) => p.value === 0 ? 'Baseline' : `+${p.value}%`
          }
        },
        {
          name: '准确率提升',
          type: 'bar',
          barWidth: '30%',
          data: [
            { value: 0, itemStyle: { color: 'rgba(100,116,139,0.4)' } },
            { value: 15, itemStyle: { color: '#14b8a6' } },
            { value: 8, itemStyle: { color: '#f59e0b' } },
            { value: 10, itemStyle: { color: '#a78bfa' } }
          ],
          label: {
            show: true, position: 'top',
            color: '#94a3b8', fontSize: 11,
            formatter: (p) => p.value === 0 ? 'Baseline' : `+${p.value}%`
          }
        }
      ]
    })
    window.addEventListener('resize', () => chart2.resize())
  }
})
</script>
