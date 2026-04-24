<template>
  <div class="section-page">
    <div class="section-header">
      <h2>核心依赖包</h2>
      <p>FastGPT 项目中使用的所有核心 npm 依赖，按功能类别分组展示，涵盖 AI、数据库、文件解析、Web 框架等关键模块。</p>
    </div>

    <!-- AI & 模型 -->
    <div class="card">
      <div class="card-title"><span class="icon">🤖</span> AI & 模型</div>
      <table class="dep-table">
        <thead><tr><th>包名</th><th>版本</th><th>说明</th><th>链接</th></tr></thead>
        <tbody>
          <tr>
            <td class="dep-name">openai</td>
            <td>4.104.0</td>
            <td>OpenAI API SDK</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/openai" target="_blank">npm</a></td>
          </tr>
          <tr>
            <td class="dep-name">tiktoken</td>
            <td>1.0.17</td>
            <td>Token计数(OpenAI)</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/tiktoken" target="_blank">npm</a></td>
          </tr>
          <tr>
            <td class="dep-name">@fortaine/fetch-event-source</td>
            <td>^3.0.6</td>
            <td>SSE流式响应</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/@fortaine/fetch-event-source" target="_blank">npm</a></td>
          </tr>
          <tr>
            <td class="dep-name">@node-rs/jieba</td>
            <td>2.0.1</td>
            <td>中文分词</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/@node-rs/jieba" target="_blank">npm</a></td>
          </tr>
          <tr>
            <td class="dep-name">@modelcontextprotocol/sdk</td>
            <td>^1</td>
            <td>MCP协议SDK</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/@modelcontextprotocol/sdk" target="_blank">npm</a></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 数据库 -->
    <div class="card">
      <div class="card-title"><span class="icon">🗄️</span> 数据库</div>
      <table class="dep-table">
        <thead><tr><th>包名</th><th>版本</th><th>说明</th><th>链接</th></tr></thead>
        <tbody>
          <tr>
            <td class="dep-name">@zilliz/milvus2-sdk-node</td>
            <td>2.4.10</td>
            <td>Milvus向量数据库客户端</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/@zilliz/milvus2-sdk-node" target="_blank">npm</a></td>
          </tr>
          <tr>
            <td class="dep-name">mongoose</td>
            <td>^8.10.1</td>
            <td>MongoDB ODM</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/mongoose" target="_blank">npm</a></td>
          </tr>
          <tr>
            <td class="dep-name">pg</td>
            <td>^8.10.0</td>
            <td>PostgreSQL客户端</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/pg" target="_blank">npm</a></td>
          </tr>
          <tr>
            <td class="dep-name">ioredis</td>
            <td>^5.6.0</td>
            <td>Redis客户端</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/ioredis" target="_blank">npm</a></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 任务队列 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚡</span> 任务队列</div>
      <table class="dep-table">
        <thead><tr><th>包名</th><th>版本</th><th>说明</th><th>链接</th></tr></thead>
        <tbody>
          <tr>
            <td class="dep-name">bullmq</td>
            <td>^5.52.2</td>
            <td>Redis任务队列</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/bullmq" target="_blank">npm</a></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 对象存储 -->
    <div class="card">
      <div class="card-title"><span class="icon">📦</span> 对象存储</div>
      <table class="dep-table">
        <thead><tr><th>包名</th><th>版本</th><th>说明</th><th>链接</th></tr></thead>
        <tbody>
          <tr>
            <td class="dep-name">minio</td>
            <td>8.0.7</td>
            <td>MinIO/S3对象存储</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/minio" target="_blank">npm</a></td>
          </tr>
          <tr>
            <td class="dep-name">@aws-sdk/client-s3</td>
            <td>^3.948.0</td>
            <td>AWS S3 SDK</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/@aws-sdk/client-s3" target="_blank">npm</a></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 文件解析 -->
    <div class="card">
      <div class="card-title"><span class="icon">📄</span> 文件解析</div>
      <table class="dep-table">
        <thead><tr><th>包名</th><th>版本</th><th>说明</th><th>链接</th></tr></thead>
        <tbody>
          <tr>
            <td class="dep-name">pdfjs-dist</td>
            <td>4.10.38</td>
            <td>PDF解析器</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/pdfjs-dist" target="_blank">npm</a></td>
          </tr>
          <tr>
            <td class="dep-name">mammoth</td>
            <td>^1.11.0</td>
            <td>DOCX转HTML</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/mammoth" target="_blank">npm</a></td>
          </tr>
          <tr>
            <td class="dep-name">node-xlsx</td>
            <td>^0.24.0</td>
            <td>Excel解析器</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/node-xlsx" target="_blank">npm</a></td>
          </tr>
          <tr>
            <td class="dep-name">papaparse</td>
            <td>5.4.1</td>
            <td>CSV解析器</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/papaparse" target="_blank">npm</a></td>
          </tr>
          <tr>
            <td class="dep-name">cheerio</td>
            <td>1.0.0-rc.12</td>
            <td>HTML解析器</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/cheerio" target="_blank">npm</a></td>
          </tr>
          <tr>
            <td class="dep-name">turndown</td>
            <td>^7.1.2</td>
            <td>HTML转Markdown</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/turndown" target="_blank">npm</a></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Web框架 -->
    <div class="card">
      <div class="card-title"><span class="icon">🌐</span> Web框架</div>
      <table class="dep-table">
        <thead><tr><th>包名</th><th>版本</th><th>说明</th><th>链接</th></tr></thead>
        <tbody>
          <tr>
            <td class="dep-name">next</td>
            <td>16.2.1</td>
            <td>Next.js框架</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/next" target="_blank">npm</a></td>
          </tr>
          <tr>
            <td class="dep-name">react</td>
            <td>^18</td>
            <td>React UI</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/react" target="_blank">npm</a></td>
          </tr>
          <tr>
            <td class="dep-name">reactflow</td>
            <td>^11.7.4</td>
            <td>流程图编辑器</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/reactflow" target="_blank">npm</a></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 工具库 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔧</span> 工具库</div>
      <table class="dep-table">
        <thead><tr><th>包名</th><th>版本</th><th>说明</th><th>链接</th></tr></thead>
        <tbody>
          <tr>
            <td class="dep-name">i18next</td>
            <td>23.16.8</td>
            <td>国际化</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/i18next" target="_blank">npm</a></td>
          </tr>
          <tr>
            <td class="dep-name">@opentelemetry/api</td>
            <td>^1.9.0</td>
            <td>OpenTelemetry API</td>
            <td><a class="dep-link" href="https://www.npmjs.com/package/@opentelemetry/api" target="_blank">npm</a></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
