<template>
  <div class="section-page">
    <div class="section-header">
      <h2>训练模式与AI模型</h2>
      <p>AI驱动的知识处理管道</p>
    </div>

    <!-- Tab 导航 -->
    <div class="tab-nav">
      <button
        v-for="(tab, index) in tabs"
        :key="index"
        :class="['tab-btn', { active: activeTab === index }]"
        @click="activeTab = index"
      >{{ tab }}</button>
    </div>

    <!-- Tab 内容区域 -->
    <!-- Tab 0: 概述 -->
    <div class="tab-content" v-show="activeTab === 0">
      <div class="card highlight-card">
        <div class="card-title">
          <span class="title-icon" style="background:rgba(0,212,255,0.15);color:#06b6d4">⚡</span>
          核心定位
        </div>
        <p class="highlight-desc">
          FastGPT 训练队列是 RAG 数据处理管道的<strong class="text-primary">核心基础设施</strong>。负责将原始文档经
          <span class="tag cyan">解析</span>→
          <span class="tag purple">分块</span>→
          <span class="tag blue">LLM处理</span>→
          <span class="tag green">向量化</span>→
          <span class="tag orange">存储</span>
          的完整流水线，转化为可语义检索的知识库数据。
        </p>
      </div>

      <div class="mode-grid">
        <div class="mode-card">
          <div class="mode-icon" style="background:rgba(79,143,255,0.12);color:#4f8fff">🗄</div>
          <div class="mode-name">MongoDB 原子操作</div>
          <div class="mode-desc">采用 MongoDB 原子操作驱动的分布式任务队列架构，通过 findOneAndUpdate 实现任务抢占</div>
        </div>
        <div class="mode-card">
          <div class="mode-icon" style="background:rgba(168,85,247,0.12);color:#a855f7">🚫</div>
          <div class="mode-name">零外部依赖</div>
          <div class="mode-desc">无需外部消息中间件（Redis / RabbitMQ），所有调度逻辑基于 MongoDB 原生能力</div>
        </div>
        <div class="mode-card">
          <div class="mode-icon" style="background:rgba(0,212,255,0.12);color:#06b6d4">🔄</div>
          <div class="mode-name">原子抢占</div>
          <div class="mode-desc">findOneAndUpdate 单操作完成查询 + 锁定，天然防止任务被重复消费</div>
        </div>
        <div class="mode-card">
          <div class="mode-icon" style="background:rgba(34,197,94,0.12);color:#10b981">📡</div>
          <div class="mode-name">实时响应</div>
          <div class="mode-desc">Change Stream 监听 insert 事件实现毫秒级实时调度响应</div>
        </div>
      </div>
    </div>

    <!-- Tab 1: 架构 -->
    <div class="tab-content" v-show="activeTab === 1">
      <div class="card" style="padding:28px">
        <div class="card-title">
          <span class="title-icon" style="background:rgba(79,143,255,0.15);color:#4f8fff">🏗</span>
          系统架构管道图
        </div>
        <div class="pipeline">
          <div class="pipeline-node">
            <div class="pn-title">用户操作层</div>
            <div class="pn-desc">文档上传、API调用</div>
          </div>
          <div class="pipeline-arrow">→</div>
          <div class="pipeline-node">
            <div class="pn-title">REST API 层</div>
            <div class="pn-desc">认证、路由、校验</div>
          </div>
          <div class="pipeline-arrow">→</div>
          <div class="pipeline-node" style="border-color:rgba(0,212,255,0.3)">
            <div class="pn-title" style="color:#06b6d4">入队控制器</div>
            <div class="pn-desc">创建训练任务</div>
          </div>
          <div class="pipeline-arrow">→</div>
          <div class="pipeline-node" style="border-color:rgba(168,85,247,0.3);background:rgba(168,85,247,0.06)">
            <div class="pn-title" style="color:#a855f7">MongoDB</div>
            <div class="pn-desc">dataset_trainings</div>
          </div>
          <div class="pipeline-arrow">→</div>
          <div class="pipeline-node" style="border-color:rgba(34,197,94,0.3)">
            <div class="pn-title" style="color:#10b981">Worker 层</div>
            <div class="pn-desc">消费处理任务</div>
          </div>
          <div class="pipeline-arrow">→</div>
          <div class="pipeline-node">
            <div class="pn-title">调度触发层</div>
            <div class="pn-desc">ChangeStream + Cron</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span class="title-icon" style="background:rgba(168,85,247,0.15);color:#a855f7">⚙</span>
          技术选型
        </div>
        <table class="data-table">
          <thead><tr><th>组件</th><th>技术选型</th><th>说明</th></tr></thead>
          <tbody>
            <tr><td>任务存储</td><td><code>MongoDB</code></td><td>利用原子操作实现分布式锁</td></tr>
            <tr><td>任务调度</td><td><code>Change Stream + Cron</code></td><td>双触发机制确保不遗漏</td></tr>
            <tr><td>并发控制</td><td><code>全局计数器</code></td><td>内存级轻量并发限制</td></tr>
            <tr><td>文本处理</td><td><code>LLM</code></td><td>QA 生成、自动摘要</td></tr>
            <tr><td>向量化</td><td><code>Embedding Model</code></td><td>文本向量生成</td></tr>
            <tr><td>向量存储</td><td><code>向量数据库</code></td><td>语义检索</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Tab 2: 数据模型 -->
    <div class="tab-content" v-show="activeTab === 2">
      <div class="card">
        <div class="card-title">
          <span class="title-icon" style="background:rgba(0,212,255,0.15);color:#06b6d4">📋</span>
          集合字段
        </div>
        <div class="field-list">
          <div class="field-item"><span class="field-name">teamId</span><span class="field-type">ObjectId</span><span class="field-desc">团队ID</span></div>
          <div class="field-item"><span class="field-name">tmbId</span><span class="field-type">ObjectId</span><span class="field-desc">团队成员ID</span></div>
          <div class="field-item"><span class="field-name">datasetId</span><span class="field-type">ObjectId</span><span class="field-desc">知识库ID</span></div>
          <div class="field-item"><span class="field-name">collectionId</span><span class="field-type">ObjectId</span><span class="field-desc">文档集合ID</span></div>
          <div class="field-item"><span class="field-name">mode</span><span class="field-type">String/Enum</span><span class="field-desc">训练模式：parse / chunk / qa / auto / image / imageParse</span></div>
          <div class="field-item"><span class="field-name">lockTime</span><span class="field-type">Date</span><span class="field-desc">锁定时间（用于任务抢占）</span></div>
          <div class="field-item"><span class="field-name">retryCount</span><span class="field-type">Number (5)</span><span class="field-desc">剩余重试次数</span></div>
          <div class="field-item"><span class="field-name">weight</span><span class="field-type">Number (0)</span><span class="field-desc">优先级权重</span></div>
          <div class="field-item"><span class="field-name">q</span><span class="field-type">String</span><span class="field-desc">问题/分块文本</span></div>
          <div class="field-item"><span class="field-name">a</span><span class="field-type">String</span><span class="field-desc">答案/补充文本</span></div>
          <div class="field-item"><span class="field-name">chunkIndex</span><span class="field-type">Number</span><span class="field-desc">分块索引</span></div>
          <div class="field-item"><span class="field-name">indexSize</span><span class="field-type">Number</span><span class="field-desc">索引大小</span></div>
          <div class="field-item"><span class="field-name">dataId</span><span class="field-type">ObjectId</span><span class="field-desc">关联数据ID（重建场景）</span></div>
          <div class="field-item"><span class="field-name">indexes</span><span class="field-type">Array</span><span class="field-desc">自定义索引</span></div>
          <div class="field-item"><span class="field-name">errorMsg</span><span class="field-type">String</span><span class="field-desc">错误信息</span></div>
          <div class="field-item"><span class="field-name">expireAt</span><span class="field-type">Date</span><span class="field-desc">7天 TTL 自动过期</span></div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span class="title-icon" style="background:rgba(168,85,247,0.15);color:#a855f7">🔍</span>
          索引设计
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:8px">
          <div class="index-badge">{ <span style="color:#06b6d4">teamId</span>: 1, <span style="color:#06b6d4">datasetId</span>: 1 } <span class="tag blue" style="margin-left:8px">团队+知识库查询</span></div>
          <div class="index-badge">{ <span style="color:#06b6d4">mode</span>: 1, <span style="color:#06b6d4">retryCount</span>: 1, <span style="color:#06b6d4">lockTime</span>: 1, <span style="color:#06b6d4">weight</span>: -1 } <span class="tag green" style="margin-left:8px">任务抢占核心索引</span></div>
          <div class="index-badge">{ <span style="color:#06b6d4">expireAt</span>: 1 } TTL 7天 <span class="tag purple" style="margin-left:8px">自动过期清理</span></div>
        </div>
      </div>
    </div>

    <!-- Tab 3: 训练模式 — 原有内容集中于此 -->
    <div class="tab-content" v-show="activeTab === 3">
      <!-- 训练模式 -->
      <div class="card">
        <h3>训练模式</h3>
        <table class="data-table">
          <thead><tr><th>模式</th><th>枚举值</th><th>AI模型</th><th>描述</th></tr></thead>
          <tbody>
            <tr><td>解析</td><td><code>parse</code></td><td><span class="tag agent">agentModel</span></td><td>读取源文件,提取文本,分块</td></tr>
            <tr><td>分块</td><td><code>chunk</code></td><td><span class="tag vector">vectorModel</span></td><td>直接对文本块向量化</td></tr>
            <tr><td>问答</td><td><code>qa</code></td><td><span class="tag agent">agentModel</span></td><td>LLM生成问答对(每段最多50对)</td></tr>
            <tr><td>自动</td><td><code>auto</code></td><td><span class="tag agent">agentModel</span></td><td>AI自动生成自定义索引</td></tr>
            <tr><td>图片</td><td><code>image</code></td><td><span class="tag vlm">vlmModel</span></td><td>VLM描述图片并索引</td></tr>
            <tr><td>图片解析</td><td><code>imageParse</code></td><td><span class="tag vlm">vlmModel</span></td><td>VLM处理完整图片内容</td></tr>
          </tbody>
        </table>
      </div>

      <!-- QA生成流程 -->
      <div class="card">
        <h3>QA生成流程</h3>
        <div class="qa-flow-wrapper">
          <!-- 主流程 -->
          <div class="qa-flow-main">
            <div class="qa-node">
              <div class="qa-node-label">文本块</div>
              <div class="qa-node-sub">原始 Chunk</div>
            </div>
            <div class="qa-arrow">→</div>
            <div class="qa-node qa-node-primary">
              <div class="qa-node-label">LLM 生成</div>
              <div class="qa-node-sub">Prompt_AgentQA<br/>temperature=0.3</div>
            </div>
            <div class="qa-arrow">→</div>
            <div class="qa-node qa-node-primary">
              <div class="qa-node-label">正则解析</div>
              <div class="qa-node-sub">Q₁:/A₁: 格式提取</div>
            </div>
            <div class="qa-arrow">→</div>
            <div class="qa-node qa-node-success">
              <div class="qa-node-label">问答对</div>
              <div class="qa-node-sub">最多 50 组 Q&amp;A</div>
            </div>
            <div class="qa-arrow">→</div>
            <div class="qa-node qa-node-success">
              <div class="qa-node-label">入队训练</div>
              <div class="qa-node-sub">mode=chunk 向量化</div>
            </div>
          </div>
          <!-- 失败回退分支 -->
          <div class="qa-flow-fallback">
            <div class="qa-branch-left">
              <div class="qa-branch-label">✅ 解析成功</div>
              <div class="qa-branch-desc">LLM 返回有效 Q&amp;A 对 → 走主流程</div>
            </div>
            <div class="qa-branch-divider"></div>
            <div class="qa-branch-right">
              <div class="qa-branch-label qa-branch-warn">⚠️ 解析失败（返回为空）</div>
              <div class="qa-branch-desc">
                回退策略：跳过 LLM 结果，直接将原始 Chunk 文本按 <code>text2Chunks()</code> 切分后以 <strong>chunk 模式</strong>重新入队
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 模型使用图表 -->
      <div class="card">
        <h3>训练模式 × AI模型映射</h3>
        <div id="chart-training-models" style="height:260px"></div>
      </div>

      <!-- AI模型类型 -->
      <div class="card">
        <h3>AI模型类型</h3>
        <table class="data-table">
          <thead><tr><th>类型</th><th>默认模型</th><th>关键特性</th></tr></thead>
          <tbody>
            <tr><td>LLM</td><td><code>gpt-5</code></td><td>maxContext=16000, toolChoice, vision, reasoning</td></tr>
            <tr><td>Embedding</td><td><code>text-embedding-3-small</code></td><td>1536维, batchSize, dbConfig/queryConfig</td></tr>
            <tr><td>Rerank</td><td><code>可配置</code></td><td>maxToken=8000, Jina兼容接口</td></tr>
            <tr><td>TTS</td><td><code>可配置</code></td><td>多种语音选项</td></tr>
            <tr><td>STT</td><td><code>whisper-1</code></td><td>语音转文本</td></tr>
          </tbody>
        </table>
      </div>

      <!-- 插件模型服务 -->
      <div class="card">
        <h3>插件模型服务</h3>
        <ul class="feature-list">
          <li><strong>pdf-mineru</strong> — PDF深度解析</li>
          <li><strong>pdf-marker</strong> — PDF标注提取</li>
          <li><strong>pdf-mistral</strong> — Mistral PDF处理</li>
          <li><strong>ocr-surya</strong> — OCR文字识别</li>
          <li><strong>rerank-bge</strong> — BGE重排序</li>
          <li><strong>stt-sensevoice</strong> — 语音识别</li>
          <li><strong>tts-cosevoice</strong> — 语音合成</li>
        </ul>
      </div>

      <!-- 定时任务 -->
      <div class="card">
        <h3>定时任务</h3>
        <ul class="feature-list">
          <li><strong>训练队列处理</strong> — 每1分钟</li>
          <li><strong>过期数据清理</strong> — 每10分钟</li>
          <li><strong>无效数据检查</strong> — 每1小时</li>
          <li><strong>孤儿向量清理</strong> — 定期执行</li>
        </ul>
      </div>
    </div>

    <!-- Tab 4: 调度 -->
    <div class="tab-content" v-show="activeTab === 4">
      <div class="dual-trigger">
        <div class="trigger-card" style="border-color:rgba(0,212,255,0.2)">
          <div class="tc-badge" style="background:rgba(0,212,255,0.1);color:#06b6d4">触发器一</div>
          <div class="tc-title">MongoDB Change Stream</div>
          <div style="font-size:12px;color:#06b6d4;margin-bottom:12px;font-weight:600">实时响应</div>
          <ul class="trigger-list">
            <li>基于 Replica Set 的 Oplog 实时监听</li>
            <li>insert 事件发生时立即触发对应 Worker</li>
            <li>延迟极低（<strong class="text-primary">毫秒级</strong>）</li>
            <li>实现真正的实时响应式调度</li>
          </ul>
        </div>
        <div class="trigger-card" style="border-color:rgba(168,85,247,0.2)">
          <div class="tc-badge" style="background:rgba(168,85,247,0.1);color:#a855f7">触发器二</div>
          <div class="tc-title">Cron 定时任务</div>
          <div style="font-size:12px;color:#a855f7;margin-bottom:12px;font-weight:600">兜底保障</div>
          <ul class="trigger-list">
            <li>每分钟执行一次 <code>startTrainingQueue()</code></li>
            <li>确保遗漏任务被重新拾取</li>
            <li>覆盖 Change Stream 断连场景</li>
            <li>双重保障机制提高可靠性</li>
          </ul>
        </div>
      </div>

      <div class="trigger-card" style="border-color:rgba(34,197,94,0.2);margin-top:20px">
        <div class="tc-badge" style="background:rgba(34,197,94,0.1);color:#10b981">触发器三</div>
        <div class="tc-title">系统启动初始化</div>
        <ul class="trigger-list">
          <li><code>startTrainingQueue(true)</code> 批量启动所有 Worker</li>
          <li>解决服务重启后任务积压问题</li>
          <li>确保系统启动后立即进入正常工作状态</li>
        </ul>
      </div>
    </div>

    <!-- Tab 5: 并发 -->
    <div class="tab-content" v-show="activeTab === 5">
      <div class="card">
        <div class="card-title">
          <span class="title-icon" style="background:rgba(79,143,255,0.15);color:#4f8fff">🔐</span>
          原子任务抢占
        </div>
        <div class="code-block"><pre><span class="cm">// 原子操作：查询 + 锁定 + 递减，一步完成</span>
