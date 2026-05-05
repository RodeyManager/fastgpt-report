<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§2 知识库管理</h2>
      <p>RAGFlow 知识库数据模型、权限体系与分块策略配置详解</p>
    </div>

    <!-- 知识库数据模型 -->
    <div class="card">
      <div class="card-title"><span class="icon">◈</span>知识库数据模型（Knowledgebase）</div>
      <table class="data-table">
        <thead>
          <tr><th>字段</th><th>类型</th><th>默认值</th><th>说明</th></tr>
        </thead>
        <tbody>
          <tr v-for="f in dataModelFields" :key="f.field">
            <td><code>{{ f.field }}</code></td>
            <td>{{ f.type }}</td>
            <td><code>{{ f.default }}</code></td>
            <td>{{ f.desc }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 权限模型 -->
    <div class="card">
      <div class="card-title"><span class="icon">◈</span>权限模型数据流</div>
      <div class="flow-diagram">
        <div class="flow-steps">
          <div class="flow-step primary">Tenant<br><small>租户</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">UserTenant<br><small>租户-用户关联</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">User<br><small>用户</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step primary">Knowledgebase<br><small>permission: me | team</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">Document<br><small>文档</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">Chunk<br><small>ES / Infinity</small></div>
        </div>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>权限传递链：</strong>租户（Tenant）通过 UserTenant 关联用户，用户按知识库的 <code>permission</code> 字段决定访问范围。<code>me</code> 表示仅创建者可见，<code>team</code> 表示团队内所有成员可访问。文档的删除权限仅限 <code>created_by</code> 用户。
      </div>

      <!-- 权限级别表 -->
      <table class="data-table" style="margin-top:16px;">
        <thead>
          <tr><th>权限级别</th><th>值</th><th>可见范围</th><th>删除权限</th></tr>
        </thead>
        <tbody>
          <tr v-for="p in permissions" :key="p.level">
            <td><strong>{{ p.level }}</strong></td>
            <td><code>{{ p.value }}</code></td>
            <td>{{ p.scope }}</td>
            <td>{{ p.delete }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分块策略配置 -->
    <div class="card">
      <div class="card-title"><span class="icon">◈</span>分块策略配置（parser_config）</div>
      <table class="data-table">
        <thead>
          <tr><th>策略 ID</th><th>适用场景</th><th>默认块大小</th><th>说明</th></tr>
        </thead>
        <tbody>
          <tr v-for="s in chunkStrategies" :key="s.id">
            <td><code>{{ s.id }}</code></td>
            <td>{{ s.scene }}</td>
            <td><code>{{ s.chunkSize }}</code></td>
            <td>{{ s.desc }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 优劣势分析 -->
    <div class="pros-cons-grid">
      <div class="pros-card">
        <h4>✓ 优势</h4>
        <ul>
          <li v-for="p in pros" :key="p"><strong>{{ p.split('：')[0] }}：</strong>{{ p.split('：').slice(1).join('：') }}</li>
        </ul>
      </div>
      <div class="cons-card">
        <h4>✗ 不足</h4>
        <ul>
          <li v-for="c in cons" :key="c"><strong>{{ c.split('：')[0] }}：</strong>{{ c.split('：').slice(1).join('：') }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 知识库数据模型字段
const dataModelFields = ref([
  { field: 'id', type: 'CharField(32)', default: 'PK', desc: '主键，唯一标识知识库' },
  { field: 'tenant_id', type: 'CharField(32)', default: '—', desc: '所属租户 ID，外键关联 Tenant' },
  { field: 'name', type: 'CharField(128)', default: "''", desc: '知识库名称' },
  { field: 'language', type: 'CharField(32)', default: "'English'", desc: '语言设置：English / Chinese' },
  { field: 'embd_id', type: 'CharField(128)', default: '—', desc: '嵌入模型 ID，决定向量化方式' },
  { field: 'parser_id', type: 'CharField(32)', default: "'naive'", desc: '默认分块策略 ID' },
  { field: 'parser_config', type: 'JSONField', default: '{}', desc: '分块策略详细配置（块大小、重叠等）' },
  { field: 'permission', type: 'CharField(32)', default: "'me'", desc: '权限模型：me（私有）/ team（团队）' },
  { field: 'similarity_threshold', type: 'FloatField', default: '0.2', desc: '相似度阈值，低于此值的结果被过滤' },
  { field: 'vector_similarity_weight', type: 'FloatField', default: '0.3', desc: '向量相似度在混合检索中的权重' },
  { field: 'doc_num / chunk_num / token_num', type: 'IntegerField', default: '0', desc: '文档数 / 分块数 / Token 数统计' },
  { field: 'graphrag_task_id', type: 'CharField(128)', default: "''", desc: 'GraphRAG 任务 ID（知识图谱增强）' },
  { field: 'raptor_task_id', type: 'CharField(128)', default: "''", desc: 'RAPTOR 任务 ID（递归摘要聚类）' }
])

// 权限级别
const permissions = ref([
  { level: '私有', value: 'me', scope: '仅创建者可见', delete: '仅 created_by' },
  { level: '团队', value: 'team', scope: '租户内所有成员可访问', delete: '仅 created_by' }
])

// 分块策略配置
const chunkStrategies = ref([
  { id: 'naive', scene: '通用文本', chunkSize: '512', desc: '默认策略，按固定 token 数分块，适合大多数场景' },
  { id: 'knowledge_graph', scene: '知识图谱', chunkSize: '8192', desc: '提取实体与关系构建知识图谱，需要 LLM 配合' },
  { id: 'qa', scene: 'QA 问答对', chunkSize: '—', desc: '将文档拆分为问答对，适合 FAQ 场景' },
  { id: 'paper', scene: '学术论文', chunkSize: '—', desc: '针对论文结构（摘要/章节/参考文献）解析' },
  { id: 'book', scene: '书籍', chunkSize: '—', desc: '按章节/段落层级解析长文档' },
  { id: 'laws', scene: '法律法规', chunkSize: '—', desc: '按条款/条文结构解析法律文本' },
  { id: 'presentation', scene: '演示文稿', chunkSize: '—', desc: '按幻灯片逐页解析 PPT 内容' },
  { id: 'table/resume/one/email/picture', scene: '专项格式', chunkSize: '—', desc: '表格、简历、单块、邮件、图片等特殊解析策略' }
])

// 优势
const pros = ref([
  '灵活权限模型：me/team 双模型兼顾私有与协作场景',
  '独立 Embedding 配置：每个知识库可单独选择嵌入模型，避免全局耦合',
  '相似度阈值可调：similarity_threshold 与 vector_similarity_weight 精细控制检索质量',
  'GraphRAG / RAPTOR / Mindmap：支持知识图谱增强、递归摘要聚类与思维导图三种高级检索模式'
])

// 不足
const cons = ref([
  '缺乏细粒度 RBAC：仅 me/team 两级权限，不支持角色级别的读写分离',
  '更换模型需重建索引：embd_id 变更后所有文档需重新解析和向量化',
  '不支持跨知识库检索：每次查询仅限单个知识库，无法跨库联合召回',
  '高级功能依赖 LLM 质量：GraphRAG / QA 模式的效果高度依赖 LLM 抽取能力'
])
</script>
