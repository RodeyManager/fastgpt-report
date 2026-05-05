<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§8 检索</h2>
      <p>RAGFlow 混合检索流水线 — 查询处理、向量检索、重排序与 GraphRAG</p>
    </div>

    <!-- 检索流水线 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔍</span>检索流水线（6 步）</div>
      <div class="flow-diagram">
        <div class="flow-steps">
          <div class="flow-step primary">查询处理<br><small>FulltextQueryer</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">查询向量化<br><small>LLMBundle.encode_queries</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">混合检索<br><small>Dealer.search</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">重排序<br><small>Rerank / Hybrid</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">排序过滤<br><small>rank_feature</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step" style="border-color:var(--accent, #10b981);">[可选] GraphRAG<br><small>实体/关系/社区</small></div>
        </div>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>流水线说明：</strong>
        ① 查询处理（FulltextQueryer）→ 繁简转换 → 分词 → 词权重 → 同义词扩展 → MatchTextExpr；
        ② 查询向量化（LLMBundle.encode_queries）→ MatchDenseExpr（cosine）；
        ③ 混合检索（Dealer.search）→ MatchText（5%）+ MatchDense（95%）+ FusionExpr（weighted_sum）；
        ④ 重排序 → [有 Rerank] token_sim + rerank_sim / [无 Rerank] hybrid_similarity；
        ⑤ 排序过滤 → rank_feature 评分 + similarity_threshold + 分页；
        ⑥ [可选] GraphRAG 实体/关系/社区检索。
      </div>
    </div>

    <!-- 查询字段权重 + 检索参数 -->
    <div class="two-col">
      <!-- 查询字段权重 -->
      <div class="card">
        <div class="card-title"><span class="icon">⚖️</span>查询字段权重</div>
        <table class="data-table">
          <thead>
            <tr><th>字段</th><th>权重</th><th>说明</th></tr>
          </thead>
          <tbody>
            <tr v-for="f in queryFieldWeights" :key="f.field">
              <td><code>{{ f.field }}</code></td>
              <td><strong>{{ f.weight }}</strong></td>
              <td>{{ f.desc }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 检索参数 -->
      <div class="card">
        <div class="card-title"><span class="icon">⚙️</span>检索参数</div>
        <table class="data-table">
          <thead>
            <tr><th>参数</th><th>默认值</th><th>说明</th></tr>
          </thead>
          <tbody>
            <tr v-for="p in retrievalParams" :key="p.param">
              <td><code>{{ p.param }}</code></td>
              <td><strong>{{ p.defaultVal }}</strong></td>
              <td>{{ p.desc }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Rerank 提供商 -->
    <div class="card">
      <div class="card-title"><span class="icon">🏆</span>Rerank 提供商（18+）</div>
      <div class="feature-list" style="display:flex; flex-wrap:wrap; gap:8px; list-style:none; padding:0; margin:0;">
        <span v-for="r in rerankProviders" :key="r.name" class="tag" :class="r.cls">{{ r.name }}</span>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>Rerank 机制：</strong>配置了 Rerank 模型时，最终得分 = <code>token_sim × weight + rerank_sim × (1 - weight)</code>；未配置时使用 <code>hybrid_similarity = vector_sim × w + text_sim × (1 - w)</code>，其中 w 为 <code>vector_similarity_weight</code>。
      </div>
    </div>

    <!-- GraphRAG 流程 -->
    <div class="card">
      <div class="card-title"><span class="icon">🕸️</span>GraphRAG 检索流程</div>
      <div class="flow-diagram">
        <div class="flow-steps">
          <div class="flow-step primary">query_rewrite<br><small>查询改写</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">get_relevant_ents<br><small>实体检索</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">get_relevant_relations<br><small>关系检索</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">N-hop 路径遍历<br><small>多跳关联</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step" style="border-color:var(--accent, #10b981);">community_retrieval<br><small>社区检索</small></div>
        </div>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>三级检索：</strong>GraphRAG 支持实体级、关系级、社区级三级检索。查询先经过 query_rewrite 改写，再分别检索相关实体和关系，通过 N-hop 路径遍历发现隐式关联，最后通过 community_retrieval 获取社区级别的聚合信息，提供更全面的上下文。
      </div>
    </div>

    <!-- 优势与不足 -->
    <div class="pros-cons-grid">
      <div class="card">
        <div class="card-title"><span class="icon">✅</span>优势</div>
        <ul class="feature-list">
          <li v-for="p in pros" :key="p">{{ p }}</li>
        </ul>
      </div>
      <div class="card">
        <div class="card-title"><span class="icon">⚠️</span>不足</div>
        <ul class="feature-list">
          <li v-for="c in cons" :key="c">{{ c }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 查询字段权重
const queryFieldWeights = ref([
  { field: 'important_kwd', weight: 30, desc: '关键词（高亮）' },
  { field: 'important_tks', weight: 20, desc: '关键词分词' },
  { field: 'question_tks', weight: 20, desc: '问题分词' },
  { field: 'title_tks', weight: 10, desc: '标题分词' },
  { field: 'title_sm_tks', weight: 5, desc: '标题平滑分词' },
  { field: 'content_ltks', weight: 2, desc: '内容分词' },
  { field: 'content_sm_ltks', weight: 1, desc: '内容平滑分词' }
])

// 检索参数
const retrievalParams = ref([
  { param: 'similarity_threshold', defaultVal: '0.2', desc: '相似度阈值' },
  { param: 'vector_similarity_weight', defaultVal: '0.3', desc: '向量相似度权重' },
  { param: 'top_k', defaultVal: '1024', desc: '向量检索召回数' },
  { param: 'top_n', defaultVal: '6', desc: '最终返回条数' },
  { param: 'fusion weights', defaultVal: '"0.05, 0.95"', desc: '文本/向量融合权重' },
  { param: 'minimum_should_match', defaultVal: '0.3 中文 / 0.6 英文', desc: '最小匹配比例' }
])

// Rerank 提供商
const rerankProviders = ref([
  { name: 'Jina', cls: 'tag-blue' },
  { name: 'Xinference', cls: 'tag-green' },
  { name: 'LocalAI', cls: 'tag-purple' },
  { name: 'NVIDIA', cls: 'tag-green' },
  { name: 'LM-Studio', cls: 'tag-blue' },
  { name: 'Cohere / VLLM', cls: 'tag-purple' },
  { name: 'TogetherAI', cls: 'tag-green' },
  { name: 'SILICONFLOW', cls: 'tag-blue' },
  { name: '百度文心', cls: 'tag-purple' },
  { name: 'Voyage AI', cls: 'tag-green' },
  { name: '通义千问', cls: 'tag-blue' },
  { name: 'HuggingFace', cls: 'tag-purple' },
  { name: 'GPUStack', cls: 'tag-green' },
  { name: 'OpenAI', cls: 'tag-blue' },
  { name: 'Ollama', cls: 'tag-green' },
  { name: 'Tongyi (Qwen)', cls: 'tag-purple' },
  { name: 'DashScope', cls: 'tag-blue' },
  { name: 'FastEmbed', cls: 'tag-green' }
])

// 优势
const pros = ref([
  '混合检索 5%+95% — 文本检索与向量检索加权融合，兼顾精确匹配与语义理解',
  '18+ Reranker — 支持 Jina、Cohere、NVIDIA、通义千问等 18 种以上重排序模型',
  '4 种向量引擎 — Elasticsearch KNN / Infinity / OpenSearch / OceanBase 按需切换',
  '同义词 + 词权重 — 内置同义词扩展与字段级权重（important_kwd 权重高达 30）',
  'GraphRAG 三级检索 — 实体级、关系级、社区级三级检索，发现隐式关联',
  '精确页码坐标 — 检索结果携带文档页码与坐标信息，支持精确定位引用来源'
])

// 不足
const cons = ref([
  '权重不可动态调整 — 文本/向量融合权重（0.05/0.95）硬编码，无法按查询自适应',
  '无 LTR — 缺少 Learning-to-Rank 机制，无法基于用户反馈优化排序',
  '稀疏向量有限 — 仅依赖 BM25 全文检索，未引入 SPLADE 等学习型稀疏表示',
  '同义词需手动维护 — 同义词库需要人工配置，缺乏自动同义词发现',
  'GraphRAG 构建耗时 — 实体/关系抽取与社区检测需额外处理时间',
  '仅 PDF/DOCX 精确引用 — 精确页码坐标仅限 PDF 和 DOCX 格式，其他格式不支持'
])
</script>