<span class="kw">findOneAndUpdate</span>({
  <span class="str">mode</span>: <span class="str">'chunk'</span>,
  <span class="str">retryCount</span>: { <span class="op">$gt</span>: <span class="num">0</span> },
  <span class="str">lockTime</span>: { <span class="op">$lte</span>: <span class="fn">now</span>() - <span class="num">3</span>min }
}, {
  <span class="str">lockTime</span>: <span class="kw">new</span> <span class="fn">Date</span>(),
  <span class="op">$inc</span>: { <span class="str">retryCount</span>: <span class="num">-1</span> }
})</pre></div>
        <p style="font-size:13px;color:#94a3b8;line-height:1.8;margin-top:16px">
          <strong class="text-primary">核心机制：</strong>findOneAndUpdate 作为原子操作，在单个数据库调用中完成"查找可用任务 → 锁定 → 扣减重试次数"三步操作，
          天然避免了多 Worker 间的竞态条件，无需额外的分布式锁。
        </p>
      </div>

      <div class="card">
        <div class="card-title">
          <span class="title-icon" style="background:rgba(168,85,247,0.15);color:#a855f7">📊</span>
          并发限制配置
        </div>
        <table class="data-table">
          <thead><tr><th>Worker 类型</th><th>全局计数器</th><th>默认上限</th><th>锁定超时</th></tr></thead>
          <tbody>
            <tr><td><span class="tag green">向量化</span></td><td><code>global.vectorQueueLen</code></td><td><strong style="color:#06b6d4">10</strong></td><td>3 分钟</td></tr>
            <tr><td><span class="tag purple">QA 生成</span></td><td><code>global.qaQueueLen</code></td><td><strong style="color:#06b6d4">10</strong></td><td>10 分钟</td></tr>
            <tr><td><span class="tag blue">文档解析</span></td><td><code>global.datasetParseQueueLen</code></td><td><strong style="color:#06b6d4">10</strong></td><td>10 分钟</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Tab 6: 容错 -->
    <div class="tab-content" v-show="activeTab === 6">
      <div class="mode-grid">
        <div class="mode-card">
          <div class="mode-icon" style="background:rgba(245,158,11,0.12);color:#f59e0b">🔄</div>
          <div class="mode-name">5 次自动重试</div>
          <div class="mode-desc">默认 5 次重试机会，通过原子操作 $inc 递减 retryCount，确保计数准确</div>
        </div>
        <div class="mode-card">
          <div class="mode-icon" style="background:rgba(236,72,153,0.12);color:#ec4899">📝</div>
          <div class="mode-name">错误记录</div>
          <div class="mode-desc">失败时记录 errorMsg 字段，用户可在前端查看详细错误信息</div>
        </div>
        <div class="mode-card">
          <div class="mode-icon" style="background:rgba(79,143,255,0.12);color:#4f8fff">👤</div>
          <div class="mode-name">手动重试</div>
          <div class="mode-desc">用户可通过 API 手动重试失败任务，灵活应对异常情况</div>
        </div>
        <div class="mode-card">
          <div class="mode-icon" style="background:rgba(34,197,94,0.12);color:#10b981">🔒</div>
          <div class="mode-name">事务保证</div>
          <div class="mode-desc">MongoDB 事务保证数据一致性，避免部分写入导致的脏数据</div>
        </div>
        <div class="mode-card">
          <div class="mode-icon" style="background:rgba(168,85,247,0.12);color:#a855f7">✂️</div>
          <div class="mode-name">分块事务</div>
          <div class="mode-desc">分批处理避免超时：500 条/批，10,000 条/事务上限</div>
        </div>
        <div class="mode-card">
          <div class="mode-icon" style="background:rgba(0,212,255,0.12);color:#06b6d4">⏰</div>
          <div class="mode-name">TTL 过期</div>
          <div class="mode-desc">7 天 TTL 索引自动过期清理，防止历史任务无限堆积</div>
        </div>
      </div>
    </div>

    <!-- Tab 7: API -->
    <div class="tab-content" v-show="activeTab === 7">
      <div class="card">
        <div class="card-title">
          <span class="title-icon" style="background:rgba(79,143,255,0.15);color:#4f8fff">🔌</span>
          训练队列 API 端点
        </div>
        <table class="data-table">
          <thead><tr><th>路由</th><th>方法</th><th>功能</th><th>权限</th></tr></thead>
          <tbody>
            <tr><td><code>getDatasetTrainingQueue</code></td><td><span class="tag blue">GET</span></td><td>队列计数统计</td><td><span class="tag green">Read</span></td></tr>
            <tr><td><code>trainingDetail</code></td><td><span class="tag blue">GET</span></td><td>训练详细进度</td><td><span class="tag green">Read</span></td></tr>
            <tr><td><code>getTrainingError</code></td><td><span class="tag orange">POST</span></td><td>错误列表（分页）</td><td><span class="tag green">Read</span></td></tr>
            <tr><td><code>updateTrainingData</code></td><td><span class="tag purple">PUT</span></td><td>更新 / 重试</td><td><span class="tag blue">Write</span></td></tr>
            <tr><td><code>deleteTrainingData</code></td><td><span class="tag pink">DELETE</span></td><td>删除训练数据</td><td><span class="tag orange">Manage</span></td></tr>
            <tr><td><code>rebuildEmbedding</code></td><td><span class="tag orange">POST</span></td><td>向量重建</td><td><span class="tag purple">Owner</span></td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="tab-content" v-show="activeTab === 8">
      <div class="card highlight-card">
        <div class="card-title">
          <span class="title-icon" style="background:rgba(245,158,11,0.15);color:#f59e0b">🔄</span>
          重建流程
        </div>
        <div class="flow-steps">
          <div class="flow-step">
            <div class="fs-num">1</div>
            <div class="fs-text">标记所有数据为 <code>rebuilding</code> 状态</div>
          </div>
          <div class="flow-connector"></div>
          <div class="flow-step">
            <div class="fs-num">2</div>
            <div class="fs-text">链式创建重建任务（非批量，避免内存溢出）</div>
          </div>
          <div class="flow-connector"></div>
          <div class="flow-step">
            <div class="fs-num">3</div>
            <div class="fs-text">流式处理，逐步完成向量重建</div>
          </div>
        </div>
      </div>

      <div class="mode-grid">
        <div class="mode-card">
          <div class="mode-icon" style="background:rgba(245,158,11,0.12);color:#f59e0b">🛡</div>
          <div class="mode-name">高容错设计</div>
          <div class="mode-desc">重建任务 retryCount 设为 <strong style="color:#06b6d4">50</strong> 次（对比正常的 5 次），大幅提升容错能力</div>
        </div>
        <div class="mode-card">
          <div class="mode-icon" style="background:rgba(0,212,255,0.12);color:#06b6d4">⛓</div>
          <div class="mode-name">链式触发</div>
          <div class="mode-desc">链式触发避免批量创建大量任务，防止内存溢出和队列阻塞</div>
        </div>
      </div>
    </div>

    <div class="tab-content" v-show="activeTab === 9">
      <!-- RAG 生命周期图 -->
      <div class="card" style="padding:32px">
        <div class="lifecycle">
          <div class="lifecycle-node">知识获取</div>
          <div class="lifecycle-arrow">→</div>
          <div class="lifecycle-node highlight">
            <span>🧠 知识处理</span>
            <small>（训练队列）</small>
          </div>
          <div class="lifecycle-arrow">→</div>
          <div class="lifecycle-node">知识存储</div>
          <div class="lifecycle-arrow">→</div>
          <div class="lifecycle-node">知识检索</div>
        </div>
      </div>

      <!-- 直接影响列表 -->
      <div class="card">
        <div class="card-title">
          <span class="title-icon" style="background:rgba(59,130,246,0.15);color:#3b82f6">🎯</span>
          直接影响
        </div>
        <ol class="impact-list">
          <li><strong>分块质量决定检索精度</strong> — 20% 重叠率有效减少语义截断，提升分块间的语义连贯性</li>
          <li><strong>QA 增强检索效果</strong> — 问答对天然适合问答式 RAG，显著提升答案匹配度</li>
          <li><strong>自动索引提升召回</strong> — 多索引维度支持多角度检索，提高知识召回率</li>
          <li><strong>向量模型无缝切换</strong> — 流式重建机制不中断服务，确保业务连续性</li>
          <li><strong>错误重试保障完整性</strong> — 多层容错确保每条数据都能被正确处理</li>
        </ol>
      </div>

      <!-- 三大检索模式 -->
      <div class="card">
        <div class="card-title">
          <span class="title-icon" style="background:rgba(168,85,247,0.15);color:#a855f7">🔍</span>
          支撑三大检索模式
        </div>
        <table class="data-table">
          <thead><tr><th>检索模式</th><th>依赖的训练产出</th><th>说明</th></tr></thead>
          <tbody>
            <tr><td><span class="tag green">embedding</span><br/>向量检索</td><td>Embedding 向量</td><td>语义相似度匹配，精准度最高</td></tr>
            <tr><td><span class="tag blue">fullTextRecall</span><br/>全文检索</td><td>dataset_data_text 文本</td><td>关键词匹配，速度快</td></tr>
            <tr><td><span class="tag purple">mixedRecall</span><br/>混合检索</td><td>向量 + 全文双重索引</td><td>兼顾语义与关键词，效果最优</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="tab-content" v-show="activeTab === 10">
      <!-- 2 列对比 -->
      <div class="vs-grid">
        <div class="vs-card vs-fastgpt">
          <h4><span style="color:#06b6d4">●</span> FastGPT 方案</h4>
          <table class="data-table">
            <thead><tr><th>方面</th><th>实现</th></tr></thead>
            <tbody>
              <tr><td>消息中间件</td><td><strong style="color:#06b6d4">MongoDB 原生</strong></td></tr>
              <tr><td>运维复杂度</td><td><span class="tag green">低</span> 无额外组件</td></tr>
              <tr><td>持久性</td><td><span class="tag green">天然持久</span> 数据库即队列</td></tr>
              <tr><td>适用规模</td><td>中小规模（最佳性价比）</td></tr>
            </tbody>
          </table>
        </div>
        <div class="vs-card vs-traditional">
          <h4><span style="color:#ec4899">●</span> 传统方案 (Redis + BullMQ)</h4>
          <table class="data-table">
            <thead><tr><th>方面</th><th>实现</th></tr></thead>
            <tbody>
              <tr><td>消息中间件</td><td>Redis / RabbitMQ</td></tr>
              <tr><td>运维复杂度</td><td><span class="tag pink">高</span> 多组件维护</td></tr>
              <tr><td>持久性</td><td><span class="tag orange">需额外配置</span></td></tr>
              <tr><td>适用规模</td><td>大规模集群</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 核心优势卡片 -->
      <div class="card" style="margin-top:20px">
        <div class="card-title">
          <span class="title-icon" style="background:rgba(0,212,255,0.15);color:#06b6d4">🏆</span>
          核心优势
        </div>
        <div class="adv-grid">
          <div class="adv-item">
            <div class="adv-icon">⚡</div>
            <div class="adv-title">原子抢占模式</div>
            <div class="adv-desc">单操作完成查询 + 锁定，天然防竞态，无需分布式锁</div>
          </div>
          <div class="adv-item">
            <div class="adv-icon">🔄</div>
            <div class="adv-title">双触发调度</div>
            <div class="adv-desc">Change Stream 实时 + Cron 定时，实时与可靠互补</div>
          </div>
          <div class="adv-item">
            <div class="adv-icon">🧩</div>
            <div class="adv-title">多态队列设计</div>
            <div class="adv-desc">单集合通过 mode 字段灵活扩展，无需多队列管理</div>
          </div>
          <div class="adv-item">
            <div class="adv-icon">🌊</div>
            <div class="adv-title">流式重建</div>
            <div class="adv-desc">内存友好的链式处理，可中断可恢复，不阻塞服务</div>
          </div>
        </div>
      </div>
    </div>

    <div class="tab-content" v-show="activeTab === 11">
      <div class="card">
        <div class="card-title">
          <span class="title-icon" style="background:rgba(99,102,241,0.15);color:#6366f1">📂</span>
          核心源码索引
        </div>
        <p style="font-size:0.82rem;color:#94a3b8;margin-bottom:20px">按架构层次组织的关键源码文件</p>
        <div class="source-layers">
          <div class="source-layer">
            <div class="sl-title"><span class="sl-dot" style="background:#3b82f6"></span> 数据模型层</div>
            <div class="sl-files">
              <span class="sl-file">schema.ts</span>
              <span class="sl-file">constants.ts</span>
              <span class="sl-file">type.ts</span>
            </div>
          </div>
          <div class="source-layer">
            <div class="sl-title"><span class="sl-dot" style="background:#06b6d4"></span> 入队控制层</div>
            <div class="sl-files">
              <span class="sl-file">controller.ts</span>
              <span class="sl-file">utils.ts</span>
            </div>
          </div>
          <div class="source-layer">
            <div class="sl-title"><span class="sl-dot" style="background:#10b981"></span> Worker 消费层</div>
            <div class="sl-files">
              <span class="sl-file">datasetParse.ts</span>
              <span class="sl-file">generateQA.ts</span>
              <span class="sl-file">generateVector.ts</span>
            </div>
          </div>
          <div class="source-layer">
            <div class="sl-title"><span class="sl-dot" style="background:#a855f7"></span> 调度层</div>
            <div class="sl-files">
              <span class="sl-file">cron.ts</span>
              <span class="sl-file">volumnMongoWatch.ts</span>
              <span class="sl-file">instrumentation.ts</span>
            </div>
          </div>
          <div class="source-layer">
            <div class="sl-title"><span class="sl-dot" style="background:#f59e0b"></span> API 路由层</div>
            <div class="sl-files">
              <span class="sl-file">6 个 training API</span>
              <span class="sl-file">trainingDetail</span>
            </div>
          </div>
          <div class="source-layer">
            <div class="sl-title"><span class="sl-dot" style="background:#ec4899"></span> 前端展示层</div>
            <div class="sl-files">
              <span class="sl-file">TrainingStates.tsx</span>
              <span class="sl-file">constants.ts</span>
              <span class="sl-file">api.ts</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

