<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§6 图片索引</h2>
      <p>多模态图片处理与索引管道</p>
    </div>

    <div class="source-ref-list">
      <div class="ref-title">&#128204; 核心源码</div>
      <div class="source-ref-item"><span class="ref-file">packages/service/core/dataset/image/schema.ts</span> <span class="ref-desc">GridFS图片Schema</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/core/dataset/image/controller.ts</span> <span class="ref-desc">GridFS图片读取控制器</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/common/s3/utils.ts</span> <span class="ref-desc">S3上传工具(uploadImage2S3Bucket)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/common/file/read/utils.ts</span> <span class="ref-desc">文档图片提取(readFileContentByBuffer)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/core/dataset/collection/utils.ts</span> <span class="ref-desc">训练模式判定(getTrainingModeByCollection)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/core/dataset/training/controller.ts</span> <span class="ref-desc">训练队列VLM模型解析</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/core/ai/model.ts</span> <span class="ref-desc">VLM模型配置(getVlmModel)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/core/dataset/data/controller.ts</span> <span class="ref-desc">图片数据格式化(formatDatasetDataValue)</span></div>
    </div>

    <!-- 图片处理双路径流程 -->
    <div class="card">
      <div class="card-title"><span class="icon">&#128247;</span> 图片处理双路径流程</div>
      <div class="flow-diagram">
        <h4 style="color:var(--accent-cyan);margin-bottom:12px;">路径A: 图片数据集 (imageParse模式)</h4>
        <div class="flow-steps">
          <div class="flow-step">用户上传图片</div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step primary">S3存储(7天TTL)</div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step">创建Collection</div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step">Training Queue<br><span class="tag tag-purple">imageParse</span></div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step primary">Plus VLM处理<br>(视觉模型描述)</div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step">Embedding向量化</div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step primary">PG向量存储<br>MongoDB元数据</div>
        </div>
        <h4 style="color:var(--accent-orange);margin-top:20px;margin-bottom:12px;">路径B: 文档图片提取 (image模式)</h4>
        <div class="flow-steps">
          <div class="flow-step">DOCX/PDF文档</div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step primary">Worker解析<br>提取base64图片</div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step">S3上传图片<br>UUID替换为URL</div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step">文本分块<br>携带imageIdList</div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step primary">Plus VLM<br>生成imageDescMap</div><span class="flow-arrow">&rarr;</span>
          <div class="flow-step">Embedding+存储</div>
        </div>
      </div>
    </div>

    <div class="two-col">
      <!-- 图片提取方式 -->
      <div class="card">
        <div class="card-title"><span class="icon">&#128295;</span> 图片提取方式</div>
        <table class="data-table">
          <thead>
            <tr><th>文档类型</th><th>提取方式</th><th>处理方法</th></tr>
          </thead>
          <tbody>
            <tr><td>DOCX</td><td>mammoth转base64</td><td>UUID替换src属性, 上传S3</td></tr>
            <tr><td>PDF(Doc2x)</td><td>API解析</td><td>Markdown+图片提取, S3存储</td></tr>
            <tr><td>PDF(Textin)</td><td>XParse API</td><td>PDF&#8594;Markdown, 表格+图片</td></tr>
            <tr><td>Markdown</td><td>正则匹配</td><td>![](url)提取, 匹配mdImg()</td></tr>
          </tbody>
        </table>
      </div>

      <!-- 图片数据模型 -->
      <div class="card">
        <div class="card-title"><span class="icon">&#128451;</span> 图片数据模型</div>
        <ul class="feature-list">
          <li><strong>imageId：</strong>S3对象存储密钥</li>
          <li><strong>imageDescMap：</strong>图片描述映射 Record&lt;string, string&gt;</li>
          <li><strong>GridFS存储：</strong>dataset_image.files, 含metadata(teamId, datasetId, collectionId)</li>
          <li><strong>S3签名URL：</strong>90天有效期预览链接, JWT认证</li>
          <li><strong>VLM模式：</strong>imageParse使用视觉语言模型自动生成图片描述</li>
        </ul>
      </div>
    </div>

    <!-- 纯图片知识库 -->
    <div class="card">
      <div class="card-title"><span class="icon">&#128444;</span> 纯图片知识库</div>
      <div class="highlight-block">
        图片集合(DatasetCollectionTypeEnum.images)支持纯图片知识库，每张图片作为一个数据块，通过VLM生成语义描述后进行向量化索引。
      </div>
    </div>

    <!-- 图片上传S3源码 -->
    <div class="collapsible-code">
      <div class="collapsible-header" onclick="this.querySelector('.toggle-icon').classList.toggle('open');this.nextElementSibling.classList.toggle('open')">
        <span class="title"><span class="icon">&#128196;</span> 图片上传S3源码 (create/images.ts)</span>
        <span class="toggle-icon">&#9654;</span>
      </div>
      <div class="collapsible-body">
        <div class="code-block">
          <span class="lang-tag">TypeScript</span>
          <pre><span class="code-comment">// projects/app/src/pages/api/core/dataset/collection/create/images.ts</span>
