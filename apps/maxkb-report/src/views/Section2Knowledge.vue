<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§2 知识管理能力</h2>
      <p>MaxKB 知识库类型体系、配置选项、核心 API 与知识管理流程全解析</p>
    </div>

    <!-- 知识库类型支持表 + 饼图 -->
    <div class="two-col">
      <div class="card">
        <div class="card-title"><span class="icon">📚</span> 知识库类型支持</div>
        <table class="data-table">
          <thead>
            <tr><th>类型</th><th>枚举值</th><th>说明</th><th>数据来源</th></tr>
          </thead>
          <tbody>
            <tr v-for="t in kbTypes" :key="t.name">
              <td><strong>{{ t.name }}</strong></td>
              <td><code>{{ t.enum }}</code></td>
              <td>{{ t.desc }}</td>
              <td>{{ t.source }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card">
        <div class="card-title"><span class="icon">📊</span> 知识库类型分布</div>
        <div id="kb-type-chart" class="chart-container"></div>
      </div>
    </div>

    <!-- 知识库配置选项表 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚙️</span> 知识库配置选项</div>
      <table class="data-table">
        <thead>
          <tr><th>配置项</th><th>字段</th><th>默认值</th><th>说明</th></tr>
        </thead>
        <tbody>
          <tr v-for="c in configOptions" :key="c.item">
            <td><strong>{{ c.item }}</strong></td>
            <td><code>{{ c.field }}</code></td>
            <td><code>{{ c.default }}</code></td>
            <td>{{ c.desc }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 核心 API 端点 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔗</span> 核心 API 端点</div>
      <div class="code-block" data-language="python">
        <span class="lang-tag">Python</span>
        <pre><span class="code-comment"># apps/knowledge/urls.py（95个URL模式）</span>
<span class="code-string">'/workspace/&lt;id&gt;/knowledge'</span>              <span class="code-comment"># GET 列表</span>
<span class="code-string">'/workspace/&lt;id&gt;/knowledge/base'</span>         <span class="code-comment"># POST 创建通用知识库</span>
<span class="code-string">'/workspace/&lt;id&gt;/knowledge/web'</span>          <span class="code-comment"># POST 创建Web知识库</span>
<span class="code-string">'/workspace/&lt;id&gt;/knowledge/workflow'</span>     <span class="code-comment"># POST 创建工作流知识库</span>
<span class="code-string">'/workspace/&lt;id&gt;/knowledge/&lt;id&gt;'</span>         <span class="code-comment"># GET/PUT/DELETE 操作</span>
<span class="code-string">'/workspace/&lt;id&gt;/knowledge/&lt;id&gt;/embedding'</span>  <span class="code-comment"># PUT 重新向量化</span>
<span class="code-string">'/workspace/&lt;id&gt;/knowledge/&lt;id&gt;/hit_test'</span>   <span class="code-comment"># POST 命中测试</span>
<span class="code-string">'/workspace/&lt;id&gt;/knowledge/batch_delete'</span>    <span class="code-comment"># PUT 批量删除</span>
<span class="code-string">'/workspace/&lt;id&gt;/knowledge/batch_move'</span>      <span class="code-comment"># PUT 批量移动</span>
<span class="code-string">'/workspace/&lt;id&gt;/knowledge/&lt;id&gt;/export*'</span>    <span class="code-comment"># GET 导出(excel/zip/完整包)</span></pre>
      </div>
    </div>

    <!-- 知识管理流程图 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔄</span> 知识管理流程</div>
      <div class="flow-diagram">
        <!-- 第一行：创建 → 配置 → 上传/Web源 -->
        <div class="flow-steps">
          <div class="flow-step primary">创建知识库<br><small>POST /knowledge/base</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">配置嵌入模型<br><small>embedding_model_id</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">上传文档<br><small>文件上传</small></div>
        </div>
        <div style="margin:8px 0;color:var(--text-muted);font-size:0.8rem;">或</div>
        <div class="flow-steps">
          <div class="flow-step primary">创建Web知识库<br><small>POST /knowledge/web</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">配置嵌入模型<br><small>embedding_model_id</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">Web爬取(Fork)<br><small>URL + CSS选择器</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">HTML→Markdown<br><small>格式转换</small></div>
        </div>
        <div style="margin:12px 0;"><div class="flow-arrow" style="font-size:1.6rem;">↓</div></div>
        <!-- 第二行：解析 → 分块 → 异步任务 -->
        <div class="flow-steps">
          <div class="flow-step">文档解析<br><small>文本提取</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">文本分块<br><small>段落拆分</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step primary">触发Celery异步任务<br><small>分布式处理</small></div>
        </div>
        <div style="margin:12px 0;"><div class="flow-arrow" style="font-size:1.6rem;">↓</div></div>
        <!-- 第三行：向量化 + 生成问题 -->
        <div class="flow-steps">
          <div class="flow-step primary">嵌入向量化<br><small>pgvector存储</small></div>
          <div class="flow-arrow">+</div>
          <div class="flow-step primary">生成相关问题<br><small>Problem + Mapping</small></div>
        </div>
      </div>
      <div class="source-ref-list" style="margin-top:16px;">
        <div class="ref-title">📂 源码参考</div>
        <div class="source-ref-item">
          <span class="ref-file">apps/knowledge/serializers/knowledge.py</span>
          <span class="ref-desc">— 序列化器（1313行）</span>
        </div>
        <div class="source-ref-item">
          <span class="ref-file">apps/knowledge/views/knowledge.py</span>
          <span class="ref-desc">— 视图层</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

// 知识库类型支持
const kbTypes = ref([
  { name: '通用知识库', enum: 'BASE(0)', desc: '手动上传文档', source: '文件上传' },
  { name: 'Web站点知识库', enum: 'WEB(1)', desc: '自动爬取网站', source: 'URL + CSS选择器' },
  { name: '飞书知识库', enum: 'LARK(2)', desc: '飞书文档集成', source: '飞书API' },
  { name: '语雀知识库', enum: 'YUQUE(3)', desc: '语雀文档集成', source: '语雀API' },
  { name: '工作流知识库', enum: 'WORKFLOW(4)', desc: '工作流处理管道', source: '自定义工作流' }
])

// 知识库配置选项
const configOptions = ref([
  { item: '嵌入模型', field: 'embedding_model_id', default: '-', desc: '每个知识库可独立配置' },
  { item: '文件大小限制', field: 'file_size_limit', default: '100 MB', desc: '单文件上传限制' },
  { item: '文件数量限制', field: 'file_count_limit', default: '50', desc: '单次上传限制' },
  { item: '可见范围', field: 'scope', default: 'SHARED', desc: 'WORKSPACE / SHARED' },
  { item: '文件夹归属', field: 'folder', default: '-', desc: 'MPTT树形目录组织' },
  { item: '元数据', field: 'meta (JSON)', default: '{}', desc: '扩展元数据(Web URL/选择器等)' }
])

// ECharts 饼图
let chartInstance = null

onMounted(() => {
  const el = document.getElementById('kb-type-chart')
  if (!el) return
  chartInstance = echarts.init(el)
  chartInstance.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: { color: '#e2e8f0', fontSize: 12 }
    },
    series: [{
      type: 'pie',
      radius: ['35%', '65%'],
      center: ['40%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 6,
        borderColor: '#1a2236',
        borderWidth: 2
      },
      label: {
        show: true,
        color: '#e2e8f0',
        fontSize: 11,
        formatter: '{b}\n{d}%'
      },
      labelLine: {
        lineStyle: { color: 'rgba(148, 163, 184, 0.4)' }
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      },
      data: [
        { value: 40, name: '通用(BASE)', itemStyle: { color: '#3370ff' } },
        { value: 25, name: 'Web站点(WEB)', itemStyle: { color: '#14b8a6' } },
        { value: 15, name: '飞书(LARK)', itemStyle: { color: '#f59e0b' } },
        { value: 10, name: '语雀(YUQUE)', itemStyle: { color: '#7f3bf5' } },
        { value: 10, name: '工作流(WORKFLOW)', itemStyle: { color: '#ef4444' } }
      ]
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