// Tab 管理
const activeTab = ref(0) // 默认显示概述 Tab
const tabs = [
  '概述', '架构', '数据模型', '训练模式',
  '调度', '并发', '容错', 'API',
  '重建', 'RAG影响', '优势', '源码'
]

let chart = null

const modes = [
  { name: '解析(parse)', model: 'agentModel' },
  { name: '分块(chunk)', model: 'vectorModel' },
  { name: '问答(qa)', model: 'agentModel' },
  { name: '自动(auto)', model: 'agentModel' },
  { name: '图片(image)', model: 'vlmModel' },
  { name: '图片解析(imageParse)', model: 'vlmModel' }
]

const modelTypes = ['agentModel', 'vectorModel', 'vlmModel']
const colors = { agentModel: '#6366f1', vectorModel: '#10b981', vlmModel: '#f59e0b' }

onMounted(() => {
  const el = document.getElementById('chart-training-models')
  if (!el) return
  chart = echarts.init(el)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: modelTypes, top: 0, textStyle: { fontSize: 11 } },
    grid: { left: 20, right: 20, bottom: 24, top: 36, containLabel: true },
    xAxis: { type: 'category', data: modes.map(m => m.name), axisLabel: { fontSize: 10, rotate: 15 } },
    yAxis: { type: 'value', max: 1, splitNumber: 1, axisLabel: { show: false } },
    series: modelTypes.map(t => ({
      name: t, type: 'bar', stack: 'total', barWidth: 28,
      data: modes.map(m => m.model === t ? 1 : 0),
      itemStyle: { color: colors[t] },
      emphasis: { focus: 'series' }
    }))
  })
  window.addEventListener('resize', () => chart?.resize())
})

