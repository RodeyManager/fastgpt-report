<template>
  <section class="section-page">
    <div class="section-header">
      <h2>数据表结构详情</h2>
      <p>FastGPT 知识库系统 MongoDB 集合与 PostgreSQL 向量表完整字段定义</p>
    </div>

    <!-- ER Relationship Diagram -->
    <div class="card">
      <div class="card-title"><span class="icon">&#128279;</span> 数据表关联关系图</div>
      <p style="color:var(--text-secondary);font-size:0.88rem;margin-bottom:16px;">FastGPT 使用 MongoDB (41个集合) + PostgreSQL (1个向量表) 的双数据库架构。核心数据链路: teams → datasets → dataset_collections → dataset_datas ↔ modeldata(PG)</p>

      <div class="er-container">
        <h4 style="color:var(--accent-cyan);margin-bottom:12px;font-size:0.9rem;">&#128218; 知识库核心链路</h4>
        <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-bottom:16px;">
          <div class="er-table">
            <div class="er-table-header">teams</div>
            <div class="er-table-body">
              <div class="er-table-row"><span class="er-table-pk">_id</span> ObjectId</div>
              <div class="er-table-row">name String</div>
              <div class="er-table-row">ownerId → users</div>
            </div>
          </div>
          <div style="display:flex;align-items:center;color:var(--accent-blue);font-size:1.2rem;">&#8594;</div>
          <div class="er-table">
            <div class="er-table-header">datasets</div>
            <div class="er-table-body">
              <div class="er-table-row"><span class="er-table-pk">_id</span> ObjectId</div>
              <div class="er-table-row"><span class="er-table-fk">teamId</span> → teams</div>
              <div class="er-table-row"><span class="er-table-fk">parentId</span> → datasets</div>
              <div class="er-table-row">vectorModel String</div>
              <div class="er-table-row">vlmModel String</div>
            </div>
          </div>
          <div style="display:flex;align-items:center;color:var(--accent-blue);font-size:1.2rem;">&#8594;</div>
          <div class="er-table">
            <div class="er-table-header">dataset_collections</div>
            <div class="er-table-body">
              <div class="er-table-row"><span class="er-table-pk">_id</span> ObjectId</div>
              <div class="er-table-row"><span class="er-table-fk">datasetId</span> → datasets</div>
              <div class="er-table-row"><span class="er-table-fk">parentId</span> → collections</div>
              <div class="er-table-row">type Enum</div>
              <div class="er-table-row">chunkSettings JSON</div>
            </div>
          </div>
          <div style="display:flex;align-items:center;color:var(--accent-blue);font-size:1.2rem;">&#8594;</div>
          <div class="er-table">
            <div class="er-table-header">dataset_datas</div>
            <div class="er-table-body">
              <div class="er-table-row"><span class="er-table-pk">_id</span> ObjectId</div>
              <div class="er-table-row"><span class="er-table-fk">datasetId</span> → datasets</div>
              <div class="er-table-row"><span class="er-table-fk">collectionId</span> → collections</div>
              <div class="er-table-row">q String (主文本)</div>
              <div class="er-table-row">indexes[].dataId → PG</div>
            </div>
          </div>
          <div style="display:flex;align-items:center;color:var(--accent-red);font-size:1.2rem;">&#8596;</div>
          <div class="er-table" style="border-color:var(--accent-blue);">
            <div class="er-table-header" style="background:rgba(99,102,241,0.3);">modeldata (PG)</div>
            <div class="er-table-body">
              <div class="er-table-row"><span class="er-table-pk">id</span> BIGSERIAL</div>
              <div class="er-table-row">vector VECTOR(1536)</div>
              <div class="er-table-row"><span class="er-table-fk">dataset_id</span> → datasets</div>
              <div class="er-table-row"><span class="er-table-fk">collection_id</span> → collections</div>
            </div>
          </div>
        </div>

        <h4 style="color:var(--accent-orange);margin-top:20px;margin-bottom:12px;font-size:0.9rem;">&#128273; 跨数据库桥梁</h4>
        <div class="highlight-block" style="font-size:0.82rem;">
          <code>dataset_datas.indexes[].dataId</code> (MongoDB) 存储 PostgreSQL <code>modeldata.id</code> (BIGSERIAL) — 这是连接两个数据库的外键。向量检索返回PG ID → MongoDB通过此ID获取完整数据块内容。
        </div>

        <h4 style="color:var(--accent-green);margin-top:20px;margin-bottom:12px;font-size:0.9rem;">&#128101; 用户权限体系</h4>
        <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:8px;">
          <div class="er-table">
            <div class="er-table-header">users</div>
            <div class="er-table-body">
              <div class="er-table-row"><span class="er-table-pk">_id</span> ObjectId</div>
              <div class="er-table-row">username String</div>
              <div class="er-table-row">lastLoginTmbId → members</div>
            </div>
          </div>
          <div style="display:flex;align-items:center;color:var(--accent-blue);font-size:1.2rem;">&#8596;</div>
          <div class="er-table">
            <div class="er-table-header">team_members</div>
            <div class="er-table-body">
              <div class="er-table-row"><span class="er-table-pk">_id</span> ObjectId</div>
              <div class="er-table-row"><span class="er-table-fk">teamId</span> → teams</div>
              <div class="er-table-row"><span class="er-table-fk">userId</span> → users</div>
              <div class="er-table-row">role Enum</div>
            </div>
          </div>
          <div style="display:flex;align-items:center;color:var(--accent-blue);font-size:1.2rem;">&#8596;</div>
          <div class="er-table">
            <div class="er-table-header">resource_permissions</div>
            <div class="er-table-body">
              <div class="er-table-row"><span class="er-table-pk">_id</span> ObjectId</div>
              <div class="er-table-row"><span class="er-table-fk">tmbId</span> → members</div>
              <div class="er-table-row"><span class="er-table-fk">groupId</span> → groups</div>
              <div class="er-table-row">resourceType Enum</div>
              <div class="er-table-row">resourceId (多态)</div>
            </div>
          </div>
        </div>

        <h4 style="color:var(--accent-purple);margin-top:20px;margin-bottom:12px;font-size:0.9rem;">&#128172; 应用对话体系</h4>
        <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:8px;">
          <div class="er-table">
            <div class="er-table-header">apps</div>
            <div class="er-table-body">
              <div class="er-table-row"><span class="er-table-pk">_id</span> ObjectId</div>
              <div class="er-table-row"><span class="er-table-fk">teamId</span> → teams</div>
              <div class="er-table-row">modules JSON (工作流)</div>
              <div class="er-table-row">edges JSON</div>
            </div>
          </div>
          <div style="display:flex;align-items:center;color:var(--accent-blue);font-size:1.2rem;">&#8594;</div>
          <div class="er-table">
            <div class="er-table-header">chats</div>
            <div class="er-table-body">
              <div class="er-table-row"><span class="er-table-pk">_id</span> ObjectId</div>
              <div class="er-table-row"><span class="er-table-fk">appId</span> → apps</div>
              <div class="er-table-row">chatId String</div>
              <div class="er-table-row">title String</div>
            </div>
          </div>
          <div style="display:flex;align-items:center;color:var(--accent-blue);font-size:1.2rem;">&#8594;</div>
          <div class="er-table">
            <div class="er-table-header">chatitems</div>
            <div class="er-table-body">
              <div class="er-table-row"><span class="er-table-pk">_id</span> ObjectId</div>
              <div class="er-table-row"><span class="er-table-fk">chatId</span> → chats</div>
              <div class="er-table-row">obj Enum (Human/AI/System)</div>
              <div class="er-table-row">value String</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- datasets -->
    <div class="card">
      <div class="card-title-row">
        <h3 class="card-title"><span class="icon">◈</span> datasets (知识库集合)</h3>
        <div>
          <span class="tag tag-blue">MongoDB</span>
          <span class="source-tag">来源: packages/service/core/dataset/schema.ts</span>
        </div>
      </div>
      <table class="data-table">
        <thead><tr><th>字段名</th><th>类型</th><th>描述</th></tr></thead>
        <tbody>
          <tr><td class="field">_id</td><td>ObjectId</td><td>主键</td></tr>
          <tr><td class="field">parentId</td><td>ObjectId</td><td>父级ID (文件夹层级)</td></tr>
          <tr><td class="field">teamId</td><td>ObjectId</td><td>团队ID</td></tr>
          <tr><td class="field">tmbId</td><td>ObjectId</td><td>成员ID</td></tr>
          <tr><td class="field">type</td><td>String</td><td>数据集类型: folder / dataset / websiteDataset / externalFile / apiDataset / feishu / yuque</td></tr>
          <tr><td class="field">name</td><td>String</td><td>名称</td></tr>
          <tr><td class="field">intro</td><td>String</td><td>简介</td></tr>
          <tr><td class="field">avatar</td><td>String</td><td>头像</td></tr>
          <tr><td class="field">vectorModel</td><td>String</td><td>向量模型 (默认 text-embedding-3-small)</td></tr>
          <tr><td class="field">agentModel</td><td>String</td><td>AI代理模型</td></tr>
          <tr><td class="field">vlmModel</td><td>String</td><td>视觉语言模型</td></tr>
          <tr><td class="field">chunkSettings</td><td>Object</td><td>分块配置 (trainingType, chunkSize, chunkSplitMode, indexSize等)</td></tr>
          <tr><td class="field">websiteConfig</td><td>Object</td><td>网站同步配置</td></tr>
          <tr><td class="field">apiDatasetServer</td><td>Object</td><td>API数据集服务配置</td></tr>
          <tr><td class="field">status</td><td>String</td><td>状态: active / syncing / waiting / error</td></tr>
          <tr><td class="field">forbid</td><td>Boolean</td><td>是否禁用</td></tr>
          <tr><td class="field">deleteTime</td><td>Date</td><td>软删除时间</td></tr>
          <tr><td class="field">createTime</td><td>Date</td><td>创建时间</td></tr>
        </tbody>
      </table>
    </div>

    <!-- dataset_collections -->
    <div class="card">
      <div class="card-title-row">
        <h3 class="card-title"><span class="icon">◈</span> dataset_collections (数据集合)</h3>
        <div>
          <span class="tag tag-cyan">MongoDB</span>
          <span class="source-tag">来源: packages/service/core/dataset/collection/schema.ts</span>
        </div>
      </div>
      <table class="data-table">
        <thead><tr><th>字段名</th><th>类型</th><th>描述</th></tr></thead>
        <tbody>
          <tr><td class="field">_id</td><td>ObjectId</td><td>主键</td></tr>
          <tr><td class="field">parentId</td><td>ObjectId</td><td>父级文件夹ID</td></tr>
          <tr><td class="field">teamId</td><td>ObjectId</td><td>团队ID</td></tr>
          <tr><td class="field">tmbId</td><td>ObjectId</td><td>成员ID</td></tr>
          <tr><td class="field">datasetId</td><td>ObjectId</td><td>所属知识库ID</td></tr>
          <tr><td class="field">type</td><td>String</td><td>集合类型: folder / virtual / file / link / externalFile / apiFile / images</td></tr>
          <tr><td class="field">name</td><td>String</td><td>名称</td></tr>
          <tr><td class="field">fileId</td><td>String</td><td>S3文件Key</td></tr>
          <tr><td class="field">rawLink</td><td>String</td><td>原始链接</td></tr>
          <tr><td class="field">apiFileId</td><td>String</td><td>API文件ID</td></tr>
          <tr><td class="field">externalFileId</td><td>String</td><td>外部文件ID</td></tr>
          <tr><td class="field">externalFileUrl</td><td>String</td><td>外部文件URL</td></tr>
          <tr><td class="field">tags</td><td>Array&lt;ObjectId&gt;</td><td>标签ID列表</td></tr>
          <tr><td class="field">rawTextLength</td><td>Number</td><td>原始文本长度</td></tr>
          <tr><td class="field">hashRawText</td><td>String</td><td>原始文本哈希 (去重)</td></tr>
          <tr><td class="field">chunkSize</td><td>Number</td><td>分块大小</td></tr>
          <tr><td class="field">chunkSplitter</td><td>String</td><td>自定义分隔符</td></tr>
          <tr><td class="field">trainingType</td><td>String</td><td>训练类型: chunk / qa / auto / imageParse</td></tr>
          <tr><td class="field">imageIndex</td><td>Boolean</td><td>是否启用图片索引</td></tr>
          <tr><td class="field">autoIndexes</td><td>Boolean</td><td>是否自动生成索引</td></tr>
          <tr><td class="field">qaPrompt</td><td>String</td><td>QA模式提示词</td></tr>
          <tr><td class="field">forbid</td><td>Boolean</td><td>是否禁用</td></tr>
          <tr><td class="field">createTime / updateTime</td><td>Date</td><td>时间戳</td></tr>
        </tbody>
      </table>
    </div>

    <!-- dataset_datas -->
    <div class="card">
      <div class="card-title-row">
        <h3 class="card-title"><span class="icon">◈</span> dataset_datas (数据块)</h3>
        <div>
          <span class="tag tag-green">MongoDB</span>
          <span class="source-tag">来源: packages/service/core/dataset/data/schema.ts</span>
        </div>
      </div>
      <table class="data-table">
        <thead><tr><th>字段名</th><th>类型</th><th>描述</th></tr></thead>
        <tbody>
          <tr><td class="field">_id</td><td>ObjectId</td><td>主键</td></tr>
          <tr><td class="field">teamId</td><td>ObjectId</td><td>团队ID</td></tr>
          <tr><td class="field">tmbId</td><td>ObjectId</td><td>成员ID</td></tr>
          <tr><td class="field">datasetId</td><td>ObjectId</td><td>知识库ID</td></tr>
          <tr><td class="field">collectionId</td><td>ObjectId</td><td>集合ID</td></tr>
          <tr><td class="field">q</td><td>String</td><td>主文本 (问题/内容)</td></tr>
          <tr><td class="field">a</td><td>String</td><td>补充文本 (答案/备注)</td></tr>
          <tr><td class="field">chunkIndex</td><td>Number</td><td>分块索引序号</td></tr>
          <tr><td class="field">indexes</td><td>Array&lt;Object&gt;</td><td>索引列表 {type, dataId, text} — type: default / custom / summary / question / image, dataId: 向量DB ID</td></tr>
          <tr><td class="field">fullTextToken</td><td>String</td><td>Jieba分词全文检索Token</td></tr>
          <tr><td class="field">imageId</td><td>String</td><td>图片S3 Key</td></tr>
          <tr><td class="field">imageDescMap</td><td>Object</td><td>图片描述映射</td></tr>
          <tr><td class="field">forbid</td><td>Boolean</td><td>是否禁用</td></tr>
          <tr><td class="field">rebuilding</td><td>Boolean</td><td>是否正在重建</td></tr>
          <tr><td class="field">history</td><td>Array&lt;Object&gt;</td><td>编辑历史 {q, a, updateTime}</td></tr>
          <tr><td class="field">createTime / updateTime</td><td>Date</td><td>时间戳</td></tr>
        </tbody>
      </table>
    </div>

    <!-- dataset_trainings -->
    <div class="card">
      <div class="card-title-row">
        <h3 class="card-title"><span class="icon">◈</span> dataset_trainings (训练队列)</h3>
        <div>
          <span class="tag tag-orange">MongoDB</span>
          <span class="source-tag">来源: packages/service/core/dataset/training/schema.ts</span>
        </div>
      </div>
      <table class="data-table">
        <thead><tr><th>字段名</th><th>类型</th><th>描述</th></tr></thead>
        <tbody>
          <tr><td class="field">_id</td><td>ObjectId</td><td>主键</td></tr>
          <tr><td class="field">teamId</td><td>ObjectId</td><td>团队ID</td></tr>
          <tr><td class="field">tmbId</td><td>ObjectId</td><td>成员ID</td></tr>
          <tr><td class="field">datasetId</td><td>ObjectId</td><td>知识库ID</td></tr>
          <tr><td class="field">collectionId</td><td>ObjectId</td><td>集合ID</td></tr>
          <tr><td class="field">mode</td><td>String</td><td>训练模式: parse / chunk / qa / auto / image / imageParse</td></tr>
          <tr><td class="field">q</td><td>String</td><td>主文本</td></tr>
          <tr><td class="field">a</td><td>String</td><td>补充文本</td></tr>
          <tr><td class="field">chunkIndex</td><td>Number</td><td>分块索引</td></tr>
          <tr><td class="field">indexSize</td><td>Number</td><td>索引大小</td></tr>
          <tr><td class="field">weight</td><td>Number</td><td>权重</td></tr>
          <tr><td class="field">indexes</td><td>Array</td><td>索引数据</td></tr>
          <tr><td class="field">retryCount</td><td>Number</td><td>重试次数 (默认5)</td></tr>
          <tr><td class="field">lockTime</td><td>Date</td><td>锁定时间 (乐观锁)</td></tr>
          <tr><td class="field">errorMsg</td><td>String</td><td>错误信息</td></tr>
          <tr><td class="field">billId</td><td>ObjectId</td><td>计费ID</td></tr>
          <tr><td class="field">expireAt</td><td>Date</td><td>过期时间 (TTL 7天)</td></tr>
        </tbody>
      </table>
    </div>

    <!-- dataset_data_texts -->
    <div class="card">
      <div class="card-title-row">
        <h3 class="card-title"><span class="icon">◈</span> dataset_data_texts (全文检索索引)</h3>
        <div>
          <span class="tag tag-purple">MongoDB</span>
          <span class="source-tag">来源: packages/service/core/dataset/data/dataTextSchema.ts</span>
        </div>
      </div>
      <table class="data-table">
        <thead><tr><th>字段名</th><th>类型</th><th>描述</th></tr></thead>
        <tbody>
          <tr><td class="field">_id</td><td>ObjectId</td><td>主键</td></tr>
          <tr><td class="field">teamId</td><td>ObjectId</td><td>团队ID</td></tr>
          <tr><td class="field">datasetId</td><td>ObjectId</td><td>知识库ID</td></tr>
          <tr><td class="field">collectionId</td><td>ObjectId</td><td>集合ID</td></tr>
          <tr><td class="field">dataId</td><td>ObjectId</td><td>关联数据块ID</td></tr>
          <tr><td class="field">fullTextToken</td><td>String</td><td>全文检索Token (Jieba分词)</td></tr>
          <tr class="index-row"><td class="field" colspan="3">Index: <code>{ teamId: 1, fullTextToken: 'text' }</code> — MongoDB文本索引</td></tr>
        </tbody>
      </table>
    </div>

    <!-- modeldata (PostgreSQL) -->
    <div class="card">
      <div class="card-title-row">
        <h3 class="card-title"><span class="icon">◈</span> modeldata (向量存储表)</h3>
        <div>
          <span class="tag tag-blue">PostgreSQL</span>
          <span class="source-tag">来源: packages/service/common/vectorDB/pg/index.ts</span>
        </div>
      </div>
      <table class="data-table">
        <thead><tr><th>字段名</th><th>类型</th><th>描述</th></tr></thead>
        <tbody>
          <tr><td class="field">id</td><td>BIGSERIAL</td><td>主键 (自增)</td></tr>
          <tr><td class="field">vector</td><td>VECTOR(1536)</td><td>嵌入向量 (1536维, 内积距离)</td></tr>
          <tr><td class="field">team_id</td><td>VARCHAR(50)</td><td>团队ID</td></tr>
          <tr><td class="field">dataset_id</td><td>VARCHAR(50)</td><td>知识库ID</td></tr>
          <tr><td class="field">collection_id</td><td>VARCHAR(50)</td><td>集合ID</td></tr>
          <tr><td class="field">createtime</td><td>TIMESTAMP</td><td>创建时间</td></tr>
          <tr class="index-row"><td class="field" colspan="3">Index: HNSW (m=32, ef_construction=128) — 向量索引</td></tr>
          <tr class="index-row"><td class="field" colspan="3">Index: team_id, dataset_id, collection_id — 过滤索引</td></tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
