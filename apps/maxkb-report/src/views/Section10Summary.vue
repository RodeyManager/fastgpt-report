<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§10 优势与不足总结</h2>
      <p>MaxKB RAG 平台各维度能力评分、优势亮点与待改进项全面总结</p>
    </div>

    <!-- 雷达图 + 综合评分 -->
    <div class="two-col">
      <div class="card">
        <div class="card-title"><span class="icon">🎯</span> 技术栈多维评分</div>
        <div id="radar-chart" class="chart-container"></div>
      </div>

      <div class="card">
        <div class="card-title"><span class="icon">⭐</span> 综合评分</div>
        <div class="overall-score">
          <div class="score-number">4.0<span class="score-max"> / 5</span></div>
          <div class="score-stars">⭐⭐⭐⭐</div>
          <div class="score-desc">
            MaxKB 是一个架构简洁、功能完整的开源 RAG 平台。在知识管理、文档解析（尤其 PDF）和中文支持方面表现出色。主要短板在混合检索算法和缺少 OCR 能力。整体适合中小企业快速部署 RAG 知识库系统。
          </div>
        </div>
        <!-- 评分明细 -->
        <table class="data-table" style="margin-top:16px;">
          <thead>
            <tr><th>维度</th><th>评分</th><th>说明</th></tr>
          </thead>
          <tbody>
            <tr v-for="s in scores" :key="s.dim">
              <td><strong>{{ s.dim }}</strong></td>
              <td>{{ '⭐'.repeat(s.star) }}</td>
              <td>{{ s.desc }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 优势与不足对比 -->
    <div class="pros-cons-grid">
      <!-- 优势 -->
      <div class="card">
        <div class="card-title"><span class="icon">✅</span> 优势亮点</div>
        <div class="feature-list">
          <div v-for="p in pros" :key="p.title" class="feature-item pro">
            <div class="feature-header">
              <span class="feature-badge pro-badge">优势</span>
              <strong>{{ p.title }}</strong>
            </div>
            <p>{{ p.desc }}</p>
          </div>
        </div>
      </div>

      <!-- 不足 -->
      <div class="card">
        <div class="card-title"><span class="icon">⚠️</span> 待改进项</div>
        <div class="feature-list">
          <div v-for="c in cons" :key="c.title" class="feature-item con">
            <div class="feature-header">
              <span class="feature-badge con-badge">不足</span>
              <strong>{{ c.title }}</strong>
            </div>
            <p>{{ c.desc }}</p>
            <div class="feature-suggestion">💡 {{ c.suggestion }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

// 优势列表
const pros = ref([
  { title: '架构简洁', desc: '单一技术栈(Django+PG+Redis)，部署简单，运维成本低' },
  { title: 'PDF 三策略解析', desc: 'TOC→链接→字体分析的递降策略，覆盖多种 PDF 结构' },
  { title: '嵌入模型丰富', desc: '14 个提供商，从云端 API 到本地部署全覆盖' },
  { title: '中文支持优秀', desc: 'jieba 分词 + 中文标点分割 + 中文全文检索' },
  { title: '代码块保护', desc: 'mask_code_blocks 防止代码内容被误识别为标题' },
  { title: '工作流引擎', desc: '37 种节点类型，灵活编排 RAG 管道' },
  { title: '文件去重', desc: 'SHA256 + Large Object 共享存储' },
  { title: '异步处理', desc: 'Celery + Redis 分布式任务队列' }
])

// 不足列表
const cons = ref([
  { title: '无 OCR 能力', desc: '图片内文字无法提取', suggestion: '集成 PaddleOCR / Tesseract' },
  { title: '单一向量库', desc: '仅支持 pgvector', suggestion: '抽象层已有，可扩展 Milvus / ES' },
  { title: '混合检索简单', desc: '加性融合，非归一化', suggestion: '引入 RRF (Reciprocal Rank Fusion)' },
  { title: '重排序仅工作流', desc: '默认对话管道无重排序', suggestion: '增加默认管道重排序选项' },
  { title: '表格解析有限', desc: 'PDF 表格无法提取', suggestion: '集成 Camelot / Tabula' },
  { title: '硬编码阈值', desc: '0.65 相似度固定', suggestion: '支持用户自定义' },
  { title: '分块丢弃', desc: '>4096 字符段落静默丢弃', suggestion: '改为强制分割或警告' },
  { title: 'jieba 性能', desc: '全模式分词较慢', suggestion: '考虑 jieba-fast / fastHan' }
])

// 维度评分数据
const scores = ref([
  { dim: '知识管理', star: 4, value: 8, desc: '多类型支持、文件夹组织、权限管理完善' },
  { dim: '文档上传', star: 4, value: 8, desc: '4 通道、9 种格式、SHA256 去重' },
  { dim: '文档解析', star: 4, value: 8, desc: 'PDF 三策略突出，DOCX/HTML 良好' },
  { dim: '数据清洗', star: 3, value: 6, desc: '基础清洗完善，但缺少 OCR 和高级清洗' },
  { dim: '文本分块', star: 4, value: 8, desc: '三策略灵活、中文优化、可配置模式' },
  { dim: '向量化', star: 4, value: 8, desc: '14 提供商、异步处理、缓存优化' },
  { dim: '检索能力', star: 3, value: 6, desc: '三模式检索，混合检索和重排序有提升空间' }
])

// ECharts 雷达图
let chartInstance = null

onMounted(() => {
  const el = document.getElementById('radar-chart')
  if (!el) return
  chartInstance = echarts.init(el)
  chartInstance.setOption({
    tooltip: {
      trigger: 'item'
    },
    radar: {
      indicator: [
        { name: '知识管理', max: 10 },
        { name: '文档上传', max: 10 },
        { name: '文档解析', max: 10 },
        { name: '数据清洗', max: 10 },
        { name: '文本分块', max: 10 },
        { name: '向量化', max: 10 },
        { name: '检索能力', max: 10 }
      ],
      shape: 'polygon',
      splitNumber: 5,
      axisName: {
        color: '#e2e8f0',
        fontSize: 12
      },
      splitLine: {
        lineStyle: { color: 'rgba(148, 163, 184, 0.15)' }
      },
      splitArea: {
        areaStyle: { color: ['rgba(51, 112, 255, 0.02)', 'rgba(51, 112, 255, 0.05)'] }
      },
      axisLine: {
        lineStyle: { color: 'rgba(148, 163, 184, 0.2)' }
      }
    },
    series: [{
      type: 'radar',
      data: [{
        value: [8, 8, 8, 6, 8, 8, 6],
        name: 'MaxKB 评分',
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          color: '#3370ff',
          width: 2
        },
        areaStyle: {
          color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
            { offset: 0, color: 'rgba(51, 112, 255, 0.35)' },
            { offset: 1, color: 'rgba(51, 112, 255, 0.05)' }
          ])
        },
        itemStyle: {
          color: '#3370ff'
        }
      }]
    }]
  })
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