onBeforeUnmount(() => { chart?.dispose(); chart = null })
</script>

<style scoped>
/* Tab 导航 */
.tab-nav {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding: 8px 0 16px;
  margin-bottom: 20px;
  scrollbar-width: thin;
  scrollbar-color: rgba(99,102,241,0.3) transparent;
}
.tab-nav::-webkit-scrollbar {
  height: 4px;
}
.tab-nav::-webkit-scrollbar-track {
  background: transparent;
}
.tab-nav::-webkit-scrollbar-thumb {
  background: rgba(99,102,241,0.3);
  border-radius: 2px;
}

.tab-btn {
  flex-shrink: 0;
  padding: 8px 18px;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  background: rgba(255,255,255,0.03);
  color: #94a3b8;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
  white-space: nowrap;
}
.tab-btn:hover {
  background: rgba(99,102,241,0.08);
  border-color: rgba(99,102,241,0.25);
  color: #c7d2fe;
}
.tab-btn.active {
  background: rgba(99,102,241,0.15);
  border-color: rgba(99,102,241,0.5);
  color: #a5b4fc;
  font-weight: 700;
  box-shadow: 0 0 12px rgba(99,102,241,0.15);
}

/* Tab 内容 */
.tab-content {
  min-height: 200px;
}

/* 通用卡片样式 */
.card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 16px;
}
.card h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 16px;
}

