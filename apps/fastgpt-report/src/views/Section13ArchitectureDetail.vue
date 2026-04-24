<template>
  <div class="section-page">
    <div class="section-header">
      <h2>FastGPT 项目架构图</h2>
      <p>完整的 FastGPT 系统分层架构，涵盖前端、核心服务、业务包、工作线程、任务队列、数据存储与外部插件</p>
    </div>

    <div class="card">
      <div class="card-title">系统分层架构</div>
      <div class="arch-container">

        <!-- LAYER 1: 前端层 -->
        <div class="arch-layer">
          <div class="arch-layer-title">前端层 (Frontend)</div>
          <div class="arch-modules">
            <div class="arch-module">
              <div class="mod-name">Next.js App</div>
              <div class="mod-desc">projects/app - SSR页面 + API路由</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">Marketplace</div>
              <div class="mod-desc">projects/marketplace - 插件市场</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">React Flow</div>
              <div class="mod-desc">工作流可视化编辑器</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">Chakra UI</div>
              <div class="mod-desc">组件库</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">Zustand</div>
              <div class="mod-desc">状态管理</div>
            </div>
          </div>
        </div>

        <div class="arch-arrow">↓</div>

        <!-- LAYER 2: 核心服务层 -->
        <div class="arch-layer">
          <div class="arch-layer-title">核心服务层 (Core Services)</div>
          <div class="arch-modules">
            <div class="arch-module">
              <div class="mod-name">FastGPT App (:3000)</div>
              <div class="mod-desc">主应用服务</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">Plugin Service</div>
              <div class="mod-desc">插件执行服务</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">Code Sandbox (Bun)</div>
              <div class="mod-desc">代码沙箱隔离执行</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">MCP Server</div>
              <div class="mod-desc">MCP协议服务</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">Volume Manager (Bun)</div>
              <div class="mod-desc">Docker卷管理</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">AI Proxy</div>
              <div class="mod-desc">多模型网关</div>
            </div>
          </div>
        </div>

        <div class="arch-arrow">↓</div>

        <!-- LAYER 3: 业务逻辑层 -->
        <div class="arch-layer">
          <div class="arch-layer-title">业务逻辑层 (Packages)</div>
          <div class="arch-modules">
            <div class="arch-module">
              <div class="mod-name">@fastgpt/global</div>
              <div class="mod-desc">共享类型定义(纯TS, 无服务端依赖)</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">@fastgpt/service</div>
              <div class="mod-desc">后端业务逻辑</div>
              <div class="mod-desc">core/ai · core/workflow · core/dataset · core/app · core/chat · worker/</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">@fastgpt/web</div>
              <div class="mod-desc">共享UI组件(20+自定义Hooks)</div>
            </div>
          </div>
        </div>

        <div class="arch-arrow">↓</div>

        <!-- LAYER 4: 工作线程 -->
        <div class="arch-layer">
          <div class="arch-layer-title">工作线程 (Worker Threads)</div>
          <div class="arch-modules">
            <div class="arch-module">
              <div class="mod-name">readFile</div>
              <div class="mod-desc">文件解析(PDF/DOCX/PPTX/CSV/XLSX/HTML)</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">text2Chunks</div>
              <div class="mod-desc">文本分块</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">htmlStr2Md</div>
              <div class="mod-desc">HTML转Markdown</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">countTokens</div>
              <div class="mod-desc">Token计数</div>
            </div>
          </div>
        </div>

        <div class="arch-arrow">↓</div>

        <!-- LAYER 5: 任务队列 -->
        <div class="arch-layer">
          <div class="arch-layer-title">任务队列 (BullMQ)</div>
          <div class="arch-modules">
            <div class="arch-module">
              <div class="mod-name">datasetSync</div>
              <div class="mod-desc">数据集同步</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">training</div>
              <div class="mod-desc">训练任务</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">s3FileDelete</div>
              <div class="mod-desc">S3文件清理</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">appDelete</div>
              <div class="mod-desc">应用删除</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">teamDelete</div>
              <div class="mod-desc">团队删除</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">evaluation</div>
              <div class="mod-desc">评测任务</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">wechatPoll</div>
              <div class="mod-desc">微信轮询</div>
            </div>
          </div>
        </div>

        <div class="arch-arrow">↓</div>

        <!-- LAYER 6: 数据存储层 -->
        <div class="arch-layer">
          <div class="arch-layer-title">数据存储层 (Storage)</div>
          <div class="arch-modules">
            <div class="arch-module">
              <div class="mod-name">MongoDB (mongoose)</div>
              <div class="mod-desc">41个集合, 全文检索, 灵活Schema</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">PostgreSQL + pgvector</div>
              <div class="mod-desc">向量存储, HNSW索引</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">Redis (ioredis)</div>
              <div class="mod-desc">会话/缓存/队列/限流/SSE恢复</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">MinIO / S3</div>
              <div class="mod-desc">文件存储(多厂商: AWS/COS/OSS)</div>
            </div>
          </div>
        </div>

        <div class="arch-arrow">↓</div>

        <!-- LAYER 7: 外部插件 -->
        <div class="arch-layer">
          <div class="arch-layer-title">外部插件 (Plugins)</div>
          <div class="arch-modules">
            <div class="arch-module">
              <div class="mod-name">OCR (Surya)</div>
              <div class="mod-desc">图像文字识别</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">PDF-Marker</div>
              <div class="mod-desc">PDF标注处理</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">PDF-MinerU</div>
              <div class="mod-desc">PDF深度解析</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">Rerank-BGE</div>
              <div class="mod-desc">重排序模型</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">STT-SenseVoice</div>
              <div class="mod-desc">语音识别</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">TTS-CoseVoice</div>
              <div class="mod-desc">语音合成</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">Web Crawler</div>
              <div class="mod-desc">Puppeteer网页抓取</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">SearXNG</div>
              <div class="mod-desc">聚合搜索引擎</div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- RAG Data Flow -->
    <div class="card">
      <div class="card-title">RAG 数据流</div>
      <div class="flow-diagram">
        <div class="flow-steps">
          <div class="flow-step primary">用户上传文件</div><span class="flow-arrow">→</span>
          <div class="flow-step">S3存储</div><span class="flow-arrow">→</span>
          <div class="flow-step">Worker解析</div><span class="flow-arrow">→</span>
          <div class="flow-step">MongoDB原文</div><span class="flow-arrow">→</span>
          <div class="flow-step">文本分块</div><span class="flow-arrow">→</span>
          <div class="flow-step primary">Embedding API</div><span class="flow-arrow">→</span>
          <div class="flow-step">PG向量存储</div>
        </div>
        <div class="flow-steps" style="margin-top:12px;">
          <div class="flow-step">查询向量化</div><span class="flow-arrow">→</span>
          <div class="flow-step primary">双路检索+RRF</div><span class="flow-arrow">→</span>
          <div class="flow-step">可选Rerank</div><span class="flow-arrow">→</span>
          <div class="flow-step" style="background:rgba(16,185,129,0.15);border-color:var(--accent-green);">✓ 结果返回</div>
        </div>
      </div>
    </div>

    <!-- Deployment Architecture -->
    <div class="card">
      <div class="card-title">Docker 部署架构</div>
      <div class="arch-container">
        <div class="arch-layer">
          <div class="arch-layer-title">Docker Networks</div>
          <div class="arch-modules">
            <div class="arch-module">
              <div class="mod-name">data</div>
              <div class="mod-desc">FastGPT App ↔ MongoDB / Redis / MinIO / PostgreSQL</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">app</div>
              <div class="mod-desc">FastGPT ↔ Plugin Service ↔ MCP Server</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">codesandbox</div>
              <div class="mod-desc">Code Sandbox ↔ FastGPT App</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">aiproxy</div>
              <div class="mod-desc">AI Proxy ↔ PostgreSQL</div>
            </div>
            <div class="arch-module">
              <div class="mod-name">opensandbox</div>
              <div class="mod-desc">Code Sandbox ↔ Volume Manager</div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
