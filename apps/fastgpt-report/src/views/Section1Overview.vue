<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§1 项目概览</h2>
      <p>FastGPT 技术架构全面解析 — 核心指标、技术栈与项目结构</p>
    </div>

    <!-- 关键指标 -->
    <div class="metrics-grid">
      <div class="metric-card" v-for="m in metrics" :key="m.label">
        <div class="metric-value">{{ m.value }}</div>
        <div class="metric-label">{{ m.label }}</div>
      </div>
    </div>

    <div class="two-col">
      <!-- 技术栈总览 -->
      <div class="card">
        <div class="card-title"><span class="icon">⚡</span> 技术栈总览</div>
        <table class="data-table">
          <thead><tr><th>技术</th><th>版本</th><th>用途</th></tr></thead>
          <tbody>
            <tr v-for="t in techStack" :key="t.name">
              <td><code>{{ t.name }}</code></td>
              <td>{{ t.ver }}</td>
              <td>{{ t.usage }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Monorepo 架构 -->
      <div class="card">
        <div class="card-title"><span class="icon">📦</span> Monorepo 架构</div>
        <div class="highlight-block">
          FastGPT 采用 Monorepo 管理多包项目，统一依赖版本与构建流程，提升跨模块协作效率。
        </div>
        <table class="data-table">
          <thead><tr><th>目录</th><th>职责</th></tr></thead>
          <tbody>
            <tr v-for="p in packages" :key="p.dir">
              <td><code>{{ p.dir }}</code></td>
              <td>{{ p.desc }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 技术栈构成图表 -->
    <div class="card">
      <div class="card-title"><span class="icon">📊</span> 技术栈构成</div>
      <div id="chart-tech-stack" class="chart-container"></div>
    </div>

    <!-- 核心特性 -->
    <div class="card">
      <div class="card-title"><span class="icon">✨</span> 核心特性</div>
      <div class="two-col">
        <ul class="feature-list">
          <li v-for="f in features.slice(0, 3)" :key="f">{{ f }}</li>
        </ul>
        <ul class="feature-list">
          <li v-for="f in features.slice(3)" :key="f">{{ f }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const metrics = ref([
  { value: '6', label: '训练模式' },
  { value: '3', label: '搜索模式' },
  { value: '7', label: '数据集类型' },
  { value: '34', label: '工作流节点' }
])

const techStack = ref([
  { name: 'Next.js', ver: '16.2', usage: '框架' },
  { name: 'MongoDB', ver: '5.0', usage: '主数据库' },
  { name: 'PostgreSQL+pgvector', ver: '-', usage: '向量数据库' },
  { name: 'Redis', ver: '7.2', usage: '缓存/队列' },
  { name: 'MinIO/S3', ver: '-', usage: '对象存储' },
  { name: 'TypeScript', ver: '5.x', usage: '语言' },
  { name: 'Chakra UI', ver: '-', usage: 'UI 组件' },
  { name: 'ReactFlow', ver: '-', usage: '工作流编辑器' },
  { name: 'BullMQ', ver: '-', usage: '消息队列' },
  { name: 'ECharts', ver: '-', usage: '图表' }
])

const packages = ref([
  { dir: 'packages/global', desc: '共享类型与常量' },
  { dir: 'packages/service', desc: '后端服务逻辑' },
  { dir: 'packages/web', desc: '前端通用组件' },
  { dir: 'projects/app', desc: '主应用入口' },
  { dir: 'plugins/', desc: '模型插件扩展' },
  { dir: 'sdk/', desc: '独立 SDK 封装' }
])

const features = ref([
  'RAG 知识库管理 — 支持 PDF/Word/Excel 等多格式文档导入，自动分块与向量化',
  '可视化工作流编辑 — 拖拽式编排 AI 对话流程，支持条件分支与循环',
  '多模型支持 — OpenAI / Claude / 国内大模型一键切换',
  '插件系统 — 自定义工具与 API 扩展能力',
  'API 开放平台 — 完整 RESTful API，支持第三方集成',
  '多租户权限管理 — 企业级团队协作与数据隔离'
])

onMounted(() => {
  const el = document.getElementById('chart-tech-stack')
  if (!el) return
  const chart = echarts.init(el)
  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    legend: {
      bottom: 0, textStyle: { color: '#94a3b8', fontSize: 12 },
      itemWidth: 12, itemHeight: 12, itemGap: 16
    },
    series: [{
      type: 'pie', radius: ['40%', '70%'], center: ['50%', '45%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: '#1a2236', borderWidth: 2 },
      label: { color: '#e2e8f0', fontSize: 13, formatter: '{b}\n{d}%' },
      labelLine: { lineStyle: { color: '#64748b' } },
      emphasis: {
        itemStyle: { shadowBlur: 20, shadowColor: 'rgba(99,102,241,0.3)' },
        label: { fontSize: 15, fontWeight: 'bold' }
      },
      data: [
        { value: 25, name: '前端框架', itemStyle: { color: '#6366f1' } },
        { value: 20, name: '数据库', itemStyle: { color: '#06b6d4' } },
        { value: 25, name: 'AI/机器学习', itemStyle: { color: '#8b5cf6' } },
        { value: 15, name: '基础设施', itemStyle: { color: '#14b8a6' } },
        { value: 15, name: '开发工具', itemStyle: { color: '#f59e0b' } }
      ]
    }]
  })
  window.addEventListener('resize', () => chart.resize())
})
</script>