/* 表格基础样式 */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}
.data-table th {
  text-align: left;
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  color: #94a3b8;
  font-weight: 600;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.data-table td {
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  color: #cbd5e1;
}
.data-table code {
  background: rgba(99,102,241,0.12);
  color: #a5b4fc;
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 0.78rem;
}

/* 彩色标签 */
.tag { padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.tag.agent { background: rgba(99,102,241,.15); color: #6366f1; }
.tag.vector { background: rgba(16,185,129,.15); color: #10b981; }
.tag.vlm { background: rgba(245,158,11,.15); color: #f59e0b; }

/* 特性列表 */
.feature-list {
  list-style: none;
  padding: 0;
}
.feature-list li {
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  color: #cbd5e1;
  font-size: 0.85rem;
}
.feature-list li:last-child {
  border-bottom: none;
}
.feature-list strong {
  color: #e2e8f0;
}

/* QA Flow */
.qa-flow-wrapper {
  background: rgba(15,23,42,0.5);
  border: 1px solid rgba(99,102,241,0.15);
  border-radius: 10px;
  padding: 20px;
}
.qa-flow-main {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}
.qa-node {
  padding: 10px 14px;
  background: rgba(30,41,59,0.9);
  border: 1px solid rgba(148,163,184,0.2);
  border-radius: 8px;
  text-align: center;
  min-width: 80px;
  color: #e2e8f0;
}
.qa-node-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 4px;
}
.qa-node-sub {
  font-size: 0.7rem;
  color: #94a3b8;
  line-height: 1.4;
}
.qa-node-primary {
  background: rgba(99,102,241,0.12);
  border-color: rgba(99,102,241,0.35);
}
.qa-node-primary .qa-node-label { color: #a5b4fc; }
.qa-node-success {
  background: rgba(16,185,129,0.1);
  border-color: rgba(16,185,129,0.3);
}
.qa-node-success .qa-node-label { color: #6ee7b7; }
.qa-arrow {
  color: #64748b;
  font-weight: 700;
  font-size: 1rem;
}

/* Fallback section */
.qa-flow-fallback {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 0;
  margin-top: 18px;
  border-top: 1px solid rgba(148,163,184,0.1);
  padding-top: 16px;
  align-items: stretch;
}
.qa-branch-left, .qa-branch-right {
  padding: 12px 16px;
  border-radius: 8px;
}
.qa-branch-left {
  background: rgba(16,185,129,0.05);
  border: 1px solid rgba(16,185,129,0.15);
}
.qa-branch-right {
  background: rgba(245,158,11,0.05);
  border: 1px solid rgba(245,158,11,0.15);
}
.qa-branch-label {
  font-size: 0.82rem;
  font-weight: 700;
  color: #10b981;
  margin-bottom: 6px;
}
.qa-branch-warn {
  color: #f59e0b;
}
.qa-branch-desc {
  font-size: 0.76rem;
  color: #94a3b8;
  line-height: 1.6;
}
.qa-branch-desc code {
  background: rgba(99,102,241,0.15);
  color: #a5b4fc;
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 0.72rem;
}
.qa-branch-desc strong {
  color: #e2e8f0;
}
.qa-branch-divider {
  width: 1px;
  background: rgba(148,163,184,0.15);
  margin: 0 4px;
}

small { opacity: .7; font-size: 11px; }

/* ===== 高亮卡片 ===== */
.highlight-card {
  border: 1px solid rgba(0,212,255,0.15);
  background: linear-gradient(135deg, rgba(0,212,255,0.04) 0%, rgba(168,85,247,0.04) 100%);
  box-shadow: 0 0 24px rgba(0,212,255,0.06);
}
.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.95rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 14px;
}
.title-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  font-size: 0.85rem;
  flex-shrink: 0;
}
.highlight-desc {
  font-size: 0.85rem;
  color: #94a3b8;
  line-height: 1.9;
  margin-bottom: 0;
}
.text-primary { color: #e2e8f0 !important; }

/* ===== 扩展 Tag 颜色 ===== */
.tag.green { background: rgba(16,185,129,.15); color: #10b981; }
.tag.blue { background: rgba(59,130,246,.15); color: #3b82f6; }
.tag.purple { background: rgba(168,85,247,.15); color: #a855f7; }
.tag.orange { background: rgba(245,158,11,.15); color: #f59e0b; }
.tag.pink { background: rgba(236,72,153,.15); color: #ec4899; }
.tag.cyan { background: rgba(6,182,212,.15); color: #06b6d4; }

/* ===== 卡片网格 ===== */
.mode-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}
.mode-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  padding: 20px;
}
.mode-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  margin-bottom: 12px;
}
.mode-name {
  font-size: 0.9rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 8px;
}
.mode-desc {
  font-size: 0.78rem;
  color: #94a3b8;
  line-height: 1.7;
}

/* ===== 管道流程图 ===== */
.pipeline {
  display: flex;
  align-items: center;
  gap: 6px;
  overflow-x: auto;
  padding: 8px 0;
}
.pipeline-node {
  flex-shrink: 0;
  padding: 14px 16px;
  background: rgba(30,41,59,0.8);
  border: 1px solid rgba(148,163,184,0.15);
  border-radius: 10px;
  text-align: center;
  min-width: 100px;
}
.pn-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 4px;
}
.pn-desc {
  font-size: 0.7rem;
  color: #94a3b8;
}
.pipeline-arrow {
  flex-shrink: 0;
  color: #475569;
  font-size: 1.2rem;
  font-weight: 700;
}

/* ===== 字段列表 ===== */
.field-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.field-item {
  display: grid;
  grid-template-columns: 130px 100px 1fr;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  font-size: 0.82rem;
  align-items: center;
}
.field-item:last-child { border-bottom: none; }
.field-name {
  font-family: 'Courier New', monospace;
  color: #a5b4fc;
  background: rgba(99,102,241,0.1);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.78rem;
}
.field-type {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.72rem;
  font-weight: 600;
  background: rgba(168,85,247,0.1);
  color: #c4b5fd;
}
.field-desc {
  color: #94a3b8;
}

/* ===== 索引 Badge ===== */
.index-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 14px;
  background: rgba(30,41,59,0.7);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 6px;
  font-family: 'Courier New', monospace;
  font-size: 0.78rem;
  color: #cbd5e1;
}

/* ===== 双触发器布局 ===== */
.dual-trigger {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
@media (max-width: 640px) {
  .dual-trigger { grid-template-columns: 1fr; }
}
.trigger-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  padding: 20px;
}
.trigger-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.trigger-list li {
  padding: 6px 0;
  color: #94a3b8;
  font-size: 0.82rem;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  line-height: 1.6;
}
.trigger-list li:last-child { border-bottom: none; }
.trigger-list code {
  background: rgba(99,102,241,0.12);
  color: #a5b4fc;
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 0.75rem;
}
.tc-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 0.72rem;
  font-weight: 700;
  margin-bottom: 10px;
}
.tc-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 4px;
}

/* ===== 代码块 ===== */
.code-block {
  background: rgba(15,23,42,0.85);
  border: 1px solid rgba(99,102,241,0.15);
  border-radius: 8px;
  padding: 18px;
  overflow-x: auto;
}
.code-block pre {
  margin: 0;
  font-family: 'Courier New', Consolas, monospace;
  font-size: 0.82rem;
  line-height: 1.75;
  color: #cbd5e1;
}
.kw { color: #c084fc; font-weight: 600; }
.fn { color: #60a5fa; }
.str { color: #a5b4fc; }
.num { color: #f59e0b; }
.cm { color: #64748b; font-style: italic; }
.op { color: #f472b6; }

/* ===== Tab 8: 重建流程步骤 ===== */
.flow-steps {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 8px 0;
}
.flow-step {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  background: rgba(30,41,59,0.6);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px;
}
.fs-num {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(245,158,11,0.2), rgba(245,158,11,0.1));
  color: #f59e0b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.85rem;
  flex-shrink: 0;
  border: 1px solid rgba(245,158,11,0.3);
}
.fs-text {
  font-size: 0.85rem;
  color: #cbd5e1;
  line-height: 1.6;
}
.fs-text code {
  background: rgba(99,102,241,0.15);
  color: #a5b4fc;
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 0.78rem;
}
.flow-connector {
  width: 2px;
  height: 18px;
  background: linear-gradient(to bottom, rgba(245,158,11,0.4), rgba(245,158,11,0.1));
  margin: 0 auto;
}

/* ===== Tab 9: RAG 生命周期图 ===== */
.lifecycle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}
.lifecycle-node {
  padding: 14px 20px;
  background: rgba(30,41,59,0.7);
  border: 1px solid rgba(148,163,184,0.15);
  border-radius: 10px;
  text-align: center;
  font-size: 0.88rem;
  font-weight: 600;
  color: #e2e8f0;
  line-height: 1.5;
}
.lifecycle-node.highlight {
  background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(168,85,247,0.1));
  border-color: rgba(99,102,241,0.4);
  box-shadow: 0 0 16px rgba(99,102,241,0.12);
  color: #c4b5fd;
}
.lifecycle-arrow {
  color: #475569;
  font-size: 1.2rem;
  font-weight: 700;
}

/* ===== Tab 9: 影响列表 ===== */
.impact-list {
  list-style: none;
  padding: 0;
  counter-reset: impact-counter;
}
.impact-list li {
  counter-increment: impact-counter;
  padding: 10px 0 10px 36px;
  position: relative;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  font-size: 0.84rem;
  color: #94a3b8;
  line-height: 1.7;
}
.impact-list li:last-child { border-bottom: none; }
.impact-list li::before {
  content: counter(impact-counter);
  position: absolute;
  left: 0;
  top: 10px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(59,130,246,0.12);
  color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  font-weight: 700;
}
.impact-list strong {
  color: #e2e8f0;
}

/* ===== Tab 10: VS 对比网格 ===== */
.vs-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.vs-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  padding: 20px;
}
.vs-card h4 {
  font-size: 0.92rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 14px;
}
.vs-fastgpt {
  border-color: rgba(0,212,255,0.2);
  background: linear-gradient(135deg, rgba(0,212,255,0.03), rgba(0,212,255,0.01));
}
.vs-traditional {
  border-color: rgba(236,72,153,0.15);
}

/* ===== Tab 10: 核心优势网格 ===== */
.adv-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 14px;
}
.adv-item {
  padding: 16px;
  background: rgba(30,41,59,0.5);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 10px;
  text-align: center;
}
.adv-icon {
  font-size: 1.6rem;
  margin-bottom: 10px;
}
.adv-title {
  font-size: 0.88rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 8px;
}
.adv-desc {
  font-size: 0.78rem;
  color: #94a3b8;
  line-height: 1.6;
}

/* ===== Tab 11: 源码索引层 ===== */
.source-layers {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.source-layer {
  padding: 14px 16px;
  background: rgba(30,41,59,0.5);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 10px;
}
.sl-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.88rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 10px;
}
.sl-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.sl-files {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.sl-file {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(15,23,42,0.7);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 5px;
  font-family: 'Courier New', monospace;
  font-size: 0.76rem;
  color: #94a3b8;
}

/* ===== 响应式样式 ===== */
@media (max-width: 768px) {
  .dual-trigger { grid-template-columns: 1fr; }
  .vs-grid { grid-template-columns: 1fr; }
  .mode-grid { grid-template-columns: 1fr; }
  .pipeline {
    flex-direction: column;
    align-items: center;
  }
  .pipeline-arrow { transform: rotate(90deg); }
  .field-item {
    grid-template-columns: 1fr;
    gap: 4px;
  }
  .field-name, .field-type { min-width: auto; }
  .lifecycle {
    flex-direction: column;
  }
  .qa-flow-fallback {
    grid-template-columns: 1fr;
  }
  .qa-branch-divider {
    width: 100%;
    height: 1px;
    margin: 8px 0;
  }
}
</style>
