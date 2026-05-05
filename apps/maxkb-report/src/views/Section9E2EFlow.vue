<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§9 RAG 端到端流程</h2>
      <p>完整数据管道：文档摄入 → 向量化存储 → 检索召回 → LLM生成</p>
    </div>

    <!-- 9.1 完整数据流 Sankey 图 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔀</span> 9.1 完整数据流 — Sankey 全景</div>
      <div ref="sankeyRef" style="height:520px;"></div>
    </div>

    <!-- 9.1 管道阶段说明 -->
    <div class="card">
      <div class="card-title"><span class="icon">📋</span> 9.1 管道阶段详解</div>
      <div class="flow-diagram" style="margin:16px 0;">
        <div class="flow-steps" style="flex-direction:column;align-items:stretch;gap:0;">
          <!-- 文档摄入阶段 -->
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(99,102,241,0.12);border-radius:8px 8px 0 0;">
            <span style="background:#6366f1;color:#fff;padding:2px 10px;border-radius:4px;font-size:12px;font-weight:600;">摄入阶段</span>
            <strong>文档上传 → 格式Handler → SplitModel → 子分块</strong>
            <code style="margin-left:auto;font-size:11px;">PDF/DOCX/HTML/XLSX/CSV/TXT/MD</code>
          </div>
          <div style="text-align:center;padding:4px;color:#6366f1;font-weight:bold;">↓</div>
          <!-- 存储+异步 -->
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(139,92,246,0.12);">
            <span style="background:#8b5cf6;color:#fff;padding:2px 10px;border-radius:4px;font-size:12px;font-weight:600;">存储阶段</span>
            <strong>段落存储 → Celery异步 → 向量化 + 问题生成</strong>
            <code style="margin-left:auto;font-size:11px;">embed_query() / LLM生成</code>
          </div>
          <div style="text-align:center;padding:4px;color:#8b5cf6;font-weight:bold;">↓</div>
          <!-- 向量存储 -->
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(236,72,153,0.12);">
            <span style="background:#ec4899;color:#fff;padding:2px 10px;border-radius:4px;font-size:12px;font-weight:600;">索引阶段</span>
            <strong>pgvector Embedding表 + Problem关联表</strong>
            <code style="margin-left:auto;font-size:11px;">HNSW索引加速</code>
          </div>
          <div style="text-align:center;padding:4px;color:#ec4899;font-weight:bold;">─ ─ ─ ─ ─ ─ ─ ─ 检索阶段 ─ ─ ─ ─ ─ ─ ─ ─</div>
          <!-- 检索阶段 -->
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(245,158,11,0.12);">
            <span style="background:#f59e0b;color:#fff;padding:2px 10px;border-radius:4px;font-size:12px;font-weight:600;">检索阶段</span>
            <strong>用户查询 → 查询嵌入 → 向量/全文/混合检索</strong>
            <code style="margin-left:auto;font-size:11px;">段落匹配</code>
          </div>
          <div style="text-align:center;padding:4px;color:#f59e0b;font-weight:bold;">↓</div>
          <!-- 生成阶段 -->
          <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;background:rgba(51,112,255,0.12);border-radius:0 0 8px 8px;">
            <span style="background:#3370ff;color:#fff;padding:2px 10px;border-radius:4px;font-size:12px;font-weight:600;">生成阶段</span>
            <strong>可选重排序(工作流) → LLM生成回答</strong>
            <code style="margin-left:auto;font-size:11px;">最终响应返回用户</code>
          </div>
        </div>
      </div>
    </div>

    <!-- 9.2 关键性能优化点 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚡</span> 9.2 关键性能优化点</div>
      <table class="data-table">
        <thead>
          <tr><th>优化策略</th><th>实现方式</th><th>效果</th></tr>
        </thead>
        <tbody>
          <tr v-for="opt in perfData" :key="opt.name">
            <td><strong>{{ opt.name }}</strong></td>
            <td><code>{{ opt.impl }}</code></td>
            <td>{{ opt.effect }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 性能优化可视化 -->
    <div class="card">
      <div class="card-title"><span class="icon">📈</span> 优化点影响范围</div>
      <div ref="barRef" style="height:360px;"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

// 性能优化数据
const perfData = ref([
  { name: 'HNSW索引', impl: 'create_knowledge_index()', effect: 'pgvector近似最近邻加速' },
  { name: '模型缓存', impl: 'ModelManage 8h TTL', effect: '避免重复加载嵌入模型' },
  { name: '任务去重', impl: 'celery-once QueueOnce', effect: '防止重复嵌入计算' },
  { name: '分布式锁', impl: 'RedisLock', effect: '并发安全' },
  { name: '批量操作', impl: 'bulk_create()', effect: '批量向量插入' },
  { name: '连接池', impl: 'dj_db_conn_pool 20+80', effect: 'PostgreSQL连接复用' },
  { name: '文件去重', impl: 'SHA256哈希', effect: '相同文件不重复存储' },
  { name: 'ZIP压缩', impl: 'Large Object压缩', effect: '节省存储空间' },
])

// Sankey 图表引用
const sankeyRef = ref(null)
// 柱状图引用
const barRef = ref(null)

onMounted(() => {
  // ── Sankey 端到端流程图 ──
  if (sankeyRef.value) {
    const sankeyChart = echarts.init(sankeyRef.value)

    sankeyChart.setOption({
      tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove',
        backgroundColor: 'rgba(15,23,42,0.9)',
        borderColor: '#6366f1',
        textStyle: { color: '#e2e8f0', fontSize: 13 }
      },
      series: [{
        type: 'sankey',
        layout: 'none',
        layoutIterations: 0,
        emphasis: {
          focus: 'adjacency'
        },
        nodeAlign: 'left',
        nodeGap: 12,
        nodeWidth: 22,
        draggable: true,
        label: {
          color: '#e2e8f0',
          fontSize: 12,
          fontWeight: 'bold'
        },
        lineStyle: {
          color: 'gradient',
          curveness: 0.5,
          opacity: 0.35
        },
        itemStyle: {
          borderWidth: 0
        },
        // 节点数据
        data: [
          // ── 摄入阶段 ──
          { name: '文档上传', itemStyle: { color: '#6366f1' } },
          { name: 'PDF', itemStyle: { color: '#818cf8' } },
          { name: 'DOCX', itemStyle: { color: '#818cf8' } },
          { name: 'HTML', itemStyle: { color: '#818cf8' } },
          { name: 'XLSX/CSV', itemStyle: { color: '#818cf8' } },
          { name: 'TXT/MD', itemStyle: { color: '#818cf8' } },
          { name: '格式Handler', itemStyle: { color: '#7c3aed' } },
          { name: 'SplitModel', itemStyle: { color: '#7c3aed' } },
          { name: '标题树解析', itemStyle: { color: '#a78bfa' } },
          { name: '智能分割', itemStyle: { color: '#a78bfa' } },
          { name: '子分块(256字符)', itemStyle: { color: '#8b5cf6' } },
          // ── 存储阶段 ──
          { name: '段落存储', itemStyle: { color: '#ec4899' } },
          { name: 'Celery异步任务', itemStyle: { color: '#f472b6' } },
          // ── 索引阶段 ──
          { name: '向量化', itemStyle: { color: '#f59e0b' } },
          { name: '问题生成', itemStyle: { color: '#f59e0b' } },
          { name: 'pgvector', itemStyle: { color: '#fbbf24' } },
          { name: 'Problem+Mapping', itemStyle: { color: '#fbbf24' } },
          // ── 检索阶段 ──
          { name: '用户查询', itemStyle: { color: '#3370ff' } },
          { name: '查询嵌入', itemStyle: { color: '#5b8fff' } },
          { name: '向量检索', itemStyle: { color: '#7f3bf5' } },
          { name: '全文检索', itemStyle: { color: '#9b5ff5' } },
          { name: '混合检索', itemStyle: { color: '#b585f7' } },
          { name: '段落匹配', itemStyle: { color: '#3370ff' } },
          // ── 生成阶段 ──
          { name: '重排序(可选)', itemStyle: { color: '#06b6d4' } },
          { name: 'LLM生成回答', itemStyle: { color: '#3b82f6' } },
        ],
        // 边数据
        links: [
          // ── 文档上传 → 各格式 ──
          { source: '文档上传', target: 'PDF', value: 20 },
          { source: '文档上传', target: 'DOCX', value: 18 },
          { source: '文档上传', target: 'HTML', value: 10 },
          { source: '文档上传', target: 'XLSX/CSV', value: 12 },
          { source: '文档上传', target: 'TXT/MD', value: 8 },
          // ── 各格式 → Handler ──
          { source: 'PDF', target: '格式Handler', value: 20 },
          { source: 'DOCX', target: '格式Handler', value: 18 },
          { source: 'HTML', target: '格式Handler', value: 10 },
          { source: 'XLSX/CSV', target: '格式Handler', value: 12 },
          { source: 'TXT/MD', target: '格式Handler', value: 8 },
          // ── Handler → SplitModel ──
          { source: '格式Handler', target: 'SplitModel', value: 68 },
          // ── SplitModel → 两种策略 ──
          { source: 'SplitModel', target: '标题树解析', value: 35 },
          { source: 'SplitModel', target: '智能分割', value: 33 },
          // ── 策略 → 子分块 ──
          { source: '标题树解析', target: '子分块(256字符)', value: 35 },
          { source: '智能分割', target: '子分块(256字符)', value: 33 },
          // ── 子分块 → 段落存储 ──
          { source: '子分块(256字符)', target: '段落存储', value: 68 },
          // ── 段落存储 → Celery ──
          { source: '段落存储', target: 'Celery异步任务', value: 68 },
          // ── Celery → 向量化/问题生成 ──
          { source: 'Celery异步任务', target: '向量化', value: 45 },
          { source: 'Celery异步任务', target: '问题生成', value: 23 },
          // ── 向量化/问题生成 → 存储 ──
          { source: '向量化', target: 'pgvector', value: 45 },
          { source: '问题生成', target: 'Problem+Mapping', value: 23 },
          // ── 检索阶段 ──
          { source: '用户查询', target: '查询嵌入', value: 50 },
          { source: '查询嵌入', target: '向量检索', value: 22 },
          { source: '查询嵌入', target: '全文检索', value: 12 },
          { source: '查询嵌入', target: '混合检索', value: 16 },
          { source: '向量检索', target: '段落匹配', value: 22 },
          { source: '全文检索', target: '段落匹配', value: 12 },
          { source: '混合检索', target: '段落匹配', value: 16 },
          // ── 段落匹配 → 重排序 ──
          { source: '段落匹配', target: '重排序(可选)', value: 30 },
          // ── 重排序 → LLM ──
          { source: '重排序(可选)', target: 'LLM生成回答', value: 30 },
        ]
      }]
    })

    const resizeSankey = () => sankeyChart.resize()
    window.addEventListener('resize', resizeSankey)
  }

  // ── 性能优化影响范围柱状图 ──
  if (barRef.value) {
    const barChart = echarts.init(barRef.value)

    const categories = ['HNSW索引', '模型缓存', '任务去重', '分布式锁', '批量操作', '连接池', '文件去重', 'ZIP压缩']
    // 影响分值 (1-10)
    const perfScores = [9, 8, 7, 6, 8, 7, 5, 4]
    // 作用域标签
    const scopeLabels = ['检索加速', '推理加速', '计算效率', '并发安全', '写入性能', '连接效率', '存储节省', '存储节省']

    barChart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: 'rgba(15,23,42,0.9)',
        borderColor: '#6366f1',
        textStyle: { color: '#e2e8f0' },
        formatter: (params) => {
          const d = params[0]
          return `<strong>${d.name}</strong><br/>影响分值: <span style="color:#a5f3fc;font-weight:bold">${d.value}/10</span><br/>作用域: ${scopeLabels[d.dataIndex]}`
        }
      },
      grid: {
        top: 30,
        bottom: 40,
        left: 80,
        right: 30,
        containLabel: false
      },
      xAxis: {
        type: 'value',
        max: 10,
        axisLabel: { color: '#94a3b8' },
        axisLine: { lineStyle: { color: '#334155' } },
        splitLine: { lineStyle: { color: '#1e293b' } }
      },
      yAxis: {
        type: 'category',
        data: categories,
        inverse: true,
        axisLabel: {
          color: '#e2e8f0',
          fontSize: 12,
          fontWeight: 'bold'
        },
        axisLine: { show: false },
        axisTick: { show: false }
      },
      series: [{
        type: 'bar',
        data: perfScores.map((v, i) => ({
          value: v,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: v >= 8 ? '#6366f1' : v >= 6 ? '#8b5cf6' : '#a78bfa' },
              { offset: 1, color: v >= 8 ? '#a5f3fc' : v >= 6 ? '#c4b5fd' : '#ddd6fe' }
            ]),
            borderRadius: [0, 4, 4, 0]
          }
        })),
        barWidth: 18,
        label: {
          show: true,
          position: 'right',
          color: '#94a3b8',
          fontSize: 12,
          formatter: '{c}/10'
        }
      }]
    })

    const resizeBar = () => barChart.resize()
    window.addEventListener('resize', resizeBar)
  }
})
</script>
