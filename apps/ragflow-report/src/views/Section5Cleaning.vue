<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§5 格式转换与数据清洗</h2>
      <p>RAGFlow 7 阶段数据清洗流水线 — 从编码检测到 NLP 预处理</p>
    </div>

    <!-- 7 阶段流水线流程图 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚙</span> 7 阶段数据清洗流水线</div>
      <div class="flow-diagram">
        <div class="flow-steps">
          <div
            v-for="(stage, idx) in pipelineStages"
            :key="stage.id"
            class="flow-step-wrapper"
          >
            <div class="flow-step" :class="stage.cls">
              <div class="flow-step-num">Stage {{ stage.id }}</div>
              <div class="flow-step-name">{{ stage.name }}</div>
            </div>
            <div v-if="idx < pipelineStages.length - 1" class="flow-arrow">→</div>
          </div>
        </div>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>流水线设计：</strong>原始文档依次经过编码检测 → 文本规范化 → 噪声移除 → 表格结构化 → 图片处理 → 语言检测 → NLP 预处理，最终输出可用于向量化的干净文本块。每个阶段独立可配置，支持按需跳过。
      </div>
    </div>

    <!-- 各阶段详情 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔍</span> 各阶段详情</div>
      <table class="data-table">
        <thead>
          <tr><th>阶段</th><th>名称</th><th>核心逻辑</th></tr>
        </thead>
        <tbody>
          <tr v-for="s in stageDetails" :key="s.stage">
            <td><strong>{{ s.stage }}</strong></td>
            <td>{{ s.name }}</td>
            <td>{{ s.detail }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 优劣势分析 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚖</span> 优劣势分析</div>
      <div class="pros-cons-grid">
        <div class="pros-col">
          <div class="pros-col-title">优势</div>
          <ul class="feature-list">
            <li v-for="p in pros" :key="p">{{ p }}</li>
          </ul>
        </div>
        <div class="cons-col">
          <div class="cons-col-title">不足</div>
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

// 流水线阶段（流程图用）
const pipelineStages = ref([
  { id: 1, name: '编码检测', cls: 'primary' },
  { id: 2, name: '文本规范化', cls: '' },
  { id: 3, name: '噪声移除', cls: '' },
  { id: 4, name: '表格结构化', cls: 'primary' },
  { id: 5, name: '图片处理', cls: '' },
  { id: 6, name: '语言检测', cls: '' },
  { id: 7, name: 'NLP 预处理', cls: 'primary' }
])

// 各阶段详细说明
const stageDetails = ref([
  {
    stage: '1',
    name: '编码检测',
    detail: '使用 chardet 库检测文件编码（confidence > 0.5），支持 60+ 种编码格式自动识别与解码'
  },
  {
    stage: '2',
    name: '文本规范化',
    detail: '全角→半角转换（strQ2B）、繁体→简体（tradi2simp）、\\u3000→普通空格、多余空格移除'
  },
  {
    stage: '3',
    name: '噪声移除',
    detail: 'HTML style/script/注释标签移除、控制字符（\\x00-\\x1f）清除、目录结构移除（remove_contents_table）'
  },
  {
    stage: '4',
    name: '表格结构化',
    detail: '支持 HTML <table> 及自然语言表格；单元格类型自动分类（日期/数字/文本/姓名），双格式输出'
  },
  {
    stage: '5',
    name: '图片处理',
    detail: '提取文档图片 → 竖向拼接 → JPEG 压缩 → MinIO 存储；可选 Vision LLM 生成图片描述'
  },
  {
    stage: '6',
    name: '语言检测',
    detail: 'is_english：ASCII 字符占比 > 80%；is_chinese：CJK 字符占比 > 20%；中英文混合文档自动识别'
  },
  {
    stage: '7',
    name: 'NLP 预处理',
    detail: 'rag_tokenizer 自定义分词、26 个停用词过滤、synonym.json + WordNet 同义词扩展'
  }
])

// 优势
const pros = ref([
  'chardet + 60 种编码兜底，覆盖绝大多数文件来源',
  '中英文自动检测，按语言选择不同处理策略',
  '目录移除 + HTML 清理，有效降低文档噪声',
  'xxhash 生成 chunk ID，快速且唯一',
  '双格式表格输出（结构化 + 自然语言），适配不同检索场景'
])

// 不足
const cons = ref([
  '极端编码（罕见语种/混合编码）可能检测失败',
  '小语种（日/韩/泰等）语言检测能力不足',
  '缺少通用样板（boilerplate）检测模块',
  '无文档级去重机制，重复内容会冗余入库',
  '复杂合并单元格表格可能丢失部分信息'
])
</script>
