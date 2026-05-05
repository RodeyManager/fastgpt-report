<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§9 总结与评价</h2>
      <p>RAGFlow RAG 底座能力综合评价与核心优劣势分析</p>
    </div>

    <!-- 能力评分表 -->
    <div class="card">
      <div class="card-title"><span class="icon">📊</span> 能力评分总览</div>
      <table class="data-table">
        <thead>
          <tr><th>能力维度</th><th>评分</th><th>说明</th></tr>
        </thead>
        <tbody>
          <tr v-for="item in capabilityScores" :key="item.dimension">
            <td><strong>{{ item.dimension }}</strong></td>
            <td>{{ item.stars }}</td>
            <td>{{ item.desc }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 雷达图 -->
    <div class="card">
      <div class="card-title"><span class="icon">🎯</span> 能力雷达图</div>
      <div ref="chartRef" class="chart-container"></div>
    </div>

    <div class="two-col">
      <!-- 核心优势 -->
      <div class="card">
        <div class="card-title"><span class="icon">✅</span> 核心优势</div>
        <ul class="feature-list">
          <li v-for="s in strengths" :key="s">{{ s }}</li>
        </ul>
      </div>

      <!-- 主要不足 -->
      <div class="card">
        <div class="card-title"><span class="icon">⚠️</span> 主要不足</div>
        <ul class="feature-list">
          <li v-for="w in weaknesses" :key="w">{{ w }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

// 能力评分数据
const capabilityScores = ref([
  { dimension: '知识库管理', stars: '⭐⭐⭐⭐', desc: '支持多知识库、多租户管理，具备基础 CRUD 与权限控制', score: 4 },
  { dimension: '文档上传', stars: '⭐⭐⭐⭐', desc: '支持 PDF/DOCX/PPTX/XLSX/图片/HTML 等多格式上传，含拖拽与批量操作', score: 4 },
  { dimension: '文档解析', stars: '⭐⭐⭐⭐⭐', desc: '6 种 PDF 解析策略，自研 OCR + 布局识别 + 表格结构识别模型链', score: 5 },
  { dimension: '数据清洗', stars: '⭐⭐⭐', desc: '基础去空白、去重（chunk 级 xxhash），缺少文档级去重与样板检测', score: 3 },
  { dimension: '文本分块', stars: '⭐⭐⭐⭐⭐', desc: '15 种专用分块器覆盖论文/法律/书籍/简历等场景，深度优化', score: 5 },
  { dimension: '向量化', stars: '⭐⭐⭐⭐⭐', desc: '35+ Embedding 提供商，18+ Reranker，4 种向量引擎灵活切换', score: 5 },
  { dimension: '检索', stars: '⭐⭐⭐⭐', desc: '文本 5% + 向量 95% 混合检索，支持 GraphRAG 三级知识图谱检索', score: 4 }
])

// 核心优势
const strengths = ref([
  '深度文档理解：自研 OCR + 布局识别 + 表格结构识别 ONNX 模型链',
  '多策略解析：6 种 PDF 解析策略，适配不同文档类型与场景',
  '15 种专用分块器：论文/法律/书籍/简历等深度优化',
  '混合检索：文本 5% + 向量 95% 融合，35+ Embedding + 18+ Reranker',
  'GraphRAG 支持：实体/关系/社区三级知识图谱检索',
  '广泛模型生态：30+ LLM，35+ Embedding，18+ Rerank'
])

// 主要不足
const weaknesses = ref([
  '无文档级去重：仅 chunk 级 xxhash，缺乏全局去重能力',
  '无样板/噪声检测：缺少模板页、水印、页眉页脚等噪声识别',
  '分块非语义级：基于 token 数切分，未考虑语义边界',
  '检索权重静态：fusion weights 硬编码，缺乏自适应调优',
  '模型切换成本高：更换 Embedding 模型需重建全量索引',
  '部分功能依赖外部 API：OCR、LLM 调用等依赖外部服务可用性'
])

// ECharts 雷达图
const chartRef = ref(null)
let chartInstance = null

onMounted(() => {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption({
    tooltip: {
      trigger: 'item'
    },
    radar: {
      indicator: [
        { name: '知识库管理', max: 5 },
        { name: '文档上传', max: 5 },
        { name: '文档解析', max: 5 },
        { name: '数据清洗', max: 5 },
        { name: '文本分块', max: 5 },
        { name: '向量化', max: 5 },
        { name: '检索', max: 5 }
      ],
      shape: 'polygon',
      splitNumber: 5,
      axisName: {
        color: '#e2e8f0',
        fontSize: 13
      },
      splitLine: {
        lineStyle: { color: 'rgba(148, 163, 184, 0.15)' }
      },
      splitArea: {
        areaStyle: { color: ['rgba(16, 185, 129, 0.02)', 'rgba(16, 185, 129, 0.05)'] }
      },
      axisLine: {
        lineStyle: { color: 'rgba(148, 163, 184, 0.2)' }
      }
    },
    series: [{
      type: 'radar',
      data: [{
        value: [4, 4, 5, 3, 5, 5, 4],
        name: 'RAGFlow 能力评分',
        areaStyle: {
          color: 'rgba(16, 185, 129, 0.25)'
        },
        lineStyle: {
          color: '#10b981',
          width: 2
        },
        itemStyle: {
          color: '#10b981'
        },
        symbol: 'circle',
        symbolSize: 6
      }]
    }]
  })
  // 响应窗口变化
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})

function handleResize() {
  chartInstance?.resize()
}
</script>
