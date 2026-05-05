<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§1 项目架构概览</h2>
      <p>RAGFlow v0.24.0 系统架构全解析 — 核心指标、Docker 服务矩阵与技术栈</p>
    </div>

    <!-- 核心指标 -->
    <div class="metrics-grid">
      <div class="metric-card" v-for="m in metrics" :key="m.label">
        <div class="metric-value">{{ m.value }}</div>
        <div class="metric-label">{{ m.label }}</div>
      </div>
    </div>

    <!-- 系统架构流程图 -->
    <div class="card">
      <div class="card-title"><span class="icon">◈</span>系统架构数据流</div>
      <div class="flow-diagram">
        <div class="flow-steps">
          <div class="flow-step primary">用户端<br><small>Browser / SDK</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">Nginx<br><small>:80 / :443</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">React 前端<br><small>静态资源</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step primary">ragflow_server<br><small>Quart :9380</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">数据层<br><small>MySQL / Redis / MinIO / ES</small></div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">task_executor<br><small>异步 Worker</small></div>
        </div>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>请求路由：</strong>Nginx 同时托管 React 静态资源与 <code>/v1/*</code> API 反向代理。ragflow_server 基于 Quart（异步 Flask）处理 API 请求，通过 Redis Streams 下发任务给异步 Worker，结果写入 MySQL + 向量引擎。
      </div>
    </div>

    <!-- Docker 服务矩阵 + 核心技术栈 -->
    <div class="two-col">
      <!-- Docker 服务矩阵 -->
      <div class="card">
        <div class="card-title"><span class="icon">🐳</span> Docker 服务矩阵</div>
        <table class="data-table">
          <thead>
            <tr><th>服务</th><th>镜像</th><th>角色</th><th>Profile</th></tr>
          </thead>
          <tbody>
            <tr v-for="s in dockerServices" :key="s.name">
              <td><strong>{{ s.name }}</strong></td>
              <td><code>{{ s.image }}</code></td>
              <td>{{ s.role }}</td>
              <td><code>{{ s.profile }}</code></td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 核心技术栈 -->
      <div class="card">
        <div class="card-title"><span class="icon">⚡</span> 核心技术栈</div>
        <table class="data-table">
          <thead>
            <tr><th>层次</th><th>技术</th></tr>
          </thead>
          <tbody>
            <tr v-for="t in techStack" :key="t.layer">
              <td><strong>{{ t.layer }}</strong></td>
              <td>{{ t.tech }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 架构亮点 -->
    <div class="card">
      <div class="card-title"><span class="icon">✨</span> 架构亮点</div>
      <div class="two-col">
        <ul class="feature-list">
          <li v-for="f in highlights.slice(0, 3)" :key="f">{{ f }}</li>
        </ul>
        <ul class="feature-list">
          <li v-for="f in highlights.slice(3)" :key="f">{{ f }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 核心指标卡片
const metrics = ref([
  { value: '9', label: 'Docker 服务' },
  { value: '35+', label: 'Embedding 提供商' },
  { value: '15', label: '分块策略' },
  { value: '6', label: 'PDF 解析策略' },
  { value: '4', label: '向量引擎' },
  { value: '18+', label: 'Rerank 提供商' }
])

// Docker 服务矩阵
const dockerServices = ref([
  { name: 'ragflow', image: 'infiniflow/ragflow:v0.24.0', role: '主应用', profile: 'cpu / gpu' },
  { name: 'mysql', image: 'mysql:8.0.39', role: '关系数据库', profile: 'always' },
  { name: 'minio', image: 'minio:RELEASE.2025-06-13', role: '对象存储', profile: 'always' },
  { name: 'redis', image: 'valkey/valkey:8', role: '任务队列/缓存', profile: 'always' },
  { name: 'es01', image: 'elasticsearch:8.11.3', role: '向量+全文检索', profile: 'elasticsearch' },
  { name: 'infinity', image: 'infiniflow/infinity:v0.7.0-dev2', role: '替代向量引擎', profile: 'infinity' },
  { name: 'oceanbase', image: 'oceanbase/oceanbase-ce:4.4.1.0', role: '替代向量引擎', profile: 'oceanbase' },
  { name: 'opensearch', image: 'opensearch:2.19.1', role: '替代向量引擎', profile: 'opensearch' },
  { name: 'tei', image: 'text-embeddings-inference', role: '本地 Embedding 服务', profile: 'tei-cpu / tei-gpu' }
])

// 核心技术栈
const techStack = ref([
  { layer: '后端框架', tech: 'Python 3.10+, Flask / Quart' },
  { layer: '前端框架', tech: 'TypeScript, React, UmiJS' },
  { layer: 'ORM', tech: 'Peewee（连接池）' },
  { layer: '任务队列', tech: 'Redis Streams（Consumer Group）' },
  { layer: '向量引擎', tech: 'Elasticsearch KNN / Infinity / OpenSearch / OceanBase' },
  { layer: '文档解析', tech: 'ONNX Runtime（自定义模型）+ PaddleOCR' },
  { layer: 'Embedding', tech: '35+ 提供商, tiktoken（cl100k_base）' }
])

// 架构亮点
const highlights = ref([
  '多引擎向量存储 — 同时支持 Elasticsearch KNN、Infinity、OpenSearch、OceanBase 四种向量引擎，用户可按需切换',
  '丰富 Embedding 生态 — 35+ 嵌入提供商（OpenAI、Cohere、本地模型等），tiktoken cl100k_base 统一分词',
  '深度文档解析 — 6 种 PDF 解析策略 + ONNX Runtime 自定义模型 + PaddleOCR，精准提取表格/图片/公式',
  '异步任务架构 — Redis Streams Consumer Group 驱动 task_executor，支持文档解析/向量化的高并发处理',
  '灵活 Docker Profile — 通过 cpu/gpu/elasticsearch/infinity 等 Profile 按需组合服务，降低部署门槛',
  '本地 Embedding 加速 — 内置 TEI（Text Embeddings Inference）容器，零外部依赖即可运行本地嵌入模型'
])
</script>
