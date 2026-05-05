<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§7 向量化</h2>
      <p>RAGFlow 35+ Embedding 提供商与 4 种向量存储引擎</p>
    </div>

    <!-- 模型抽象 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔧</span> Embedding 模型抽象基类</div>
      <div class="code-block" data-language="python">
        <pre><code>class Base(ABC):
    def encode(self, texts: list) -&gt; tuple[np.ndarray, int]:     # 文档向量化
    def encode_queries(self, text: str) -&gt; tuple[np.ndarray, int]: # 查询向量化</code></pre>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>设计要点：</strong>所有 Embedding 提供商均继承 <code>Base</code> 抽象基类，统一实现 <code>encode()</code>（文档批量向量化）与 <code>encode_queries()</code>（查询向量化）两个接口。返回值为 <code>(向量矩阵, Token 用量)</code> 元组，便于上层统一调用与成本统计。
      </div>
    </div>

    <!-- 提供商分类表 -->
    <div class="card">
      <div class="card-title"><span class="icon">🌐</span> 35+ Embedding 提供商分类</div>
      <table class="data-table">
        <thead>
          <tr><th>分类</th><th>提供商</th></tr>
        </thead>
        <tbody>
          <tr v-for="cat in providerCategories" :key="cat.category">
            <td><strong>{{ cat.category }}</strong></td>
            <td>{{ cat.providers }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 向量引擎表 -->
    <div class="card">
      <div class="card-title"><span class="icon">🗄️</span> 4 种向量存储引擎</div>
      <table class="data-table">
        <thead>
          <tr><th>引擎</th><th>检索能力</th><th>说明</th></tr>
        </thead>
        <tbody>
          <tr v-for="e in vectorEngines" :key="e.name">
            <td><strong>{{ e.name }}</strong></td>
            <td><code>{{ e.capabilities }}</code></td>
            <td>{{ e.note }}</td>
          </tr>
        </tbody>
      </table>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>向量列命名：</strong>所有引擎统一使用 <code>q_{dim}_vec</code> 格式命名向量列（如 <code>q_768_vec</code>、<code>q_1024_vec</code>），距离度量统一为 <strong>cosine 余弦相似度</strong>。切换引擎无需修改应用层代码。
      </div>
    </div>

    <!-- 优劣势分析 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚖️</span> 优劣势分析</div>
      <div class="pros-cons-grid">
        <div class="pros-cons-col">
          <div class="pros-cons-header advantage">✅ 优势</div>
          <ul class="feature-list">
            <li v-for="p in pros" :key="p">{{ p }}</li>
          </ul>
        </div>
        <div class="pros-cons-col">
          <div class="pros-cons-header disadvantage">⚠️ 不足</div>
          <ul class="feature-list">
            <li v-for="c in cons" :key="c">{{ c }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 提供商分类
const providerCategories = ref([
  { category: '国际主流', providers: 'OpenAI、Azure OpenAI、Cohere、Jina 多模态、Voyage AI、Mistral' },
  { category: '国内厂商', providers: '通义千问、智谱 AI、百川、百度文心、火山引擎' },
  { category: '开源平台', providers: 'Ollama、HuggingFace TEI、Xinference、LocalAI、VLLM' },
  { category: '云服务', providers: 'AWS Bedrock、Google Gemini、NVIDIA、SILICONFLOW' },
  { category: '其他', providers: 'Youdao BCE、LM-Studio、DeepInfra、TogetherAI、GPUStack' }
])

// 向量引擎
const vectorEngines = ref([
  { name: 'Elasticsearch', capabilities: 'KNN + query_string + rank_feature', note: '默认引擎，成熟稳定，支持混合检索' },
  { name: 'Infinity', capabilities: 'match_text + match_dense + fusion', note: '高性能原生向量引擎，支持多路融合' },
  { name: 'OpenSearch', capabilities: '自定义 KNN DSL', note: 'AWS 生态兼容，灵活查询 DSL' },
  { name: 'OceanBase', capabilities: 'SQL: fulltext JOIN vector', note: '关系型数据库扩展向量能力，SQL 统一查询' }
])

// 优势
const pros = ref([
  '35+ 嵌入提供商 — 覆盖国际主流、国内厂商、开源平台、云服务四大类别，按需选择',
  '4 种向量引擎 — Elasticsearch（默认）、Infinity、OpenSearch、OceanBase 灵活切换',
  'Jina 多模态嵌入 — 支持图像+文本联合向量化，为多模态检索奠定基础',
  'TEI 本地部署 — 内置 HuggingFace Text Embeddings Inference 容器，零外部依赖'
])

// 不足
const cons = ref([
  '切换模型需重建索引 — 向量维度变化时需全量重新向量化，迁移成本高',
  '引擎间特性不一致 — 不同向量引擎支持的检索能力与 DSL 差异较大',
  '默认非多模态 — 大部分提供商仅支持文本嵌入，多模态能力有限',
  'GPU 需求高 — 本地部署 Embedding 模型对 GPU 资源要求较高'
])
</script>
