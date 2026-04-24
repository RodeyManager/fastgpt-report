<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§7 文本向量化</h2>
      <p>Embedding模型与向量存储 — 多后端向量数据库适配与检索优化</p>
    </div>

    <div class="source-ref-list">
      <div class="ref-title">&#128204; 核心源码</div>
      <div class="source-ref-item"><span class="ref-file">packages/service/core/ai/embedding/index.ts</span> <span class="ref-desc">向量化核心(getVectorsByText, formatVectors)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/common/vectorDB/controller.ts</span> <span class="ref-desc">向量DB抽象层</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/common/vectorDB/pg/index.ts</span> <span class="ref-desc">pgvector实现(HNSW检索)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/global/core/ai/constants.ts</span> <span class="ref-desc">默认模型配置</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/core/ai/config.ts</span> <span class="ref-desc">AI API配置(getAIApi)</span></div>
    </div>

    <div class="two-col">
      <!-- 默认嵌入模型 -->
      <div class="card">
        <div class="card-title"><span class="icon">🧠</span> 默认嵌入模型</div>
        <div class="highlight-block">
          <strong>text-embedding-3-small</strong> (OpenAI)，支持任何OpenAI兼容模型通过配置接入<br/>
          <strong>API路由：</strong><code>userKey</code> &gt; <code>oneapiUrl</code> &gt; <code>AIPROXY</code> &gt; <code>OPENAI_BASE_URL</code>
        </div>
      </div>

      <!-- 向量格式化逻辑 -->
      <div class="card">
        <div class="card-title"><span class="icon">📐</span> 向量格式化逻辑</div>
        <pre class="code-block"><code>function formatVectors(vector, normalization = false) {
  if (vector.length > 1536)
    return normalize(vector.slice(0, 1536));
  if (vector.length < 1536)
    vector = vector.concat(
      new Array(1536 - vector.length).fill(0)
    );
  return normalization
    ? normalize(vector) : vector;
}</code></pre>
        <ul class="feature-list" style="margin-top: 12px">
          <li><strong>固定1536维度</strong> — 零填充 / 截断对齐</li>
          <li><strong>可选L2归一化</strong> — 归一化提升余弦相似度精度</li>
          <li><strong>嵌入类型：</strong><code>db</code>（存储）vs <code>query</code>（查询）</li>
        </ul>
      </div>
    </div>

    <!-- 向量数据库对比 -->
    <div class="card">
      <div class="card-title"><span class="icon">🗄️</span> 向量数据库对比</div>
      <table class="data-table">
        <thead>
          <tr><th>后端</th><th>连接方式</th><th>量化精度</th><th>HNSW配置</th></tr>
        </thead>
        <tbody>
          <tr v-for="db in vectorDbs" :key="db.name">
            <td><strong>{{ db.name }}</strong></td>
            <td><code>{{ db.conn }}</code></td>
            <td>{{ db.precision }}</td>
            <td>{{ db.hnsw }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 雷达图 -->
    <div class="card">
      <div class="card-title"><span class="icon">📊</span> 向量数据库综合对比</div>
      <div id="chart-vector-db" class="chart-container"></div>
    </div>

    <!-- API路由优先级 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔗</span> API路由优先级</div>
      <ul class="feature-list">
        <li v-for="(r, i) in apiRoutes" :key="i">
          <strong>{{ r.label }}</strong> <code>{{ r.key }}</code> — {{ r.desc }}
        </li>
      </ul>
    </div>

    <!-- 向量化与向量插入源码 -->
    <div class="card">
      <div class="card-title"><span class="icon">&#9881;</span> 向量化与向量插入源码</div>
      <div class="code-block">
        <span class="lang-tag">TypeScript</span>
        <pre><span class="code-comment">// packages/service/core/ai/embedding/index.ts</span>
<span class="code-keyword">async function</span> <span class="code-func">getVectorsByText</span>({ model, input, type }) {
  <span class="code-keyword">const</span> ai = <span class="code-func">getAIApi</span>();
  <span class="code-keyword">const</span> result = <span class="code-keyword">await</span> ai.embeddings.<span class="code-func">create</span>({
    model: model.model,
    input: chunk,
    encoding_format: <span class="code-string">'float'</span>,
    ...(type === <span class="code-string">'db'</span> && model.dbConfig),
    ...(type === <span class="code-string">'query'</span> && model.queryConfig)
  });
  <span class="code-keyword">return</span> {
    vectors: result.data.map(i => <span class="code-func">formatVectors</span>(i.embedding)),
    tokens: result.usage.total_tokens
  };
}

<span class="code-comment">// packages/service/common/vectorDB/pg/index.ts</span>
<span class="code-comment">// PostgreSQL HNSW 向量检索</span>
<span class="code-keyword">const</span> sql = <span class="code-string">`
  SET LOCAL hnsw.ef_search = 100;
  SELECT id, collection_id, vector <#> $1 AS score
  FROM modeldata WHERE dataset_id = ANY($2)
  ORDER BY score LIMIT $3
`</span>;</pre>
      </div>
    </div>

    <!-- ========== 多向量索引 (Multi-Vector Indexing) ========== -->

    <!-- Card 1: 多向量索引核心架构 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚡</span> 多向量索引（Multi-Vector Indexing）核心架构</div>
      <div class="highlight-block" style="margin-bottom: 20px;">
        FastGPT 对每个 Chunk 可生成<strong>多组索引文本</strong>，每组独立向量化后存入向量数据库。检索时命中任意一个向量即可召回整个 Chunk，通过 RRF 融合多路结果实现高召回率。
      </div>

      <!-- Architecture Diagram -->
      <div class="arch-container" style="padding: 24px 20px; margin: 16px 0;">
        <div style="text-align: center; margin-bottom: 16px;">
          <div style="display: inline-block; background: rgba(139,92,246,0.2); border: 2px solid #8b5cf6; border-radius: 10px; padding: 12px 24px;">
            <div style="font-size: 0.72rem; color: #8b5cf6; font-weight: 600; margin-bottom: 4px;">1 Chunk (q + a)</div>
            <div style="font-size: 0.95rem; font-weight: 700; color: #fff;">formatIndexes()</div>
          </div>
        </div>

        <!-- Branch lines SVG -->
        <div style="display: flex; justify-content: center; margin-bottom: 6px;">
          <svg width="720" height="36" viewBox="0 0 720 36" style="max-width: 100%;">
            <line x1="360" y1="0" x2="72" y2="36" stroke="#6366f1" stroke-width="2" stroke-dasharray="4,3" opacity="0.5"/>
            <line x1="360" y1="0" x2="216" y2="36" stroke="#3b82f6" stroke-width="2" stroke-dasharray="4,3" opacity="0.5"/>
            <line x1="360" y1="0" x2="360" y2="36" stroke="#10b981" stroke-width="2" stroke-dasharray="4,3" opacity="0.5"/>
            <line x1="360" y1="0" x2="504" y2="36" stroke="#ef4444" stroke-width="2" stroke-dasharray="4,3" opacity="0.5"/>
            <line x1="360" y1="0" x2="648" y2="36" stroke="#a855f7" stroke-width="2" stroke-dasharray="4,3" opacity="0.5"/>
          </svg>
        </div>

        <!-- 5 Index Types -->
        <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; text-align: center;">
          <div style="background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3); border-radius: 8px; padding: 10px 6px;">
            <div style="font-size: 0.68rem; color: #6366f1; font-weight: 600; margin-bottom: 4px;">default</div>
            <div style="font-size: 0.68rem; color: #94a3b8;">q/a 子块切分</div>
            <div style="margin-top: 6px; font-size: 0.68rem; color: #10b981; font-weight: 600;">✅ 开源</div>
          </div>
          <div style="background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.3); border-radius: 8px; padding: 10px 6px;">
            <div style="font-size: 0.68rem; color: #3b82f6; font-weight: 600; margin-bottom: 4px;">custom</div>
            <div style="font-size: 0.68rem; color: #94a3b8;">用户自定义</div>
            <div style="margin-top: 6px; font-size: 0.68rem; color: #10b981; font-weight: 600;">✅ 开源</div>
          </div>
          <div style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 8px; padding: 10px 6px;">
            <div style="font-size: 0.68rem; color: #10b981; font-weight: 600; margin-bottom: 4px;">summary</div>
            <div style="font-size: 0.68rem; color: #94a3b8;">LLM 生成摘要</div>
            <div style="margin-top: 6px; font-size: 0.68rem; color: #f59e0b; font-weight: 600;">🔒 Plus</div>
          </div>
          <div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 8px; padding: 10px 6px;">
            <div style="font-size: 0.68rem; color: #ef4444; font-weight: 600; margin-bottom: 4px;">question</div>
            <div style="font-size: 0.68rem; color: #94a3b8;">LLM 生成问题</div>
            <div style="margin-top: 6px; font-size: 0.68rem; color: #f59e0b; font-weight: 600;">🔒 Plus</div>
          </div>
          <div style="background: rgba(168,85,247,0.1); border: 1px solid rgba(168,85,247,0.3); border-radius: 8px; padding: 10px 6px;">
            <div style="font-size: 0.68rem; color: #a855f7; font-weight: 600; margin-bottom: 4px;">image</div>
            <div style="font-size: 0.68rem; color: #94a3b8;">VLM 图片描述</div>
            <div style="margin-top: 6px; font-size: 0.68rem; color: #f59e0b; font-weight: 600;">🔒 Plus</div>
          </div>
        </div>

        <!-- Storage layers -->
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 16px;">
          <div style="background: rgba(99,102,241,0.06); border: 1px solid rgba(99,102,241,0.2); border-radius: 6px; padding: 10px; text-align: center;">
            <div style="font-size: 0.72rem; font-weight: 600; color: #6366f1;">向量数据库</div>
            <div style="font-size: 0.68rem; color: #94a3b8; margin-top: 4px;">PG / Milvus / OceanBase</div>
            <div style="font-size: 0.68rem; color: #64748b; margin-top: 2px;">每向量一行（无类型字段）</div>
          </div>
          <div style="background: rgba(6,182,212,0.06); border: 1px solid rgba(6,182,212,0.2); border-radius: 6px; padding: 10px; text-align: center;">
            <div style="font-size: 0.72rem; font-weight: 600; color: #06b6d4;">MongoDB dataset_datas</div>
            <div style="font-size: 0.68rem; color: #94a3b8; margin-top: 4px;">indexes[]: { type, dataId, text }</div>
            <div style="font-size: 0.68rem; color: #64748b; margin-top: 2px;">1 Chunk 文档 → N 索引条目</div>
          </div>
          <div style="background: rgba(245,158,11,0.06); border: 1px solid rgba(245,158,11,0.2); border-radius: 6px; padding: 10px; text-align: center;">
            <div style="font-size: 0.72rem; font-weight: 600; color: #f59e0b;">MongoDB data_texts</div>
            <div style="font-size: 0.68rem; color: #94a3b8; margin-top: 4px;">fullTextToken (Jieba 分词)</div>
            <div style="font-size: 0.68rem; color: #64748b; margin-top: 2px;">MongoDB $text 全文检索</div>
          </div>
        </div>

        <div style="text-align: center; margin-top: 14px; padding: 8px; background: rgba(16,185,129,0.08); border: 1px dashed rgba(16,185,129,0.3); border-radius: 8px;">
          <span style="color: #10b981; font-weight: 600; font-size: 0.82rem;">检索时命中 indexes[].dataId 中的任意一个向量 → 整个 Chunk 被召回</span>
        </div>
      </div>

      <div class="source-ref-list" style="margin-top: 12px;">
        <div class="ref-title">&#128204; 核心源码</div>
        <div class="source-ref-item"><span class="ref-file">packages/global/core/dataset/data/constants.ts</span> <span class="ref-desc">DatasetDataIndexTypeEnum 五种索引类型枚举</span></div>
        <div class="source-ref-item"><span class="ref-file">projects/app/src/service/core/dataset/data/controller.ts</span> <span class="ref-desc">formatIndexes() + insertData2Dataset() 核心插入逻辑</span></div>
        <div class="source-ref-item"><span class="ref-file">packages/service/common/string/jieba/index.ts</span> <span class="ref-desc">jiebaSplit() 全文搜索 token 生成</span></div>
      </div>
    </div>

    <!-- Card 2: 五种索引类型详解 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔬</span> 五种索引类型详解（源码级）</div>
      <table class="data-table">
        <thead>
          <tr>
            <th>类型</th>
            <th>颜色</th>
            <th>生成方式</th>
            <th>源码位置</th>
            <th>可用性</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>default</strong></td>
            <td>灰色</td>
            <td><code>formatIndexes()</code> 将 q/a 按 <code>indexSize</code>（默认512 token）切分为子块，每块独立向量化</td>
            <td><code>data/controller.ts:51-81</code></td>
            <td><span style="color: #10b981; font-weight: 600;">✅ 开源</span></td>
          </tr>
          <tr>
            <td><strong>custom</strong></td>
            <td>蓝色</td>
            <td>用户手动添加 / CSV 备份导入第3+列 / API <code>indexes</code> 字段</td>
            <td><code>data/constants.ts:3-9</code></td>
            <td><span style="color: #10b981; font-weight: 600;">✅ 开源</span></td>
          </tr>
          <tr>
            <td><strong>summary</strong></td>
            <td>绿色</td>
            <td>Plus API <code>/core/dataset/training/llmPargraph</code> 由 LLM 生成摘要式索引</td>
            <td><code>collection/utils.ts:242-248</code></td>
            <td><span style="color: #f59e0b; font-weight: 600;">🔒 Plus</span></td>
          </tr>
          <tr>
            <td><strong>question</strong></td>
            <td>红色</td>
            <td>Plus API 由 LLM 生成问题式索引，增强问答场景匹配</td>
            <td><code>collection/utils.ts:242-248</code></td>
            <td><span style="color: #f59e0b; font-weight: 600;">🔒 Plus</span></td>
          </tr>
          <tr>
            <td><strong>image</strong></td>
            <td>紫色</td>
            <td>VLM 模型生成图片语义描述后向量化</td>
            <td><code>collection/utils.ts:235-240</code></td>
            <td><span style="color: #f59e0b; font-weight: 600;">🔒 Plus</span></td>
          </tr>
        </tbody>
      </table>

      <div class="highlight-block" style="margin-top: 16px;">
        <strong>开源版实际可用的多向量索引：</strong><code>default</code>（q/a 文本子块切分）+ <code>custom</code>（用户自定义）。<br/>
        <code>summary</code> / <code>question</code> / <code>image</code> 三种类型的枚举定义存在于开源代码中，但生成逻辑由 FastGPT Plus 商业版服务端处理。
      </div>

      <!-- formatIndexes flow -->
      <div style="margin-top: 16px; padding: 16px; background: rgba(15,23,42,0.5); border-radius: 8px; border: 1px solid rgba(99,102,241,0.15);">
        <div style="font-size: 0.85rem; font-weight: 600; color: #06b6d4; margin-bottom: 10px;">formatIndexes() 处理流程</div>
        <div style="font-size: 0.78rem; color: #cbd5e1; line-height: 1.8;">
          <strong>1.</strong> 将 <code>q</code> 文本按 <code>indexSize</code> 切分 → 每个子块 → <code>{ type: "default", text: "子块" }</code><br/>
          <strong>2.</strong> 将 <code>a</code> 文本按 <code>indexSize</code> 切分 → 每个子块 → <code>{ type: "default", text: "子块" }</code><br/>
          <strong>3.</strong> 合并已有的 custom/summary/question 索引，与 default 去重<br/>
          <strong>4.</strong> 超长非 default 索引 → 再次切分<br/>
          <strong>5.</strong> 可选为 default 索引加 <code>indexPrefix</code>（集合名称前缀）<br/>
          <strong>6.</strong> 所有索引文本 → <code>insertDatasetDataVector()</code> 一次性批量嵌入 → 存入向量数据库
        </div>
      </div>
    </div>

    <!-- Card 3: 三路检索架构 -->
    <div class="card">
      <div class="card-title"><span class="icon">🎯</span> 三路检索架构与 RRF 融合</div>

      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 20px;">
        <!-- 向量召回 -->
        <div style="background: rgba(99,102,241,0.06); border: 1px solid rgba(99,102,241,0.25); border-radius: 8px; padding: 16px;">
          <div style="font-size: 0.92rem; font-weight: 700; color: #6366f1; margin-bottom: 10px;">🔍 向量召回</div>
          <div style="font-size: 0.78rem; color: #cbd5e1; line-height: 1.7;">
            查询向量化 → HNSW 相似度搜索<br/>
            命中任意 <code>indexes[].dataId</code><br/>
            → 反查 MongoDB 得到 Chunk<br/>
            <strong>embedding 模式 limit: 100</strong>
          </div>
          <div style="margin-top: 8px; font-size: 0.72rem; color: #64748b;">源码: search/controller.ts</div>
        </div>
        <!-- 全文检索 -->
        <div style="background: rgba(245,158,11,0.06); border: 1px solid rgba(245,158,11,0.25); border-radius: 8px; padding: 16px;">
          <div style="font-size: 0.92rem; font-weight: 700; color: #f59e0b; margin-bottom: 10px;">📝 全文检索</div>
          <div style="font-size: 0.78rem; color: #cbd5e1; line-height: 1.7;">
            Jieba 分词生成 <code>fullTextToken</code><br/>
            → MongoDB <code>$text</code> 搜索<br/>
            过滤1400+双语停用词<br/>
            <strong>fullText 模式 limit: 100</strong>
          </div>
          <div style="margin-top: 8px; font-size: 0.72rem; color: #64748b;">源码: jieba/index.ts</div>
        </div>
        <!-- Rerank精排 -->
        <div style="background: rgba(16,185,129,0.06); border: 1px solid rgba(16,185,129,0.25); border-radius: 8px; padding: 16px;">
          <div style="font-size: 0.92rem; font-weight: 700; color: #10b981; margin-bottom: 10px;">🎯 Rerank 精排</div>
          <div style="font-size: 0.78rem; color: #cbd5e1; line-height: 1.7;">
            外部 Cross-Encoder 模型<br/>
            → 对候选结果二次评分<br/>
            <code>rerankWeight</code> 加权融合<br/>
            <strong>可选开启</strong>
          </div>
          <div style="margin-top: 8px; font-size: 0.72rem; color: #64748b;">源码: ai/rerank/index.ts</div>
        </div>
      </div>

      <!-- RRF formula -->
      <div style="padding: 14px; background: rgba(139,92,246,0.06); border: 1px solid rgba(139,92,246,0.2); border-radius: 8px; margin-bottom: 16px;">
        <div style="font-size: 0.85rem; font-weight: 600; color: #8b5cf6; margin-bottom: 8px;">RRF 融合公式 (Reciprocal Rank Fusion)</div>
        <div style="text-align: center; padding: 10px; background: rgba(0,0,0,0.3); border-radius: 6px; font-family: monospace; font-size: 0.9rem; color: #e2e8f0;">
          score = weight × ( 1 / ( 60 + rank ) )
        </div>
        <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 8px; line-height: 1.6;">
          <strong>同 Chunk 被多路命中 → RRF 分数叠加 → 排名提升</strong><br/>
          向量召回权重 <code>embeddingWeight</code> + 全文权重 <code>(1 - embeddingWeight)</code>；Rerank 结果再按 <code>rerankWeight</code> 加权融合。<br/>
          源码: <code>packages/global/core/dataset/search/utils.ts</code>
        </div>
      </div>

      <!-- Search modes -->
      <table class="data-table" style="font-size: 0.82rem;">
        <thead>
          <tr><th>搜索模式</th><th>召回策略</th><th>向量 limit</th><th>全文 limit</th></tr>
        </thead>
        <tbody>
          <tr>
            <td><code>embedding</code></td>
            <td>纯向量相似度</td>
            <td>100</td>
            <td>0</td>
          </tr>
          <tr>
            <td><code>fullTextRecall</code></td>
            <td>纯全文检索</td>
            <td>0</td>
            <td>100</td>
          </tr>
          <tr>
            <td><code>mixedRecall</code></td>
            <td>双路并行 + RRF 融合</td>
            <td>80</td>
            <td>60</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Card 4: 训练模式与索引策略 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚙️</span> 训练模式与索引策略</div>
      <div style="font-size: 0.82rem; color: #94a3b8; margin-bottom: 14px;">
        训练模式由 <code>getTrainingModeByCollection()</code> 根据集合配置和 Plus 状态决定，优先级从高到低：
      </div>
      <table class="data-table">
        <thead>
          <tr><th>训练模式</th><th>使用模型</th><th>触发条件</th><th>产生的索引类型</th></tr>
        </thead>
        <tbody>
          <tr>
            <td><code>chunk</code></td>
            <td>embedding 模型</td>
            <td>默认模式</td>
            <td><span style="color:#6366f1; font-weight:600;">default</span>（q/a 子块切分）</td>
          </tr>
          <tr>
            <td><code>qa</code></td>
            <td>agent LLM</td>
            <td>手动选择 QA 模式</td>
            <td><span style="color:#6366f1; font-weight:600;">default</span>（LLM 生成 Q&A 对后再切分）</td>
          </tr>
          <tr>
            <td><code>auto</code></td>
            <td>agent LLM</td>
            <td><code>autoIndexes=true && isPlus</code></td>
            <td><span style="color:#6366f1;">default</span> + <span style="color:#10b981;">summary</span> + <span style="color:#ef4444;">question</span></td>
          </tr>
          <tr>
            <td><code>image</code></td>
            <td>VLM 模型</td>
            <td><code>imageIndex=true && isPlus</code></td>
            <td><span style="color:#6366f1;">default</span> + <span style="color:#a855f7;">image</span></td>
          </tr>
          <tr>
            <td><code>imageParse</code></td>
            <td>VLM 模型</td>
            <td>图片集合 + isPlus</td>
            <td><span style="color:#a855f7; font-weight:600;">image</span></td>
          </tr>
        </tbody>
      </table>

      <div class="highlight-block" style="margin-top: 16px;">
        <strong>关键参数：</strong><code>indexSize</code>（default 索引子块最大 token 数，默认 512，受模型 maxToken 限制）· <code>embeddingWeight</code>（向量召回在 RRF 中的权重）· <code>rerankWeight</code>（Rerank 结果在最终融合中的权重）<br/>
        <strong>auto 模式预测：</strong>每个 Chunk 预计产生 <code>data.length × 5</code> 条索引（<code>predictDataLimitLength</code>）
      </div>
    </div>

    <!-- Card 5: 不同训练模式的向量数量对比 -->
    <div class="card">
      <div class="card-title"><span class="icon">📊</span> 不同训练模式的向量数量对比（示意）</div>
      <div id="chart-enhanced-index" class="chart-container"></div>
      <div style="font-size: 0.72rem; color: #64748b; text-align: center; margin-top: 8px;">* 示意数据，假设 Chunk 含 800 字 q + 600 字 a，indexSize=512</div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const vectorDbs = ref([
  { name: 'PostgreSQL+pgvector', conn: 'PG_URL', precision: '32位 / 16位 (HALFVEC)', hnsw: 'm=32, ef_construction=128' },
  { name: 'Milvus / Zilliz', conn: 'MILVUS_ADDRESS', precision: '原生', hnsw: 'efConstruction=32, M=64' },
  { name: 'OceanBase', conn: 'OCEANBASE_ADDRESS', precision: '32 / 8 / 1位 (SQ/BQ)', hnsw: 'm=16, ef_construction=200' },
  { name: 'openGauss', conn: 'OPENGAUSS_ADDRESS', precision: '32位', hnsw: 'm=32, ef_construction=128' },
  { name: 'SeekDB', conn: 'SEEKDB_ADDRESS', precision: '原生', hnsw: '复用OceanBase' }
])

const apiRoutes = ref([
  { label: '① 用户自定义 Key.baseUrl', key: 'userKey', desc: '最高优先级，用户级覆盖' },
  { label: '② 系统配置', key: 'systemEnv.oneapiUrl', desc: '运维级 OneAPI 中转地址' },
  { label: '③ AIProxy 代理服务', key: 'AIPROXY_API_ENDPOINT', desc: '内置代理转发，开箱即用' },
  { label: '④ 直接连接（回退）', key: 'OPENAI_BASE_URL', desc: '兜底方案，直连 OpenAI' }
])

onMounted(() => {
  const el = document.getElementById('chart-vector-db')
  if (!el) return
  const chart = echarts.init(el)
  const indicators = [
    { name: '性能', max: 100 },
    { name: '扩展性', max: 100 },
    { name: '精度', max: 100 },
    { name: '易用性', max: 100 },
    { name: '生态', max: 100 }
  ]
  const colors = ['#6366f1', '#06b6d4', '#8b5cf6', '#14b8a6', '#f59e0b']
  const seriesData = [
    { value: [72, 65, 88, 90, 92], name: 'PostgreSQL+pgvector' },
    { value: [92, 95, 95, 70, 78], name: 'Milvus / Zilliz' },
    { value: [78, 82, 85, 75, 65], name: 'OceanBase' },
    { value: [70, 60, 88, 85, 70], name: 'openGauss' },
    { value: [80, 78, 90, 72, 60], name: 'SeekDB' }
  ]
  chart.setOption({
    tooltip: {},
    legend: {
      bottom: 0, textStyle: { color: '#94a3b8', fontSize: 11 },
      itemWidth: 12, itemHeight: 12, itemGap: 14
    },
    radar: {
      indicator: indicators,
      shape: 'polygon',
      splitNumber: 4,
      axisName: { color: '#e2e8f0', fontSize: 12 },
      splitLine: { lineStyle: { color: 'rgba(148,163,184,0.15)' } },
      splitArea: { areaStyle: { color: ['rgba(99,102,241,0.02)', 'rgba(99,102,241,0.05)'] } },
      axisLine: { lineStyle: { color: 'rgba(148,163,184,0.2)' } }
    },
    series: [{
      type: 'radar',
      data: seriesData.map((d, i) => ({
        ...d,
        lineStyle: { color: colors[i], width: 2 },
        areaStyle: { color: colors[i], opacity: 0.08 },
        itemStyle: { color: colors[i] },
        symbol: 'circle', symbolSize: 5
      }))
    }]
  })
  window.addEventListener('resize', () => chart.resize())

  // Multi-Vector Indexing: stacked bar chart by training mode
  const el2 = document.getElementById('chart-enhanced-index')
  if (el2) {
    const chart2 = echarts.init(el2)
    chart2.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: 'rgba(15,23,42,0.95)',
        borderColor: 'rgba(99,102,241,0.3)',
        textStyle: { color: '#e2e8f0', fontSize: 12 }
      },
      legend: {
        bottom: 0,
        textStyle: { color: '#94a3b8', fontSize: 11 },
        itemWidth: 12, itemHeight: 12, itemGap: 16
      },
      grid: {
        left: '3%', right: '4%', bottom: '14%', top: '10%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: ['chunk 模式', 'qa 模式', 'auto 模式 (Plus)', 'image 模式 (Plus)'],
        axisLabel: { color: '#94a3b8', fontSize: 11 },
        axisLine: { lineStyle: { color: 'rgba(148,163,184,0.2)' } }
      },
      yAxis: {
        type: 'value',
        name: '向量数量（个）',
        nameTextStyle: { color: '#94a3b8', fontSize: 11 },
        axisLabel: { color: '#94a3b8', fontSize: 11 },
        splitLine: { lineStyle: { color: 'rgba(148,163,184,0.1)' } }
      },
      series: [
        {
          name: 'default (q/a子块)',
          type: 'bar',
          stack: 'total',
          data: [3, 5, 3, 3],
          itemStyle: { color: '#6366f1' },
          label: { show: true, color: '#e2e8f0', fontSize: 10, position: 'inside' }
        },
        {
          name: 'custom',
          type: 'bar',
          stack: 'total',
          data: [0, 0, 0, 0],
          itemStyle: { color: '#3b82f6' }
        },
        {
          name: 'summary (Plus)',
          type: 'bar',
          stack: 'total',
          data: [0, 0, 2, 0],
          itemStyle: { color: '#10b981' },
          label: { show: true, color: '#e2e8f0', fontSize: 10, position: 'inside' }
        },
        {
          name: 'question (Plus)',
          type: 'bar',
          stack: 'total',
          data: [0, 0, 2, 0],
          itemStyle: { color: '#ef4444' },
          label: { show: true, color: '#e2e8f0', fontSize: 10, position: 'inside' }
        },
        {
          name: 'image (Plus)',
          type: 'bar',
          stack: 'total',
          data: [0, 0, 0, 1],
          itemStyle: { color: '#a855f7' },
          label: { show: true, color: '#e2e8f0', fontSize: 10, position: 'inside' }
        }
      ]
    })
    window.addEventListener('resize', () => chart2.resize())
  }
})
</script>