<span class="code-comment">// 批量上传图片到S3并创建数据集集合</span>
<span class="code-keyword">const</span> imageIds = <span class="code-keyword">await</span> Promise.<span class="code-func">all</span>(
  result.fileMetadata.<span class="code-func">map</span>(<span class="code-keyword">async</span> (file) => {
    <span class="code-keyword">const</span> filename = path.<span class="code-func">basename</span>(file.filename);
    <span class="code-keyword">const</span> { fileKey } = <span class="code-func">getFileS3Key.dataset</span>({
      datasetId, filename
    });
    <span class="code-keyword">return</span> <span class="code-func">uploadImage2S3Bucket</span>(<span class="code-string">'private'</span>, {
      base64Img: (<span class="code-keyword">await</span> fs.promises.<span class="code-func">readFile</span>(file.path))
                        .<span class="code-func">toString</span>(<span class="code-string">'base64'</span>),
      uploadKey: fileKey,
      mimetype: file.mimetype,
      filename,
      expiredTime: <span class="code-func">addDays</span>(<span class="code-keyword">new</span> Date(), <span class="code-number">7</span>)  <span class="code-comment">// 7天临时TTL</span>
    });
  })
);</pre>
        </div>
      </div>
    </div>

    <!-- VLM模型解析 + 训练队列推送源码 -->
    <div class="collapsible-code">
      <div class="collapsible-header" onclick="this.querySelector('.toggle-icon').classList.toggle('open');this.nextElementSibling.classList.toggle('open')">
        <span class="title"><span class="icon">&#129302;</span> VLM模型解析 + 训练队列推送源码</span>
        <span class="toggle-icon">&#9654;</span>
      </div>
      <div class="collapsible-body">
        <div class="code-block">
          <span class="lang-tag">TypeScript</span>
          <pre><span class="code-comment">// packages/service/core/dataset/training/controller.ts</span>
<span class="code-comment">// image/imageParse模式的VLM模型解析</span>
<span class="code-keyword">if</span> (mode === TrainingModeEnum.image ||
    mode === TrainingModeEnum.imageParse) {
  <span class="code-keyword">const</span> vllmModelData = <span class="code-func">getVlmModel</span>(vlmModel);
  <span class="code-keyword">if</span> (!vllmModelData) {
    <span class="code-keyword">return</span> Promise.<span class="code-func">reject</span>(
      i18nT(<span class="code-string">'common:error_vlm_not_config'</span>)
    );
  }
  <span class="code-keyword">return</span> {
    maxToken: <span class="code-func">getLLMMaxChunkSize</span>(vllmModelData),
    model: vllmModelData.model,  <span class="code-comment">// 视觉语言模型</span>
    weight: <span class="code-number">0</span>                    <span class="code-comment">// 最低优先级</span>
  };
}

<span class="code-comment">// packages/service/core/ai/model.ts</span>
<span class="code-comment">// 从全局模型列表中获取VLM模型</span>
<span class="code-keyword">export const</span> <span class="code-func">getVlmModel</span> = (vlmModel?: <span class="code-type">string</span>) => {
  <span class="code-keyword">return</span> global.llmModels.<span class="code-func">find</span>(
    m => m.model === (vlmModel || global.systemDefaultModel?.datasetImageLLM)
  ) || global.llmModels.<span class="code-func">find</span>(m => m.vision);
};</pre>
        </div>
      </div>
    </div>

    <!-- 图片描述与格式化源码 -->
    <div class="card">
      <div class="card-title"><span class="icon">&#9881;</span> 图片描述与格式化源码</div>
      <div class="code-block">
        <span class="lang-tag">TypeScript</span>
        <pre><span class="code-comment">// packages/service/core/dataset/data/controller.ts</span>
<span class="code-comment">// formatDatasetDataValue: 替换图片Markdown为描述文本</span>
<span class="code-keyword">export function</span> <span class="code-func">formatDatasetDataValue</span>({ q, a, imageId, imageDescMap }) {
  <span class="code-keyword">if</span> (!imageId || !imageDescMap) <span class="code-keyword">return</span> { q, a };
  
  <span class="code-comment">// 替换图片引用为描述</span>
  Object.entries(imageDescMap).forEach(([key, desc]) => {
    q = q.replaceAll(key, desc || <span class="code-string">'[图片]'</span>);
    a = a?.replaceAll(key, desc || <span class="code-string">'[图片]'</span>);
  });
  <span class="code-keyword">return</span> { q, a };
}

<span class="code-comment">// S3签名预览URL (90天有效期)</span>
<span class="code-keyword">const</span> previewUrl = <span class="code-func">replaceS3KeyToPreviewUrl</span>(
  text, <span class="code-func">addDays</span>(<span class="code-keyword">new</span> Date(), <span class="code-number">90</span>)
);</pre>
      </div>
    </div>

    <!-- Plus-only processing note -->
    <div class="highlight-block" style="font-size:0.85rem;">
      <strong>&#9888;&#65039; 重要发现:</strong> <code>image</code> 和 <code>imageParse</code> 训练模式的VLM描述生成在开源代码中<strong>未实现</strong>。MongoDB Watch Stream (training/utils.ts) 仅处理 parse/chunk/qa 三种模式。VLM处理由 FastGPT Plus 商业版服务器完成。开源版本仅完成: S3图片存储、训练队列条目创建、计费记录、结果格式化展示。
    </div>
  </div>
</template>
