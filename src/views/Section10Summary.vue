<template>
  <section class="section-page">
    <div class="section-header">
      <h2>技术总结与对比</h2>
      <p>FastGPT知识库管理核心技术评估</p>
    </div>

    <!-- 能力雷达图 -->
    <div class="card">
      <h3 class="card-title"><span class="icon">◈</span> 核心能力评估</h3>
      <div id="chart-capability-radar" class="chart-container"></div>
    </div>

    <!-- 八大技术亮点 -->
    <div class="card">
      <h3 class="card-title"><span class="icon">◈</span> 八大技术亮点</h3>
      <table class="data-table">
        <thead><tr><th>#</th><th>技术点</th><th>核心优势</th></tr></thead>
        <tbody>
          <tr v-for="item in highlights" :key="item.id">
            <td>{{ item.id }}</td>
            <td><span :class="item.tag">{{ item.name }}</span></td>
            <td>{{ item.desc }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 技术成熟度曲线 -->
    <div class="card">
      <h3 class="card-title"><span class="icon">◈</span> 技术成熟度演进</h3>
      <div id="chart-maturity-line" class="chart-container"></div>
    </div>

    <!-- 综合评价 -->
    <div class="card">
      <h3 class="card-title"><span class="icon">◈</span> 综合评价</h3>
      <div class="highlight-block">
        FastGPT构建了一套完整的知识库管理技术栈, 从文档上传到智能检索形成闭环. 其递归多策略分块算法和双通道混合检索架构在开源RAG平台中处于领先水平. 模块化设计使得各组件可独立升级, 5种向量数据库后端和插件系统为企业级部署提供了灵活性. 改进空间在于: 多语言分词优化, 更细粒度的权限控制, 以及向量维度的自适应支持.
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const highlights = ref([
  { id: 1, name: '递归多策略文本分割', tag: 'tag tag-blue', desc: '12+规则优先级分割, Markdown标题继承, 代码块保护' },
  { id: 2, name: '双通道混合检索+RRF', tag: 'tag tag-cyan', desc: '向量+全文双通道, Reciprocal Rank Fusion融合' },
  { id: 3, name: '5种可插拔向量数据库', tag: 'tag tag-green', desc: 'pgvector/Milvus/OceanBase/openGauss/SeekDB' },
  { id: 4, name: 'LLM增强QA生成', tag: 'tag tag-purple', desc: '自动生成问答对, 段落重构, 自定义Prompt' },
  { id: 5, name: '多模态VLM支持', tag: 'tag tag-blue', desc: '图片描述生成, 图片知识库, GridFS+S3存储' },
  { id: 6, name: 'Worker线程架构', tag: 'tag tag-cyan', desc: 'SharedArrayBuffer零拷贝, CPU密集任务隔离' },
  { id: 7, name: '1536维固定向量+归一化', tag: 'tag tag-green', desc: '零填充/截断, L2归一化, 跨模型兼容' },
  { id: 8, name: '亚模优化查询扩展', tag: 'tag tag-purple', desc: 'Lazy Greedy选择, 余弦相似度多样性保证' },
])

const charts = []

const initRadar = () => {
  const el = document.getElementById('chart-capability-radar')
  if (!el) return
  const chart = echarts.init(el)
  charts.push(chart)
  chart.setOption({
    tooltip: { trigger: 'item' },
    radar: {
      indicator: [
        { name: '知识库管理', max: 100 },
        { name: '文档解析', max: 100 },
        { name: '文本分块', max: 100 },
        { name: '向量检索', max: 100 },
        { name: '多模态支持', max: 100 },
        { name: '可扩展性', max: 100 },
      ],
      shape: 'polygon',
      splitNumber: 5,
      axisName: { color: '#94a3b8', fontSize: 12 },
      splitLine: { lineStyle: { color: 'rgba(99,102,241,0.15)' } },
      splitArea: { areaStyle: { color: ['rgba(99,102,241,0.02)', 'rgba(99,102,241,0.05)'] } },
      axisLine: { lineStyle: { color: 'rgba(99,102,241,0.2)' } },
    },
    series: [{
      type: 'radar',
      data: [{
        value: [90, 85, 92, 88, 75, 95],
        name: 'FastGPT',
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(99,102,241,0.45)' },
            { offset: 1, color: 'rgba(139,92,246,0.08)' },
          ]),
        },
        lineStyle: { color: '#6366f1', width: 2 },
        itemStyle: { color: '#6366f1' },
        symbol: 'circle', symbolSize: 6,
      }],
    }],
  })
}

const initLine = () => {
  const el = document.getElementById('chart-maturity-line')
  if (!el) return
  const chart = echarts.init(el)
  charts.push(chart)
  const versions = ['基础RAG(v1)', '多模型支持(v2)', '可视化工作流(v3)', '企业级特性(v4)']
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['检索精度', '文档支持', '多模态', '可扩展性'], textStyle: { color: '#94a3b8', fontSize: 12 }, top: 0 },
    grid: { left: 50, right: 30, top: 40, bottom: 35 },
    xAxis: { type: 'category', data: versions, axisLine: { lineStyle: { color: 'rgba(99,102,241,0.3)' } }, axisLabel: { color: '#94a3b8' } },
    yAxis: { type: 'value', max: 100, splitLine: { lineStyle: { color: 'rgba(99,102,241,0.1)' } }, axisLabel: { color: '#64748b' } },
    series: [
      { name: '检索精度', type: 'line', smooth: true, data: [60, 75, 85, 92], lineStyle: { color: '#6366f1' }, itemStyle: { color: '#6366f1' } },
      { name: '文档支持', type: 'line', smooth: true, data: [40, 65, 80, 88], lineStyle: { color: '#06b6d4' }, itemStyle: { color: '#06b6d4' } },
      { name: '多模态', type: 'line', smooth: true, data: [10, 30, 55, 75], lineStyle: { color: '#10b981' }, itemStyle: { color: '#10b981' } },
      { name: '可扩展性', type: 'line', smooth: true, data: [30, 55, 78, 95], lineStyle: { color: '#8b5cf6' }, itemStyle: { color: '#8b5cf6' } },
    ],
  })
}

onMounted(() => {
  initRadar()
  initLine()
  window.addEventListener('resize', () => charts.forEach(c => c.resize()))
})

onUnmounted(() => {
  charts.forEach(c => c.dispose())
  charts.length = 0
})
</script>
