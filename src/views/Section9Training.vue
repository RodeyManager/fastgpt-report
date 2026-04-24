<template>
  <section class="section">
    <div class="section-header">
      <h2>训练模式与AI模型</h2>
      <p>AI驱动的知识处理管道</p>
    </div>

    <!-- 训练模式 -->
    <div class="card">
      <h3>训练模式</h3>
      <table class="data-table">
        <thead><tr><th>模式</th><th>枚举值</th><th>AI模型</th><th>描述</th></tr></thead>
        <tbody>
          <tr><td>解析</td><td><code>parse</code></td><td><span class="tag agent">agentModel</span></td><td>读取源文件,提取文本,分块</td></tr>
          <tr><td>分块</td><td><code>chunk</code></td><td><span class="tag vector">vectorModel</span></td><td>直接对文本块向量化</td></tr>
          <tr><td>问答</td><td><code>qa</code></td><td><span class="tag agent">agentModel</span></td><td>LLM生成问答对(每段最多50对)</td></tr>
          <tr><td>自动</td><td><code>auto</code></td><td><span class="tag agent">agentModel</span></td><td>AI自动生成自定义索引</td></tr>
          <tr><td>图片</td><td><code>image</code></td><td><span class="tag vlm">vlmModel</span></td><td>VLM描述图片并索引</td></tr>
          <tr><td>图片解析</td><td><code>imageParse</code></td><td><span class="tag vlm">vlmModel</span></td><td>VLM处理完整图片内容</td></tr>
        </tbody>
      </table>
    </div>

    <!-- QA生成流程 -->
    <div class="card">
      <h3>QA生成流程</h3>
      <div class="flow-steps">
        <div class="flow-step">文本块</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step highlight">LLM Prompt<br><small>Prompt_AgentQA</small></div>
        <div class="flow-arrow">→</div>
        <div class="flow-step">流式响应</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step highlight">正则解析<br><small>Q\d+:(.*?)A\d+</small></div>
        <div class="flow-arrow">→</div>
        <div class="flow-step">问答对</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step success">训练队列<br><small>chunk模式</small></div>
      </div>
      <div class="flow-fallback">
        <span class="flow-arrow-down">↓ 解析失败</span>
        <div class="flow-step warn">回退到直接分块</div>
      </div>
    </div>

    <!-- 模型使用图表 -->
    <div class="card">
      <h3>训练模式 × AI模型映射</h3>
      <div id="chart-training-models" style="height:260px"></div>
    </div>

    <!-- AI模型类型 -->
    <div class="card">
      <h3>AI模型类型</h3>
      <table class="data-table">
        <thead><tr><th>类型</th><th>默认模型</th><th>关键特性</th></tr></thead>
        <tbody>
          <tr><td>LLM</td><td><code>gpt-5</code></td><td>maxContext=16000, toolChoice, vision, reasoning</td></tr>
          <tr><td>Embedding</td><td><code>text-embedding-3-small</code></td><td>1536维, batchSize, dbConfig/queryConfig</td></tr>
          <tr><td>Rerank</td><td><code>可配置</code></td><td>maxToken=8000, Jina兼容接口</td></tr>
          <tr><td>TTS</td><td><code>可配置</code></td><td>多种语音选项</td></tr>
          <tr><td>STT</td><td><code>whisper-1</code></td><td>语音转文本</td></tr>
        </tbody>
      </table>
    </div>

    <!-- 插件模型服务 -->
    <div class="card">
      <h3>插件模型服务</h3>
      <ul class="feature-list">
        <li><strong>pdf-mineru</strong> — PDF深度解析</li>
        <li><strong>pdf-marker</strong> — PDF标注提取</li>
        <li><strong>pdf-mistral</strong> — Mistral PDF处理</li>
        <li><strong>ocr-surya</strong> — OCR文字识别</li>
        <li><strong>rerank-bge</strong> — BGE重排序</li>
        <li><strong>stt-sensevoice</strong> — 语音识别</li>
        <li><strong>tts-cosevoice</strong> — 语音合成</li>
      </ul>
    </div>

    <!-- 定时任务 -->
    <div class="card">
      <h3>定时任务</h3>
      <ul class="feature-list">
        <li><strong>训练队列处理</strong> — 每1分钟</li>
        <li><strong>过期数据清理</strong> — 每10分钟</li>
        <li><strong>无效数据检查</strong> — 每1小时</li>
        <li><strong>孤儿向量清理</strong> — 定期执行</li>
      </ul>
    </div>
  </section>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

let chart = null

const modes = [
  { name: '解析(parse)', model: 'agentModel' },
  { name: '分块(chunk)', model: 'vectorModel' },
  { name: '问答(qa)', model: 'agentModel' },
  { name: '自动(auto)', model: 'agentModel' },
  { name: '图片(image)', model: 'vlmModel' },
  { name: '图片解析(imageParse)', model: 'vlmModel' }
]

const modelTypes = ['agentModel', 'vectorModel', 'vlmModel']
const colors = { agentModel: '#6366f1', vectorModel: '#10b981', vlmModel: '#f59e0b' }

onMounted(() => {
  const el = document.getElementById('chart-training-models')
  if (!el) return
  chart = echarts.init(el)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: modelTypes, top: 0, textStyle: { fontSize: 11 } },
    grid: { left: 20, right: 20, bottom: 24, top: 36, containLabel: true },
    xAxis: { type: 'category', data: modes.map(m => m.name), axisLabel: { fontSize: 10, rotate: 15 } },
    yAxis: { type: 'value', max: 1, splitNumber: 1, axisLabel: { show: false } },
    series: modelTypes.map(t => ({
      name: t, type: 'bar', stack: 'total', barWidth: 28,
      data: modes.map(m => m.model === t ? 1 : 0),
      itemStyle: { color: colors[t] },
      emphasis: { focus: 'series' }
    }))
  })
  window.addEventListener('resize', () => chart?.resize())
})

onBeforeUnmount(() => { chart?.dispose(); chart = null })
</script>

<style scoped>
.tag { padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.tag.agent { background: rgba(99,102,241,.15); color: #6366f1; }
.tag.vector { background: rgba(16,185,129,.15); color: #10b981; }
.tag.vlm { background: rgba(245,158,11,.15); color: #f59e0b; }
.flow-steps { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; }
.flow-step {
  padding: 8px 12px; background: var(--bg-tertiary, #f1f5f9); border-radius: 8px;
  font-size: 13px; text-align: center; white-space: nowrap;
}
.flow-step.highlight { background: rgba(99,102,241,.12); border: 1px solid rgba(99,102,241,.3); }
.flow-step.success { background: rgba(16,185,129,.12); border: 1px solid rgba(16,185,129,.3); }
.flow-step.warn { background: rgba(239,68,68,.1); border: 1px solid rgba(239,68,68,.3); color: #dc2626; }
.flow-arrow { color: var(--text-secondary, #94a3b8); font-weight: 700; }
.flow-fallback { margin-top: 10px; display: flex; align-items: center; gap: 8px; }
.flow-arrow-down { color: var(--text-secondary, #94a3b8); font-size: 13px; }
small { opacity: .7; font-size: 11px; }
</style>
