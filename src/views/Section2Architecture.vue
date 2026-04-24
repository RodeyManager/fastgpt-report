<template>
  <div class="section-page">
    <div class="section-header">
      <h2>知识库架构</h2>
      <p>Dataset → Collection → Data/Chunk → Vector Index</p>
    </div>

    <!-- 四层数据模型 -->
    <div class="card">
      <div class="card-title"><span class="icon">◈</span>四层数据模型</div>
      <table class="data-table">
        <thead>
          <tr>
            <th>层级</th><th>集合</th><th>存储</th><th>核心字段</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Dataset</strong>（知识库）</td>
            <td><code>datasets</code></td>
            <td>MongoDB</td>
            <td>vectorModel, agentModel, vlmModel, chunkSettings</td>
          </tr>
          <tr>
            <td><strong>Collection</strong>（集合）</td>
            <td><code>dataset_collections</code></td>
            <td>MongoDB</td>
            <td>type(file/link/apiFile/images), tags, rawText</td>
          </tr>
          <tr>
            <td><strong>Data</strong>（数据块）</td>
            <td><code>dataset_datas</code></td>
            <td>MongoDB</td>
            <td>q, a, indexes[], chunkIndex, imageId</td>
          </tr>
          <tr>
            <td><strong>Training</strong>（训练队列）</td>
            <td><code>dataset_trainings</code></td>
            <td>MongoDB</td>
            <td>mode(parse/chunk/qa/image), lockTime, TTL 7天</td>
          </tr>
          <tr>
            <td><strong>DataText</strong>（全文索引）</td>
            <td><code>dataset_data_texts</code></td>
            <td>MongoDB</td>
            <td>fullTextToken（Jieba分词）</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 向量存储Schema -->
    <div class="two-col">
      <div class="card">
        <div class="card-title"><span class="icon">◈</span>向量存储 Schema</div>
        <table class="data-table">
          <thead>
            <tr><th>字段</th><th>类型</th><th>说明</th></tr>
          </thead>
          <tbody>
            <tr><td><code>id</code></td><td>BIGSERIAL</td><td>主键自增</td></tr>
            <tr><td><code>vector</code></td><td>VECTOR(1536)</td><td>嵌入向量</td></tr>
            <tr><td><code>team_id</code></td><td>VARCHAR</td><td>团队标识</td></tr>
            <tr><td><code>dataset_id</code></td><td>VARCHAR</td><td>知识库标识</td></tr>
            <tr><td><code>collection_id</code></td><td>VARCHAR</td><td>集合标识</td></tr>
            <tr><td><code>createtime</code></td><td>TIMESTAMP</td><td>创建时间</td></tr>
          </tbody>
        </table>
      </div>

      <div class="card">
        <div class="card-title"><span class="icon">◈</span>HNSW 索引参数</div>
        <div class="chart-container" ref="chartRef"></div>
      </div>
    </div>

    <!-- 数据处理流水线 -->
    <div class="flow-diagram">
      <div class="card-title" style="justify-content:center;margin-bottom:12px;">
        <span class="icon">◈</span>数据处理流水线
      </div>
      <div class="flow-steps">
        <div class="flow-step primary">文档上传</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step">文本提取</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step">数据清洗</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step">文本分块</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step">训练队列</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step">向量化</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step primary">向量存储</div>
        <div class="flow-arrow">→</div>
        <div class="flow-step primary">检索服务</div>
      </div>
    </div>

    <!-- 架构总结 -->
    <div class="card">
      <div class="card-title"><span class="icon">◈</span>分离存储架构</div>
      <div class="highlight-block">
        MongoDB存储元数据与文本索引，PostgreSQL/Milvus存储向量数据，实现元数据与向量的分离存储架构。
        通过 HNSW 索引（m=32, ef_construction=128）基于内积距离实现高效近似最近邻检索，支持千万级向量毫秒级响应。
      </div>
    </div>

    <div class="card">
      <div class="card-title"><span class="icon">&#9881;</span> 分离存储架构分析</div>
      <p style="color:var(--text-secondary);font-size:0.88rem;margin-bottom:16px;">FastGPT 采用4种独立存储系统，每种负责其最擅长的场景。核心设计原则：让每个存储系统处理它最擅长的工作负载。</p>
      
      <div class="storage-flow">
        <div class="storage-box mongo">
          <span class="s-icon">&#128202;</span>
          <span class="s-name">MongoDB</span>
          <span class="s-desc">41个集合 · 业务数据 · 全文检索</span>
        </div>
        <span class="storage-flow-arrow">&#8596;</span>
        <div class="storage-box pg">
          <span class="s-icon">&#128268;</span>
          <span class="s-name">PostgreSQL</span>
          <span class="s-desc">pgvector · HNSW向量索引 · 1536维</span>
        </div>
        <span class="storage-flow-arrow">&#8596;</span>
        <div class="storage-box redis">
          <span class="s-icon">&#9889;</span>
          <span class="s-name">Redis</span>
          <span class="s-desc">会话·缓存·队列·限流·SSE恢复</span>
        </div>
        <span class="storage-flow-arrow">&#8596;</span>
        <div class="storage-box s3">
          <span class="s-icon">&#128193;</span>
          <span class="s-name">MinIO/S3</span>
          <span class="s-desc">文件存储 · 多厂商(MinIO/AWS/COS/OSS)</span>
        </div>
      </div>

      <p style="color:var(--text-secondary);font-size:0.88rem;margin:16px 0;">数据流: 用户上传文件 → <strong>S3存储</strong> → Worker解析 → <strong>MongoDB存储原文</strong> → 文本分块 → Embedding API → <strong>PostgreSQL向量存储</strong> → 检索: 查询向量化 → <strong>PG向量检索</strong> + <strong>MongoDB全文检索</strong> → RRF融合 → 结果返回</p>

      <div class="pros-cons-grid">
        <div class="pros-card">
          <h4>&#10003; 方案优势</h4>
          <ul>
            <li><strong>性能优化</strong>：每个系统针对其工作负载调优(Redis亚毫秒, PG向量HNSW)</li>
            <li><strong>独立扩展</strong>：各系统可独立扩容(PG副本加速向量检索, MongoDB分片扩展元数据)</li>
            <li><strong>全自托管</strong>：所有组件开源可自托管(pgvector vs MongoDB Atlas)</li>
            <li><strong>灵活替换</strong>：向量DB可插拔(PG/Milvus/OpenGauss/OceanBase), S3多厂商</li>
            <li><strong>成本效率</strong>：PG存向量比专用向量DB更经济, S3比MongoDB GridFS更便宜</li>
            <li><strong>运维隔离</strong>：向量重建不影响MongoDB, S3清理不影响聊天性能</li>
          </ul>
        </div>
        <div class="cons-card">
          <h4>&#10007; 方案不足</h4>
          <ul>
            <li><strong>运维复杂</strong>：需部署监控备份4+系统(pgvector+mongo+redis+minio)</li>
            <li><strong>数据一致性</strong>：跨系统引用(MongoDB indexes.dataId → PG id)需精心清理</li>
            <li><strong>开发成本</strong>：开发者需理解哪个系统存什么, 以及跨系统JOIN模式</li>
            <li><strong>部署门槛</strong>：Docker-compose需7+容器(PG/Mongo/Redis/MinIO/FastGPT/Sandbox/AIProxy)</li>
            <li><strong>事务边界</strong>：无跨系统事务, 训练失败(PG已写入但MongoDB未写入)需清理逻辑</li>
            <li><strong>备份复杂</strong>：必须协调4个系统的备份以实现一致恢复</li>
          </ul>
        </div>
      </div>

      <div class="highlight-block" style="font-size:0.85rem;">
        <strong>关键洞察:</strong> MongoDB的 <code>indexes.dataId</code> 字段是连接MongoDB和PostgreSQL的桥梁 — 它存储PG modeldata表的ID。向量检索返回PG ID → MongoDB通过此ID获取完整数据块。
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const chartRef = ref(null)
let chartInstance = null

onMounted(() => {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, textStyle: { color: '#94a3b8', fontSize: 11 } },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '45%'],
      label: { color: '#e2e8f0', fontSize: 11 },
      data: [
        { value: 1536, name: '向量维度', itemStyle: { color: '#6366f1' } },
        { value: 32, name: 'HNSW m', itemStyle: { color: '#06b6d4' } },
        { value: 128, name: 'ef_construction', itemStyle: { color: '#8b5cf6' } }
      ]
    }]
  })
})

onUnmounted(() => {
  chartInstance?.dispose()
})
</script>
