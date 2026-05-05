<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§12 高精度混合检索</h2>
      <p>结合向量检索、BM25 和自定义评分，配合先进的重排序技术，提供无与伦比的答案准确性和上下文相关性。</p>
    </div>

    <!-- 混合检索流程图 — 分支合并模式 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔍</span>混合检索架构</div>
      <div class="flow-diagram">
        <!-- 查询输入 -->
        <div style="display:flex; flex-direction:column; align-items:center; gap:0;">
          <div class="flow-step primary" style="min-width:160px;">
            🔎 用户查询<br><small>自然语言输入</small>
          </div>
          <div style="width:2px; height:24px; background:rgba(16,185,129,0.5);"></div>
          <div class="flow-step" style="min-width:160px;">
            ⚙️ 查询处理<br><small>意图识别 + 改写</small>
          </div>
          <div style="width:2px; height:24px; background:rgba(16,185,129,0.5);"></div>

          <!-- 分支点 -->
          <div style="position:relative; width:100%; max-width:620px;">
            <div style="position:absolute; top:0; left:50%; transform:translateX(-50%); width:80%; height:2px; background:rgba(16,185,129,0.3);"></div>
          </div>

          <!-- 三路并行检索 -->
          <div style="display:flex; gap:16px; align-items:flex-start; justify-content:center; flex-wrap:wrap;">
            <div style="display:flex; flex-direction:column; align-items:center; gap:0;">
              <div style="width:2px; height:16px; background:rgba(16,185,129,0.4);"></div>
              <div class="flow-step" style="min-width:150px; border-color:rgba(16,185,129,0.5);">
                📐 向量检索<br><small style="color:#10b981;">权重 95%</small><br><small>语义相似度匹配</small>
              </div>
            </div>
            <div style="display:flex; flex-direction:column; align-items:center; gap:0;">
              <div style="width:2px; height:16px; background:rgba(16,185,129,0.4);"></div>
              <div class="flow-step" style="min-width:150px; border-color:rgba(245,158,11,0.5); background:rgba(245,158,11,0.1);">
                📝 BM25 全文<br><small style="color:#f59e0b;">权重 5%</small><br><small>关键词精确匹配</small>
              </div>
            </div>
            <div style="display:flex; flex-direction:column; align-items:center; gap:0;">
              <div style="width:2px; height:16px; background:rgba(16,185,129,0.4);"></div>
              <div class="flow-step" style="min-width:150px; border-color:rgba(20,184,166,0.5); background:rgba(20,184,166,0.1);">
                ⚡ 自定义评分<br><small style="color:#14b8a6;">可配置</small><br><small>领域规则加权</small>
              </div>
            </div>
          </div>

          <!-- 合并点 -->
          <div style="position:relative; width:100%; max-width:620px;">
            <div style="position:absolute; top:0; left:50%; transform:translateX(-50%); width:80%; height:2px; background:rgba(16,185,129,0.3);"></div>
          </div>
          <div style="display:flex; flex-direction:column; align-items:center; gap:0;">
            <div style="width:2px; height:16px; background:rgba(16,185,129,0.4);"></div>
            <div class="flow-step" style="min-width:180px;">
              🔀 加权融合<br><small>18+ Rerank 模型</small><br><small>内置重排序引擎</small>
            </div>
            <div style="width:2px; height:24px; background:rgba(16,185,129,0.5);"></div>
            <div class="flow-step primary" style="min-width:180px;">
              🎯 Top-K 结果<br><small>similarity threshold 过滤</small><br><small>高质量上下文</small>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 核心检索参数 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚙️</span>核心检索参数</div>
      <div class="metrics-grid">
        <div class="metric-card" v-for="m in metrics" :key="m.label">
          <div class="metric-value">{{ m.value }}</div>
          <div class="metric-label">{{ m.label }}</div>
        </div>
      </div>
    </div>

    <!-- 检索策略对比 + Rerank 提供商 -->
    <div class="two-col">
      <div class="card">
        <div class="card-title"><span class="icon">📊</span>检索策略对比</div>
        <table class="data-table">
          <thead>
            <tr><th>策略</th><th>原理</th><th>优势</th><th>权重</th></tr>
          </thead>
          <tbody>
            <tr v-for="s in strategies" :key="s.name">
              <td><strong>{{ s.icon }} {{ s.name }}</strong></td>
              <td>{{ s.principle }}</td>
              <td>{{ s.advantage }}</td>
              <td><code>{{ s.weight }}</code></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="card">
        <div class="card-title"><span class="icon">🏆</span>Rerank 重排序提供商</div>
        <ul class="feature-list">
          <li v-for="p in rerankProviders" :key="p">{{ p }}</li>
        </ul>
        <div class="highlight-block" style="margin-top:16px;">
          <strong>重排序原理：</strong>对初步检索结果进行 Cross-Encoder 精排，利用 query-document 交互建模大幅提升 Top-K 结果的语义相关性，过滤低质量匹配。
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 核心指标
const metrics = ref([
  { value: '1024', label: 'Top-K 候选数' },
  { value: '6', label: 'Top-N 输出数' },
  { value: '0.2', label: '相似度阈值' },
  { value: '18+', label: 'Rerank 提供商' },
  { value: '95%', label: '向量检索权重' },
  { value: '5%', label: 'BM25 权重' }
])

// 检索策略
const strategies = ref([
  { icon: '📐', name: '向量检索', principle: 'Embedding 语义相似度', advantage: '理解语义，跨语言', weight: '0.95' },
  { icon: '📝', name: 'BM25 全文', principle: 'TF-IDF 关键词匹配', advantage: '精确词项匹配', weight: '0.05' },
  { icon: '⚡', name: '自定义评分', principle: '领域规则加权', advantage: '业务定制化', weight: '可配置' },
  { icon: '🔀', name: '加权融合', principle: '多路分数归一化合并', advantage: '综合优势互补', weight: '加权求和' }
])

// Rerank 提供商
const rerankProviders = ref([
  '内置 Rerank 模型 — 开箱即用的 Cross-Encoder 精排',
  'OpenAI Rerank — GPT 系列语义重排序',
  'Cohere Rerank — 工业级重排序 API',
  'BAAI/bge-reranker — 开源中文重排序模型',
  'Jina Reranker — 高性能多语言重排序',
  'Qwen Rerank — 通义千问重排序模型',
  '支持自定义 Rerank 模型接入'
])
</script>
