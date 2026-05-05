<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§1 项目架构概览</h2>
      <p>MaxKB v2.0.0 系统架构全解析 — 核心指标、Django 模块矩阵与数据模型关系</p>
    </div>

    <!-- 核心指标 -->
    <div class="metrics-grid">
      <div class="metric-card" v-for="m in metrics" :key="m.label">
        <div class="metric-value">{{ m.value }}</div>
        <div class="metric-label">{{ m.label }}</div>
      </div>
    </div>

    <!-- 架构图（ECharts） -->
    <div class="card">
      <div class="card-title"><span class="icon">◈</span>整体架构图</div>
      <div id="chart-arch" class="chart-container tall"></div>
    </div>

    <!-- Django 应用模块一览 -->
    <div class="card">
      <div class="card-title"><span class="icon">📦</span> Django 应用模块一览</div>
      <table class="data-table">
        <thead>
          <tr><th>模块</th><th>路径</th><th>职责</th><th>核心功能</th></tr>
        </thead>
        <tbody>
          <tr v-for="m in djangoModules" :key="m.name">
            <td><strong>{{ m.name }}</strong></td>
            <td><code>{{ m.path }}</code></td>
            <td>{{ m.role }}</td>
            <td>{{ m.features }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 数据模型关系图 -->
    <div class="card">
      <div class="card-title"><span class="icon">🗂</span> 数据模型关系图</div>
      <div class="code-block">
        <span class="lang-tag">models</span>
        <pre>
KnowledgeFolder (MPTT 树形目录)
  └── Knowledge (知识库)
        ├── type: BASE(0) | WEB(1) | LARK(2) | YUQUE(3) | WORKFLOW(4)
        ├── embedding_model → FK(Model)
        ├── file_size_limit (默认100MB)
        ├── file_count_limit (默认50个)
        │
        ├── Document (文档)
        │     ├── char_length, status, is_active
        │     ├── hit_handling_method: optimization | directly_return
        │     ├── directly_return_similarity (默认0.9)
        │     │
        │     ├── Paragraph (段落/分块)
        │     │     ├── content (max_length=102400)
        │     │     ├── title (max_length=256)
        │     │     ├── chunks: ArrayField (子分块)
        │     │     ├── position (排序)
        │     │     └── hit_num (命中次数)
        │     │
        │     └── DocumentTag (M2M) → Tag
        │
        ├── Problem (问题)
        │     └── ProblemParagraphMapping → M2M(Paragraph)
        │
        ├── Embedding (向量存储)
        │     ├── embedding: VectorField (pgvector)
        │     ├── search_vector: SearchVectorField (全文检索)
        │     ├── source_type: PROBLEM(0) | PARAGRAPH(1)
        │     └── is_active
        │
        └── KnowledgeWorkflow (1:1, 工作流知识库)</pre>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>源码路径：</strong><code>apps/knowledge/models/knowledge.py</code>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

// 核心指标卡片
const metrics = ref([
  { value: '9', label: 'Django 模块' },
  { value: '27+', label: '模型提供商' },
  { value: 'pgvector', label: '向量存储' },
  { value: 'Celery 5.5', label: '异步任务' },
  { value: 'Python 3.11', label: '运行时' },
  { value: '95', label: 'API URL' }
])

// Django 应用模块
const djangoModules = ref([
  { name: 'application', path: 'apps/application/', role: '应用/Agent 管理', features: '工作流引擎(37节点)、对话管道、版本管理' },
  { name: 'chat', path: 'apps/chat/', role: '公开对话 API', features: '嵌入式组件、OpenAI兼容接口、MCP协议' },
  { name: 'knowledge', path: 'apps/knowledge/', role: '知识库管理', features: '文档CRUD、向量存储、嵌入任务、Web同步' },
  { name: 'models_provider', path: 'apps/models_provider/', role: '模型抽象层', features: '27+ LLM/嵌入/重排模型提供商' },
  { name: 'tools', path: 'apps/tools/', role: '工具系统', features: '工具市场、自定义工具、MCP服务器' },
  { name: 'trigger', path: 'apps/trigger/', role: '自动化触发', features: 'Webhook触发、定时触发、任务执行' },
  { name: 'oss', path: 'apps/oss/', role: '对象存储', features: '文件上传、URL获取、图片检索' },
  { name: 'users', path: 'apps/users/', role: '用户管理', features: '认证、工作空间权限、邮箱验证' },
  { name: 'system_manage', path: 'apps/system_manage/', role: '系统设置', features: '邮箱配置、资源权限、RBAC' }
])

// 架构图 ECharts
onMounted(() => {
  const el = document.getElementById('chart-arch')
  if (!el) return
  const chart = echarts.init(el)

  chart.setOption({
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove',
      backgroundColor: 'rgba(17,24,39,0.95)',
      borderColor: 'rgba(51,112,255,0.3)',
      textStyle: { color: '#e2e8f0', fontSize: 13 }
    },
    series: [
      {
        type: 'tree',
        data: [
          {
            name: 'MaxKB v2.0.0',
            children: [
              {
                name: '前端层',
                children: [
                  { name: 'Vue 3' },
                  { name: 'Element Plus' },
                  { name: 'Logic Flow' },
                  { name: 'Pinia Store' },
                  { name: 'Vite 6 构建工具' }
                ]
              },
              {
                name: 'Django REST',
                children: [
                  { name: 'Application\n工作流引擎' },
                  { name: 'Chat\n对话API' },
                  { name: 'Knowledge\n知识管理' },
                  { name: 'Models\n模型提供者' },
                  { name: 'Tools\n工具系统' },
                  { name: 'Trigger\n触发器' }
                ]
              },
              {
                name: 'Common 基础层',
                children: [
                  { name: '认证' },
                  { name: '缓存' },
                  { name: '事件' },
                  { name: '中间件' },
                  { name: '异常处理' }
                ]
              },
              {
                name: '数据层',
                children: [
                  { name: 'PostgreSQL 17\n(pgvector)' },
                  { name: 'Redis\n缓存/Broker' }
                ]
              },
              {
                name: '异步任务',
                children: [
                  { name: '文档嵌入' },
                  { name: '问题生成' },
                  { name: 'Web同步' },
                  { name: '触发器执行' }
                ]
              }
            ]
          }
        ],
        top: '5%',
        left: '12%',
        bottom: '5%',
        right: '12%',
        symbolSize: 12,
        symbol: 'roundRect',
        orient: 'TB',
        label: {
          position: 'top',
          verticalAlign: 'middle',
          align: 'center',
          fontSize: 12,
          color: '#e2e8f0',
          distance: 8,
          formatter: (params) => params.name.replace(/\n/g, ' ')
        },
        leaves: {
          label: {
            position: 'bottom',
            align: 'center',
            fontSize: 11,
            color: '#94a3b8'
          }
        },
        lineStyle: {
          color: 'rgba(51,112,255,0.4)',
          width: 1.5,
          curveness: 0.5
        },
        itemStyle: {
          color: '#3370ff',
          borderColor: 'rgba(51,112,255,0.6)',
          borderWidth: 1
        },
        emphasis: {
          focus: 'descendant',
          itemStyle: { color: '#7f3bf5' }
        },
        expandAndCollapse: true,
        animationDuration: 550,
        animationDurationUpdate: 750
      }
    ]
  })

  window.addEventListener('resize', () => chart.resize())
})
</script>
