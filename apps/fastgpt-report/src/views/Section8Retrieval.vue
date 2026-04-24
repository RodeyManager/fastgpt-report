<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§8 检索系统</h2>
      <p>多策略混合检索与重排序</p>
    </div>

    <div class="source-ref-list">
      <div class="ref-title">&#128204; 核心源码</div>
      <div class="source-ref-item"><span class="ref-file">packages/service/core/dataset/search/controller.ts</span> <span class="ref-desc">检索编排器(999行)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/core/dataset/search/utils.ts</span> <span class="ref-desc">查询扩展编排</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/global/core/dataset/search/utils.ts</span> <span class="ref-desc">RRF融合算法</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/core/ai/rerank/index.ts</span> <span class="ref-desc">Rerank重排序</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/core/ai/functions/queryExtension.ts</span> <span class="ref-desc">查询扩展+亚模优化</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/core/ai/hooks/useTextCosine.ts</span> <span class="ref-desc">Lazy Greedy亚模选择</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/common/string/jieba/index.ts</span> <span class="ref-desc">Jieba中文分词</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/common/vectorDB/controller.ts</span> <span class="ref-desc">向量DB抽象层</span></div>
    </div>

    <!-- 三种搜索模式 -->
    <div class="card">
      <div class="card-title"><span class="icon">&#128269;</span> 三种搜索模式</div>
      <table class="data-table">
        <thead><tr><th>模式</th><th>向量检索限制</th><th>全文检索限制</th><th>说明</th></tr></thead>
        <tbody>
          <tr v-for="m in searchModes" :key="m.mode">
            <td><code>{{ m.mode }}</code></td>
            <td>{{ m.vecLimit }}</td>
            <td>{{ m.ftLimit }}</td>
            <td>{{ m.desc }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 完整检索流程 -->
    <div class="card">
      <div class="card-title"><span class="icon">&#128260;</span> 完整检索流程</div>
      <div class="flow-diagram">
        <div class="flow-row">
          <div class="flow-step primary">用户查询</div>
          <span class="flow-arrow">&rarr;</span>
          <div class="flow-step">Query Extension(可选)</div>
          <span class="flow-arrow">&rarr;</span>
          <div class="flow-step">多查询扩展</div>
        </div>
        <div style="color:var(--accent-blue);font-size:1.4rem;margin:4px 0;">&#11015;</div>
        <div class="flow-row">
          <div class="flow-step">Embedding Recall<br><span style="font-size:0.75rem;color:var(--text-muted)">向量HNSW</span></div>
          <span style="color:var(--text-muted);margin:0 12px;">+</span>
          <div class="flow-step">Full-Text Recall<br><span style="font-size:0.75rem;color:var(--text-muted)">MongoDB $text</span></div>
        </div>
        <div style="color:var(--accent-blue);font-size:1.4rem;margin:4px 0;">&#11015;</div>
        <div class="flow-row">
          <div class="flow-step">RRF融合</div>
          <span class="flow-arrow">&rarr;</span>
          <div class="flow-step">Rerank(可选)</div>
          <span class="flow-arrow">&rarr;</span>
          <div class="flow-step">最终RRF</div>
          <span class="flow-arrow">&rarr;</span>
          <div class="flow-step">去重</div>
          <span class="flow-arrow">&rarr;</span>
          <div class="flow-step">分数过滤</div>
          <span class="flow-arrow">&rarr;</span>
          <div class="flow-step primary">Token预算过滤</div>
        </div>
      </div>
    </div>

    <!-- RRF融合算法 -->
    <div class="card">
      <div class="card-title"><span class="icon">&#129518;</span> RRF融合算法</div>
      <div class="code-block">
        <span class="lang-tag">TypeScript</span>
        <pre><span class="code-comment">// Reciprocal Rank Fusion</span>
<span class="code-keyword">const</span> score = weight * (<span class="code-number">1</span> / (<span class="code-number">60</span> + rank));

<span class="code-comment">// 两阶段: 1.通道内多查询RRF  2.跨通道RRF(embedding+fullText)</span>
<span class="code-comment">// 可选第三阶段: RRF + Rerank 加权融合</span></pre>
      </div>
    </div>

    <!-- 召回贡献图表 -->
    <div class="card">
      <div class="card-title"><span class="icon">&#128202;</span> 召回通道贡献</div>
      <div id="chart-recall-contribution" class="chart-container short"></div>
    </div>

    <!-- Query Extension -->
    <div class="card">
      <div class="card-title"><span class="icon">&#128161;</span> 问题扩展 (Query Extension)</div>
      <div class="highlight-block">
        LLM生成10个多样化查询 &rarr; 嵌入向量化 &rarr; 余弦相似度计算 &rarr; 亚模优化(Lazy Greedy) &rarr; 选择Top 3最相关且多样的查询。alpha=0.3平衡相关性与多样性
      </div>
    </div>

    <!-- 搜索参数配置 -->
    <div class="card">
      <div class="card-title"><span class="icon">&#9881;</span> 搜索参数配置</div>
      <table class="data-table">
        <thead><tr><th>参数</th><th>默认值</th><th>说明</th></tr></thead>
        <tbody>
          <tr v-for="p in params" :key="p.name">
            <td><code>{{ p.name }}</code></td>
            <td>{{ p.defaultVal }}</td>
            <td>{{ p.desc }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="card">
      <div class="card-title"><span class="icon">&#9881;</span> 混合检索与RRF融合源码</div>
      <div class="code-block">
        <span class="lang-tag">TypeScript</span>
        <pre><span class="code-comment">// packages/global/core/dataset/search/utils.ts</span>
<span class="code-comment">// RRF (Reciprocal Rank Fusion) 融合算法</span>
<span class="code-keyword">const</span> <span class="code-func">datasetSearchResultConcat</span> = (arr) => {
  arr.forEach(({ weight, list }) => {
    list.forEach((data, index) => {
      <span class="code-keyword">const</span> rank = index + <span class="code-number">1</span>;
      <span class="code-keyword">const</span> score = weight * (<span class="code-number">1</span> / (<span class="code-number">60</span> + rank)); <span class="code-comment">// k=60</span>
      <span class="code-comment">// 合并: 同一数据取最高分</span>
    });
  });
  <span class="code-keyword">return</span> sortedByRRFScore;
};

<span class="code-comment">// packages/service/core/dataset/search/controller.ts</span>
<span class="code-comment">// 双通道并行检索 → RRF融合 → 可选Rerank</span>
<span class="code-keyword">const</span> [embResult, ftResult] = <span class="code-keyword">await</span> Promise.all([
  <span class="code-func">embeddingRecall</span>({ queries, limit: <span class="code-number">80</span> }),
  <span class="code-func">fullTextRecall</span>({ queries, limit: <span class="code-number">60</span> })
]);
<span class="code-keyword">const</span> rrfResult = <span class="code-func">datasetSearchResultConcat</span>([
  { weight: <span class="code-number">0.5</span>, list: embResult },
  { weight: <span class="code-number">0.5</span>, list: ftResult }
]);</pre>
      </div>
    </div>

    <!-- 9阶段检索增强流水线 -->
    <div class="card">
      <div class="card-title"><span class="icon">&#128269;</span> 9阶段检索增强流水线</div>
      <div class="flow-diagram">
        <div class="flow-steps">
          <div class="flow-step">Stage 0<br><small>入口</small></div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step primary">Stage 1<br><small>查询扩展</small></div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step primary">Stage 1a<br><small>LLM生成10候选</small></div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step primary">Stage 1b<br><small>亚模选Top3</small></div>
        </div>
        <div class="flow-steps" style="margin-top:10px;">
          <div class="flow-step">Stage 2<br><small>限制计算</small></div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step" style="background:rgba(6,182,212,0.15);border-color:var(--accent-cyan);">Stage 3+4<br><small>双通道并行</small></div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step">Stage 5<br><small>通道内RRF</small></div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step primary">Stage 6<br><small>跨通道RRF</small></div>
        </div>
        <div class="flow-steps" style="margin-top:10px;">
          <div class="flow-step primary">Stage 7<br><small>Rerank重排</small></div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step">Stage 8<br><small>分数过滤+Token预算</small></div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step" style="background:rgba(16,185,129,0.15);border-color:var(--accent-green);">&#10003; 最终结果</div>
        </div>
      </div>
    </div>

    <!-- 纯向量检索模式 (collapsible) -->
    <div class="collapsible-code">
      <div class="collapsible-header" onclick="this.querySelector('.toggle-icon').classList.toggle('open');this.nextElementSibling.classList.toggle('open')">
        <span class="title"><span class="icon">&#128200;</span> 纯向量检索模式 (embedding)</span>
        <span class="toggle-icon">&#9654;</span>
      </div>
      <div class="collapsible-body">
        <div class="code-block">
          <span class="lang-tag">TypeScript</span>
          <pre><span class="code-comment">// packages/service/core/dataset/search/controller.ts</span>
<span class="code-comment">// searchMode = 'embedding' — 仅使用向量相似度检索</span>

<span class="code-keyword">const</span> <span class="code-func">embeddingRecall</span> = <span class="code-keyword">async</span> ({ queries, limit }) => {
  <span class="code-comment">// 对每个扩展查询分别进行向量检索</span>
  <span class="code-keyword">const</span> results = <span class="code-keyword">await</span> Promise.<span class="code-func">all</span>(
    queries.<span class="code-func">map</span>(q =>
      vectorDB.<span class="code-func">search</span>({
        model: q.embeddingModel,   <span class="code-comment">// 嵌入模型</span>
        query: q.vector,           <span class="code-comment">// 查询向量</span>
        limit,                     <span class="code-comment">// Top 80</span>
        datasetIds: q.datasetIds
      })
    )
  );
  <span class="code-comment">// 通道内多查询RRF融合</span>
  <span class="code-keyword">return</span> <span class="code-func">datasetSearchResultConcat</span>(
    results.<span class="code-func">map</span>(list => ({ weight: <span class="code-number">1</span>, list }))
  );
};</pre>
        </div>
      </div>
    </div>

    <!-- 纯全文检索模式 (collapsible) -->
    <div class="collapsible-code">
      <div class="collapsible-header" onclick="this.querySelector('.toggle-icon').classList.toggle('open');this.nextElementSibling.classList.toggle('open')">
        <span class="title"><span class="icon">&#128200;</span> 纯全文检索模式 (fullTextRecall)</span>
        <span class="toggle-icon">&#9654;</span>
      </div>
      <div class="collapsible-body">
        <div class="code-block">
          <span class="lang-tag">TypeScript + MongoDB</span>
          <pre><span class="code-comment">// packages/service/core/dataset/search/controller.ts</span>
<span class="code-comment">// searchMode = 'fullTextRecall' — 仅使用全文关键词检索</span>

<span class="code-keyword">const</span> <span class="code-func">fullTextRecall</span> = <span class="code-keyword">async</span> ({ queries, limit }) => {
  <span class="code-comment">// 使用 MongoDB $text 索引进行全文检索</span>
  <span class="code-keyword">const</span> results = <span class="code-keyword">await</span> Promise.<span class="code-func">all</span>(
    queries.<span class="code-func">map</span>(q => {
      <span class="code-keyword">const</span> searchText = <span class="code-func">jiebaCut</span>(q.text); <span class="code-comment">// Jieba分词</span>
      <span class="code-keyword">return</span> MongoCollection.<span class="code-func">find</span>(
        { $text: { $search: searchText },
          datasetId: { $in: q.datasetIds } },
        { score: { $meta: <span class="code-string">'textScore'</span> } }
      ).<span class="code-func">sort</span>({ score: { $meta: <span class="code-string">'textScore'</span> } })
       .<span class="code-func">limit</span>(limit)              <span class="code-comment">// Top 60</span>
       .<span class="code-func">toArray</span>();
    })
  );
  <span class="code-keyword">return</span> <span class="code-func">datasetSearchResultConcat</span>(
    results.<span class="code-func">map</span>(list => ({ weight: <span class="code-number">1</span>, list }))
  );
};</pre>
        </div>
      </div>
    </div>

    <!-- 混合检索模式 (collapsible) -->
    <div class="collapsible-code">
      <div class="collapsible-header" onclick="this.querySelector('.toggle-icon').classList.toggle('open');this.nextElementSibling.classList.toggle('open')">
        <span class="title"><span class="icon">&#128200;</span> 混合检索模式 (mixedRecall)</span>
        <span class="toggle-icon">&#9654;</span>
      </div>
      <div class="collapsible-body">
        <div class="code-block">
          <span class="lang-tag">TypeScript</span>
          <pre><span class="code-comment">// packages/service/core/dataset/search/controller.ts</span>
<span class="code-comment">// searchMode = 'mixedRecall' (默认) — 双通道并行 + RRF融合</span>

<span class="code-comment">// Stage 3+4: 双通道并行召回</span>
<span class="code-keyword">const</span> [embResult, ftResult] = <span class="code-keyword">await</span> Promise.<span class="code-func">all</span>([
  <span class="code-func">embeddingRecall</span>({ queries, limit: embeddingLimit }),  <span class="code-comment">// Top 80</span>
  <span class="code-func">fullTextRecall</span>({ queries, limit: fullTextLimit })     <span class="code-comment">// Top 60</span>
]);

<span class="code-comment">// Stage 5: 通道内多查询RRF (各自通道的多个查询结果融合)</span>
<span class="code-comment">// Stage 6: 跨通道RRF (embedding + fullText 双通道融合)</span>
<span class="code-keyword">const</span> rrfResult = <span class="code-func">datasetSearchResultConcat</span>([
  { weight: <span class="code-number">0.5</span>, list: embResult },  <span class="code-comment">// 向量通道权重 0.5</span>
  { weight: <span class="code-number">0.5</span>, list: ftResult }   <span class="code-comment">// 全文通道权重 0.5</span>
]);

<span class="code-comment">// Stage 7: 可选Rerank重排序</span>
<span class="code-keyword">const</span> finalResult = rerankModel
  ? <span class="code-keyword">await</span> <span class="code-func">rerankSearchResult</span>(rrfResult, query)
  : rrfResult;</pre>
        </div>
      </div>
    </div>

    <!-- RRF融合算法源码 (collapsible) -->
    <div class="collapsible-code">
      <div class="collapsible-header" onclick="this.querySelector('.toggle-icon').classList.toggle('open');this.nextElementSibling.classList.toggle('open')">
        <span class="title"><span class="icon">&#128200;</span> RRF融合算法源码 (k=60)</span>
        <span class="toggle-icon">&#9654;</span>
      </div>
      <div class="collapsible-body">
        <div class="code-block">
          <span class="lang-tag">TypeScript</span>
          <pre><span class="code-comment">// packages/global/core/dataset/search/utils.ts</span>
<span class="code-comment">// 加权倒数排名融合 (Weighted Reciprocal Rank Fusion)</span>
<span class="code-keyword">export const</span> <span class="code-func">datasetSearchResultConcat</span> = (
  arr: { weight: <span class="code-type">number</span>; list: SearchDataResponseItemType[] }[]
): SearchDataResponseItemType[] => {
  <span class="code-keyword">const</span> map = <span class="code-keyword">new</span> Map&lt;<span class="code-type">string</span>, ...&gt;();

  arr.<span class="code-func">forEach</span>((item) => {
    <span class="code-keyword">const</span> weight = item.weight;
    item.list.<span class="code-func">forEach</span>((data, index) => {
      <span class="code-keyword">const</span> rank = index + <span class="code-number">1</span>;
      <span class="code-comment">// RRF核心公式: score = weight × (1 / (k + rank))  k=60</span>
      <span class="code-keyword">const</span> score = weight * (<span class="code-number">1</span> / (<span class="code-number">60</span> + rank));
      
      <span class="code-keyword">const</span> record = map.<span class="code-func">get</span>(data.id);
      <span class="code-keyword">if</span> (record) {
        <span class="code-comment">// 同一数据: 同类型取最高分, RRF分数累加</span>
        map.<span class="code-func">set</span>(data.id, {
          ...record,
          score: <span class="code-func">concatScore</span>(record.score, data.score),
          rrfScore: record.rrfScore + score
        });
      } <span class="code-keyword">else</span> {
        map.<span class="code-func">set</span>(data.id, { ...data, rrfScore: score });
      }
    });
  });

  <span class="code-keyword">return</span> Array.<span class="code-func">from</span>(map.values())
    .<span class="code-func">sort</span>((a, b) => b.rrfScore - a.rrfScore);
};</pre>
        </div>
      </div>
    </div>

    <!-- 亚模优化查询选择源码 (collapsible) -->
    <div class="collapsible-code">
      <div class="collapsible-header" onclick="this.querySelector('.toggle-icon').classList.toggle('open');this.nextElementSibling.classList.toggle('open')">
        <span class="title"><span class="icon">&#129504;</span> 亚模优化查询选择源码 (Lazy Greedy)</span>
        <span class="toggle-icon">&#9654;</span>
      </div>
      <div class="collapsible-body">
        <div class="code-block">
          <span class="lang-tag">TypeScript</span>
          <pre><span class="code-comment">// packages/service/core/ai/hooks/useTextCosine.ts</span>
<span class="code-comment">// 边际增益 = alpha × 相关性 + (1 - 最大相似度)</span>
<span class="code-comment">// alpha=0.3: 70%多样性 + 30%相关性</span>
<span class="code-keyword">const</span> <span class="code-func">computeMarginalGain</span> = (
  candidateEmbedding, selectedEmbeddings, originalEmbedding,
  alpha = <span class="code-number">0.3</span>
) => {
  <span class="code-keyword">if</span> (selectedEmbeddings.length === <span class="code-number">0</span>) {
    <span class="code-keyword">return</span> alpha * <span class="code-func">cosineSimilarity</span>(originalEmbedding, candidateEmbedding);
  }
  <span class="code-keyword">let</span> maxSimilarity = <span class="code-number">0</span>;
  <span class="code-keyword">for</span> (<span class="code-keyword">const</span> selected <span class="code-keyword">of</span> selectedEmbeddings) {
    maxSimilarity = Math.<span class="code-func">max</span>(
      maxSimilarity,
      <span class="code-func">cosineSimilarity</span>(candidateEmbedding, selected)
    );
  }
  <span class="code-keyword">const</span> relevance = alpha * <span class="code-func">cosineSimilarity</span>(originalEmbedding, candidateEmbedding);
  <span class="code-keyword">const</span> diversity = <span class="code-number">1</span> - maxSimilarity;
  <span class="code-keyword">return</span> relevance + diversity;  <span class="code-comment">// 亚模增益</span>
};

<span class="code-comment">// Lazy Greedy选择: 从LLM生成的10个候选中选最优3个</span>
<span class="code-keyword">const</span> { selectedData: selectedQueries } = <span class="code-keyword">await</span>
  <span class="code-func">lazyGreedyQuerySelection</span>({
    originalText: query,
    candidates: queries,         <span class="code-comment">// LLM生成的~10个候选查询</span>
    k: Math.<span class="code-func">min</span>(<span class="code-number">3</span>, queries.length), <span class="code-comment">// 最多选3个</span>
    alpha: <span class="code-number">0.3</span>                     <span class="code-comment">// 相关性vs多样性权衡</span>
  });</pre>
        </div>
      </div>
    </div>

    <!-- PostgreSQL HNSW向量检索源码 (collapsible) -->
    <div class="collapsible-code">
      <div class="collapsible-header" onclick="this.querySelector('.toggle-icon').classList.toggle('open');this.nextElementSibling.classList.toggle('open')">
        <span class="title"><span class="icon">&#128268;</span> PostgreSQL HNSW向量检索源码</span>
        <span class="toggle-icon">&#9654;</span>
      </div>
      <div class="collapsible-body">
        <div class="code-block">
          <span class="lang-tag">SQL + TypeScript</span>
          <pre><span class="code-comment">// packages/service/common/vectorDB/pg/index.ts</span>
<span class="code-comment">// HNSW近似最近邻检索 (内积距离)</span>
<span class="code-keyword">const</span> sql = <span class="code-string">`
  BEGIN;
    SET LOCAL hnsw.ef_search = <span class="code-number">${</span>global.systemEnv?.hnswEfSearch || <span class="code-number">100</span><span class="code-number">}</span>;
    SET LOCAL hnsw.max_scan_tuples = <span class="code-number">${</span>global.systemEnv?.hnswMaxScanTuples || <span class="code-number">100000</span><span class="code-number">}</span>;
    SET LOCAL hnsw.iterative_scan = relaxed_order;

    WITH relaxed_results AS MATERIALIZED (
      SELECT id, collection_id,
             vector <span class="code-comment">&lt;#&gt;</span> '[${vector}]' AS score
        FROM modeldata
       WHERE dataset_id IN (${datasetIds})
       ORDER BY score
       LIMIT ${limit}
    )
    SELECT id, collection_id, score
      FROM relaxed_results ORDER BY score;
  COMMIT;
`</span>;

<span class="code-comment">// &lt;#&gt; 返回负内积, 因此取反得到正值相似度</span>
<span class="code-keyword">return</span> rows.<span class="code-func">map</span>(item => ({
  id: String(item.id),
  collectionId: item.collection_id,
  score: item.score * <span class="code-number">-1</span>  <span class="code-comment">// 取反</span>
}));</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const searchModes = ref([
  { mode: 'embedding', vecLimit: 'Top 80', ftLimit: '-', desc: '纯向量检索' },
  { mode: 'fullTextRecall', vecLimit: '-', ftLimit: 'Top 60', desc: '纯全文检索' },
  { mode: 'mixedRecall(默认)', vecLimit: 'Top 80', ftLimit: 'Top 60', desc: '双通道RRF融合' }
])

const params = ref([
  { name: 'embeddingLimit', defaultVal: '80', desc: '向量检索返回数量' },
  { name: 'fullTextLimit', defaultVal: '60', desc: '全文检索返回数量' },
  { name: 'rrfK', defaultVal: '60', desc: 'RRF常数k' },
  { name: 'maxTokens', defaultVal: '自定义', desc: 'Token预算上限' },
  { name: 'searchMode', defaultVal: 'mixedRecall', desc: '搜索模式选择' }
])

onMounted(() => {
  const el = document.getElementById('chart-recall-contribution')
  if (!el) return
  const chart = echarts.init(el)
  chart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      bottom: 0,
      textStyle: { color: '#94a3b8', fontSize: 12 },
      itemWidth: 12, itemHeight: 12, itemGap: 20
    },
    grid: {
      left: '3%', right: '4%', bottom: '12%', top: '8%', containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['embedding', 'fullText', 'mixed'],
      axisLabel: { color: '#94a3b8', fontSize: 12 },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      name: '召回贡献 (%)',
      nameTextStyle: { color: '#94a3b8', fontSize: 11 },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#1e293b' } }
    },
    series: [
      {
        name: 'Embedding通道',
        type: 'bar',
        stack: 'total',
        barWidth: '40%',
        itemStyle: { color: '#6366f1', borderRadius: [0, 0, 0, 0] },
        data: [85, 0, 42]
      },
      {
        name: 'FullText通道',
        type: 'bar',
        stack: 'total',
        itemStyle: { color: '#06b6d4', borderRadius: [4, 4, 0, 0] },
        data: [0, 78, 38]
      }
    ]
  })
  window.addEventListener('resize', () => chart.resize())
})
</script>
