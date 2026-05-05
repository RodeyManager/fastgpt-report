<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§13 AI 智能体编排</h2>
      <p>在一体化平台中构建强大的智能体，通过可视化工作流无缝集成 RAG、工具和 MCP。</p>
    </div>

    <!-- Agent 中心辐射架构 -->
    <div class="card">
      <div class="card-title"><span class="icon">🤖</span>智能体中心辐射架构</div>
      <div class="flow-diagram" style="padding:40px 28px;">
        <!-- 用户意图输入 -->
        <div style="display:flex; flex-direction:column; align-items:center; gap:0;">
          <div class="flow-step" style="min-width:160px;">
            💬 用户意图<br><small>自然语言指令</small>
          </div>
          <div style="width:2px; height:28px; background:rgba(16,185,129,0.5);"></div>

          <!-- 中心 Agent -->
          <div
            class="flow-step primary"
            style="
              min-width:200px; padding:20px 28px;
              border:2px solid #10b981;
              border-radius:16px;
              font-size:1rem;
              box-shadow: 0 0 20px rgba(16,185,129,0.3);
            "
          >
            🧠 AI Agent<br>
            <small>自主规划 + 推理引擎</small><br>
            <small>可视化工作流编排</small>
          </div>

          <!-- 辐射连接线 + 工具节点 -->
          <div style="margin-top:8px; width:100%; max-width:700px;">
            <!-- 上方连接横线 -->
            <div style="display:flex; justify-content:center; margin-bottom:0;">
              <div style="width:80%; height:2px; background:rgba(16,185,129,0.3);"></div>
            </div>
          </div>

          <!-- 四个工具节点 -->
          <div style="display:flex; gap:16px; align-items:flex-start; justify-content:center; flex-wrap:wrap; margin-top:0;">
            <!-- RAG 检索 -->
            <div style="display:flex; flex-direction:column; align-items:center; gap:0;">
              <div style="width:2px; height:20px; background:rgba(16,185,129,0.4);"></div>
              <div class="flow-step" style="min-width:140px; border-color:rgba(16,185,129,0.5);">
                📚 RAG 检索<br><small>知识库查询</small><br><small>混合检索 + Rerank</small>
              </div>
            </div>
            <!-- Tool 调用 -->
            <div style="display:flex; flex-direction:column; align-items:center; gap:0;">
              <div style="width:2px; height:20px; background:rgba(245,158,11,0.4);"></div>
              <div class="flow-step" style="min-width:140px; border-color:rgba(245,158,11,0.5); background:rgba(245,158,11,0.08);">
                🔧 Tool 调用<br><small>外部 API</small><br><small>天气/搜索/数据库</small>
              </div>
            </div>
            <!-- MCP 协议 -->
            <div style="display:flex; flex-direction:column; align-items:center; gap:0;">
              <div style="width:2px; height:20px; background:rgba(20,184,166,0.4);"></div>
              <div class="flow-step" style="min-width:140px; border-color:rgba(20,184,166,0.5); background:rgba(20,184,166,0.08);">
                🔗 MCP 协议<br><small>工具链集成</small><br><small>标准化工具调用</small>
              </div>
            </div>
            <!-- 代码执行 -->
            <div style="display:flex; flex-direction:column; align-items:center; gap:0;">
              <div style="width:2px; height:20px; background:rgba(239,68,68,0.4);"></div>
              <div class="flow-step" style="min-width:140px; border-color:rgba(239,68,68,0.3); background:rgba(239,68,68,0.06);">
                💻 代码执行<br><small>沙箱环境</small><br><small>安全隔离运行</small>
              </div>
            </div>
          </div>

          <!-- 合并到结果整合 -->
          <div style="margin-top:8px; width:100%; max-width:700px;">
            <div style="display:flex; justify-content:center;">
              <div style="width:80%; height:2px; background:rgba(16,185,129,0.3);"></div>
            </div>
          </div>
          <div style="display:flex; flex-direction:column; align-items:center; gap:0;">
            <div style="width:2px; height:20px; background:rgba(16,185,129,0.4);"></div>
            <div class="flow-step" style="min-width:160px;">
              🔄 结果整合<br><small>多源信息聚合</small>
            </div>
            <div style="width:2px; height:20px; background:rgba(16,185,129,0.5);"></div>
            <div class="flow-step" style="min-width:160px;">
              ✨ LLM 生成<br><small>上下文推理 + 回答</small>
            </div>
            <div style="width:2px; height:20px; background:rgba(16,185,129,0.5);"></div>
            <div class="flow-step primary" style="min-width:160px;">
              📤 最终回答<br><small>结构化输出</small>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Agent 核心能力 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚡</span>智能体核心能力</div>
      <div class="three-col">
        <div v-for="cap in capabilities" :key="cap.title" class="metric-card" style="text-align:left; padding:20px;">
          <div style="font-size:1.6rem; margin-bottom:8px;">{{ cap.icon }}</div>
          <div style="font-weight:600; color:#fff; margin-bottom:6px;">{{ cap.title }}</div>
          <div style="font-size:0.82rem; color:var(--text-secondary);">{{ cap.desc }}</div>
        </div>
      </div>
    </div>

    <!-- 可视化工作流 + 工具生态 -->
    <div class="two-col">
      <div class="card">
        <div class="card-title"><span class="icon">🎯</span>可视化工作流编排</div>
        <ul class="feature-list">
          <li v-for="f in workflowFeatures" :key="f">{{ f }}</li>
        </ul>
      </div>
      <div class="card">
        <div class="card-title"><span class="icon">🔌</span>工具集成生态</div>
        <ul class="feature-list">
          <li v-for="t in toolIntegration" :key="t">{{ t }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 核心能力
const capabilities = ref([
  { icon: '🎯', title: '自主规划与推理', desc: 'Agent 自动分解任务、制定执行计划，根据中间结果动态调整策略' },
  { icon: '💬', title: '多轮对话管理', desc: '维护完整对话上下文，支持追问、纠偏和意图澄清' },
  { icon: '📚', title: 'RAG 知识库集成', desc: '无缝对接混合检索引擎，从企业知识库获取精准上下文' },
  { icon: '🔗', title: 'MCP 协议支持', desc: '标准化工具调用协议，一键接入外部工具和服务生态' },
  { icon: '💻', title: '代码沙箱执行', desc: '安全隔离环境中运行用户代码，支持数据分析与可视化' },
  { icon: '🤝', title: '多 Agent 协作', desc: '多个专业 Agent 分工协作，复杂任务自动路由与协调' }
])

// 工作流特性
const workflowFeatures = ref([
  '拖拽式可视化编排 — 无代码构建复杂工作流',
  '条件分支与循环 — 支持动态路由和迭代逻辑',
  '子流程嵌套 — 可复用的工作流模块',
  '实时调试预览 — 执行过程可视化追踪',
  '版本管理 — 工作流变更可追溯可回滚',
  '模板市场 — 丰富的预置工作流模板'
])

// 工具集成
const toolIntegration = ref([
  'HTTP 工具 — 任意 REST API 调用',
  '数据库工具 — MySQL / PostgreSQL 查询',
  '搜索引擎 — Google / Bing / 内部搜索',
  '天气 API — 实时天气数据获取',
  'MCP 工具链 — 标准化工具发现与调用',
  '自定义工具 — 用户可注册自定义工具函数',
  '代码执行器 — Python / JavaScript 沙箱'
])
</script>
