<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§7 向量化能力</h2>
      <p>pgvector向量存储、14家嵌入模型提供商、Celery向量化管道</p>
    </div>

    <!-- 7.1 向量存储架构 -->
    <div class="card">
      <div class="card-title"><span class="icon">🗄️</span> 7.1 向量存储架构</div>
      <div class="highlight-block">
        MaxKB <strong>唯一使用 pgvector</strong>（PostgreSQL向量扩展）作为向量数据库，采用<strong>双存储设计</strong>同时维护向量索引和全文检索索引。
      </div>
      <div class="code-block">
        <pre><code># apps/common/config/embedding_config.py
class VectorStore:
    instance_map = {'pg_vector': PGVector}  # 仅pgvector

    @staticmethod
    def get_embedding_vector():
        from django.conf import settings
        vector_name = CONFIG.get("VECTOR_STORE_NAME", 'pg_vector')
        return VectorStore.instance_map.get(vector_name, PGVector)()</code></pre>
      </div>
      <div class="two-col" style="margin-top:12px;">
        <div>
          <div class="card-title" style="font-size:14px;">双存储字段设计</div>
          <div class="code-block">
            <pre><code># Embedding模型同时存储两种索引
class Embedding:
    embedding = VectorField()          # pgvector向量列
    search_vector = SearchVectorField() # PostgreSQL全文检索tsvector列</code></pre>
          </div>
        </div>
        <div>
          <div class="card-title" style="font-size:14px;">源码信息</div>
          <table class="data-table">
            <tbody>
              <tr><td><strong>向量存储实现</strong></td><td><code>apps/knowledge/vector/pg_vector.py</code></td></tr>
              <tr><td><strong>代码行数</strong></td><td>244行</td></tr>
              <tr><td><strong>嵌入配置</strong></td><td><code>apps/common/config/embedding_config.py</code></td></tr>
              <tr><td><strong>存储引擎</strong></td><td>pgvector (PostgreSQL扩展)</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 7.2 嵌入模型提供商 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔌</span> 7.2 嵌入模型提供商（14家）</div>
      <div class="highlight-block">
        MaxKB 支持 <strong>14家</strong> 嵌入模型提供商，覆盖云端API、本地部署和开源推理引擎。每个提供商实现统一接口，位于 <code>apps/models_provider/impl/{provider}/model/embedding.py</code>。
      </div>
      <table class="data-table">
        <thead>
          <tr><th>提供商</th><th>实现类</th><th>SDK / 协议</th><th>特点</th></tr>
        </thead>
        <tbody>
          <tr v-for="p in providers" :key="p.name">
            <td><strong>{{ p.name }}</strong></td>
            <td><code>{{ p.cls }}</code></td>
            <td>{{ p.sdk }}</td>
            <td>{{ p.feature }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 7.3 向量化任务管道 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚙️</span> 7.3 向量化任务管道（Celery）</div>
      <div class="highlight-block">
        向量化任务通过 <strong>Celery</strong> 异步执行，支持单文档嵌入和全知识库重嵌入两种模式。
      </div>
      <div class="two-col" style="margin-top:12px;">
        <div>
          <div class="card-title" style="font-size:14px;">核心任务链</div>
          <div class="code-block">
            <pre><code># apps/knowledge/task/embedding.py 核心任务链

@shared_task(queue='embedding')
def embedding_by_document(document_id):
    """单个文档嵌入 (QueueOnce去重)"""
    # 1. 获取段落列表
    # 2. 批量嵌入 → pgvector
    # 3. 生成相关问题 (可选)

@shared_task(queue='embedding')
def embedding_by_knowledge(knowledge_id):
    """整个知识库重新嵌入"""
    # 1. 删除所有现有向量
    # 2. 重新嵌入所有段落和问题</code></pre>
          </div>
          <div class="highlight-block" style="margin-top:8px;">
            <strong>📂 任务:</strong> <code>apps/knowledge/task/embedding.py</code> (258行)<br>
            <strong>📂 事件:</strong> <code>apps/common/event/listener_manage.py</code>
          </div>
        </div>
        <div>
          <div class="card-title" style="font-size:14px;">优化措施</div>
          <table class="data-table">
            <thead>
              <tr><th>优化</th><th>实现</th><th>说明</th></tr>
            </thead>
            <tbody>
              <tr v-for="o in optimizations" :key="o.name">
                <td><strong>{{ o.name }}</strong></td>
                <td><code>{{ o.impl }}</code></td>
                <td>{{ o.desc }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 嵌入模型提供商数据
const providers = ref([
  { name: 'OpenAI', cls: 'OpenAIEmbeddingModel', sdk: 'openai SDK', feature: '通用性强' },
  { name: 'Azure OpenAI', cls: 'AzureOpenAIEmbeddingModel', sdk: 'langchain_openai', feature: '企业级' },
  { name: 'Ollama', cls: 'OllamaEmbedding', sdk: 'langchain_ollama', feature: '本地部署' },
  { name: 'Gemini', cls: 'GeminiEmbeddingModel', sdk: 'langchain_google_genai', feature: 'Google生态' },
  { name: '百度千帆', cls: 'QianfanEmbeddings', sdk: 'qianfan SDK', feature: '中文优化' },
  { name: '阿里百炼', cls: 'AliyunBaiLianEmbedding', sdk: 'dashscope', feature: '多模态嵌入' },
  { name: 'AWS Bedrock', cls: 'BedrockEmbeddingModel', sdk: 'langchain_aws', feature: 'AWS生态' },
  { name: '火山引擎(豆包)', cls: 'VolcanicEngineEmbeddingModel', sdk: 'volcengine SDK', feature: '视觉嵌入' },
  { name: '腾讯混元', cls: 'TencentEmbeddingModel', sdk: 'tencentcloud SDK', feature: '腾讯生态' },
  { name: 'SiliconCloud', cls: 'SiliconCloudEmbeddingModel', sdk: 'HTTP', feature: '开源模型' },
  { name: 'Xinference', cls: 'XinferenceEmbedding', sdk: 'xinference_client', feature: '本地推理' },
  { name: 'VLLM', cls: 'VllmEmbeddingModel', sdk: 'openai SDK', feature: 'GPU推理' },
  { name: 'Regolo', cls: 'RegoloEmbeddingModel', sdk: 'langchain_openai', feature: 'OpenAI兼容' },
  { name: 'XF', cls: 'XF model provider', sdk: '-', feature: 'Xinference变体' },
])

// 向量化优化措施数据
const optimizations = ref([
  { name: '任务去重', impl: 'QueueOnce by document_id', desc: '防止重复嵌入' },
  { name: '分布式锁', impl: 'RedisLock', desc: '防止并发写入' },
  { name: '批量操作', impl: 'bulk_create()', desc: '批量插入向量' },
  { name: '模型缓存', impl: 'ModelManage (8h TTL)', desc: '避免重复初始化' },
  { name: 'HNSW索引', impl: 'create_knowledge_index()', desc: '高性能近似检索' },
])
</script>
