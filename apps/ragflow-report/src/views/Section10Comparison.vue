<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§10 RAGFlow vs FastGPT vs MaxKB 深度对比</h2>
      <p>三大 RAG 开源框架全链路能力对比分析</p>
    </div>

    <!-- 10.1 系统架构对比 -->
    <div class="card">
      <div class="card-title"><span class="icon">🏗️</span> 10.1 系统架构对比</div>
      <table class="data-table">
        <thead><tr><th>维度</th><th>RAGFlow</th><th>FastGPT</th><th>MaxKB</th></tr></thead>
        <tbody>
          <tr><td><strong>后端语言</strong></td><td>Python 3.10+ (Flask/Quart)</td><td>Node.js / TypeScript (Next.js 16)</td><td>Python 3.11 (Django 5.2 + DRF)</td></tr>
          <tr><td><strong>前端框架</strong></td><td>React + UmiJS</td><td>Next.js 16.2 + React</td><td>Vue 3 + Element Plus + Pinia</td></tr>
          <tr><td><strong>元数据库</strong></td><td>MySQL (Peewee ORM)</td><td>MongoDB (41+ 集合, 4 数据库)</td><td>PostgreSQL 17 (Django ORM)</td></tr>
          <tr><td><strong>向量引擎</strong></td><td>ES / Infinity / OpenSearch / OceanBase (4种)</td><td>pgvector / Milvus / OceanBase / openGauss / SeekDB (5种)</td><td>仅 pgvector (1种)</td></tr>
          <tr><td><strong>任务队列</strong></td><td>Redis Streams (Consumer Group)</td><td>BullMQ (Redis)</td><td>Celery 5.5 + Redis</td></tr>
          <tr><td><strong>文件存储</strong></td><td>MinIO / S3 / Azure / OSS / GCS / OpenDAL (6种)</td><td>MinIO (S3 兼容)</td><td>PostgreSQL Large Objects (ZIP压缩)</td></tr>
          <tr><td><strong>部署方式</strong></td><td>Docker Compose (9 服务)</td><td>Docker Compose (5 服务)</td><td>Docker Compose (PG + Redis + App)</td></tr>
          <tr><td><strong>架构风格</strong></td><td>微服务 (API + Worker 分离)</td><td>Monorepo (pnpm workspace)</td><td>Django 单体 + Celery Worker</td></tr>
        </tbody>
      </table>
    </div>

    <!-- 10.2 知识库管理对比 -->
    <div class="card">
      <div class="card-title"><span class="icon">📚</span> 10.2 知识库管理对比</div>
      <table class="data-table">
        <thead><tr><th>维度</th><th>RAGFlow</th><th>FastGPT</th><th>MaxKB</th></tr></thead>
        <tbody>
          <tr><td><strong>数据模型</strong></td><td>Tenant → KB → Document → Chunk</td><td>Dataset → Collection → Data → Index[]</td><td>Folder(MPTT) → Knowledge → Document → Paragraph</td></tr>
          <tr><td><strong>存储分离</strong></td><td>元数据(MySQL) + 向量(ES/Infinity)</td><td>元数据(MongoDB) + 向量(PG/Milvus)</td><td>元数据+向量(PostgreSQL 统一存储)</td></tr>
          <tr><td><strong>知识库类型</strong></td><td>通用</td><td>通用</td><td>通用/Web站点/飞书/语雀/工作流 (5种)</td></tr>
          <tr><td><strong>权限模型</strong></td><td>me(私有) / team(团队) 二级</td><td>团队级别管理</td><td>WORKSPACE / SHARED 二级</td></tr>
          <tr><td><strong>配置粒度</strong></td><td>每个KB独立 Embedding + 分块策略</td><td>每个 Dataset 独立配置 vectorModel</td><td>每个KB独立 Embedding 模型</td></tr>
          <tr><td><strong>文件夹组织</strong></td><td>❌ 无文件夹</td><td>❌ 无文件夹</td><td>✅ MPTT 树形目录</td></tr>
          <tr><td><strong>GraphRAG</strong></td><td>✅ 实体/关系/社区三级检索</td><td>❌ 不支持</td><td>❌ 不支持</td></tr>
          <tr><td><strong>RAPTOR</strong></td><td>✅ 层级摘要增强</td><td>❌ 不支持</td><td>❌ 不支持</td></tr>
          <tr><td><strong>Mindmap</strong></td><td>✅ 思维导图生成</td><td>❌ 不支持</td><td>❌ 不支持</td></tr>
          <tr><td><strong>问题生成</strong></td><td>✅ LLM auto_questions</td><td>✅ LLM QA对 + 问题索引</td><td>✅ Celery异步 LLM 问题生成</td></tr>
          <tr><td><strong>命中测试</strong></td><td>❌ 无专门命中测试</td><td>❌ 无</td><td>✅ hit_test API</td></tr>
        </tbody>
      </table>
    </div>

    <!-- 10.3 文档解析对比 -->
    <div class="card">
      <div class="card-title"><span class="icon">📄</span> 10.3 文档解析对比</div>
      <table class="data-table">
        <thead><tr><th>维度</th><th>RAGFlow</th><th>FastGPT</th><th>MaxKB</th></tr></thead>
        <tbody>
          <tr><td><strong>PDF 解析</strong></td><td>6种策略：DeepDoc/plaintext/vision/mineru/docling/paddleocr/tcadp</td><td>pdfjs-dist(基础) + Doc2x/Textin(第三方)</td><td>pypdf 三策略递降：TOC→链接→字体分析</td></tr>
          <tr><td><strong>OCR</strong></td><td>✅ 自研 ONNX 模型 (DB检测 + CTC识别)</td><td>❌ 依赖第三方 (ocr-surya)</td><td>❌ 无 OCR</td></tr>
          <tr><td><strong>布局识别</strong></td><td>✅ YOLOv10 → 10种布局类型</td><td>❌ 无布局识别</td><td>❌ 无布局识别</td></tr>
          <tr><td><strong>表格识别</strong></td><td>✅ TSR模型 + 自动旋转 + 跨页合并</td><td>❌ 仅 HTML 表格边界保护</td><td>❌ PDF不支持表格</td></tr>
          <tr><td><strong>DOCX</strong></td><td>python-docx (原生)</td><td>mammoth → HTML → turndown → MD</td><td>python-docx → MD (样式+字号标题检测)</td></tr>
          <tr><td><strong>PPTX</strong></td><td>python-pptx (原生)</td><td>XML 提取 (纯文本)</td><td>❌ 不支持</td></tr>
          <tr><td><strong>XLSX</strong></td><td>openpyxl (原生)</td><td>node-xlsx + CUSTOM_SPLIT_SIGN</td><td>openpyxl → MD 表格</td></tr>
          <tr><td><strong>HTML</strong></td><td>BeautifulSoup5</td><td>cheerio → turndown</td><td>BeautifulSoup + markdownify</td></tr>
          <tr><td><strong>音频</strong></td><td>✅ ASR 转录</td><td>✅ STT (whisper-1)</td><td>❌ 不支持</td></tr>
          <tr><td><strong>图片</strong></td><td>✅ OCR + Vision LLM</td><td>✅ VLM 描述 (Plus版)</td><td>❌ 无图片内容提取</td></tr>
          <tr><td><strong>ZIP打包</strong></td><td>❌ 不支持</td><td>❌ 不支持</td><td>✅ 递归解压+委托内部handler</td></tr>
          <tr><td><strong>自研模型</strong></td><td>✅ 6个 ONNX 模型</td><td>❌ 无自研模型</td><td>❌ 无自研模型</td></tr>
          <tr><td><strong>文档去重</strong></td><td>❌ 仅文件名去重</td><td>❌ 无</td><td>✅ SHA256 文件级去重</td></tr>
        </tbody>
      </table>
      <div class="highlight-block">
        <strong>结论</strong>：RAGFlow 在文档解析能力上绝对领先（自研ONNX模型链 + 6种PDF策略）。MaxKB 的 PDF 三策略递降在无OCR场景下表现不错，但缺乏OCR是硬伤。FastGPT 最弱，主要依赖 pdfjs-dist 基础文本提取。
      </div>
    </div>

    <!-- 10.4 数据清洗对比 -->
    <div class="card">
      <div class="card-title"><span class="icon">🧹</span> 10.4 数据清洗对比</div>
      <table class="data-table">
        <thead><tr><th>维度</th><th>RAGFlow</th><th>FastGPT</th><th>MaxKB</th></tr></thead>
        <tbody>
          <tr><td><strong>编码检测</strong></td><td>chardet + 60种编码兜底</td><td>iconv-lite 编码检测</td><td>charset_normalizer</td></tr>
          <tr><td><strong>文本规范化</strong></td><td>全角→半角 / 繁体→简体 / 多余空格移除</td><td>trim() / 中文空格 / \r\n统一 / 控制字符移除</td><td>\r\n标准化 / 空白压缩 / #标记移除 / 制表符移除</td></tr>
          <tr><td><strong>噪声移除</strong></td><td>HTML标签清理 / 控制字符 / 目录移除</td><td>页眉页脚过滤(5%) / 空白Token合并 / 段落检测</td><td>HTML锚点移除 / Emoji移除(嵌入阶段) / Markdown标记清理</td></tr>
          <tr><td><strong>代码块保护</strong></td><td>❌ 无专门保护</td><td>❌ 无专门保护</td><td>✅ mask_code_blocks 遮蔽代码内容防误识别</td></tr>
          <tr><td><strong>语言检测</strong></td><td>中英文自动检测</td><td>无专门语言检测</td><td>无专门语言检测</td></tr>
          <tr><td><strong>NLP预处理</strong></td><td>rag_tokenizer 分词 + 停用词 + 同义词扩展</td><td>Jieba 分词 (@node-rs/jieba, Rust实现)</td><td>jieba 关键词提取</td></tr>
          <tr><td><strong>去重</strong></td><td>xxhash chunk ID</td><td>哈希 q+a 去重</td><td>SHA256 文件级去重</td></tr>
        </tbody>
      </table>
    </div>

    <!-- 10.5 文本分块对比 -->
    <div class="card">
      <div class="card-title"><span class="icon">✂️</span> 10.5 文本分块对比</div>
      <table class="data-table">
        <thead><tr><th>维度</th><th>RAGFlow</th><th>FastGPT</th><th>MaxKB</th></tr></thead>
        <tbody>
          <tr><td><strong>策略数量</strong></td><td>15种专用分块器</td><td>12+条优先级递归规则</td><td>3种策略：标题树/智能分割/字符硬分割</td></tr>
          <tr><td><strong>核心算法</strong></td><td>各策略独立实现 (naive/book/paper/laws/qa/table/...)</td><td>commonSplit() 递归优先级链</td><td>SplitModel 标题树递归 + smart_split_paragraph</td></tr>
          <tr><td><strong>分块粒度</strong></td><td>token 数 (默认512)</td><td>字符数 (默认800)</td><td>字符数 (默认limit=100000, 子块256)</td></tr>
          <tr><td><strong>子分块</strong></td><td>❌ 无子分块概念</td><td>❌ 无子分块概念</td><td>✅ chunks[] 数组 (256字符子块)</td></tr>
          <tr><td><strong>Overlap</strong></td><td>✅ 0-90% 可配置</td><td>✅ 后续步骤允许块间重叠</td><td>❌ 无重叠机制</td></tr>
          <tr><td><strong>Markdown感知</strong></td><td>❌ 无专门 Markdown 标题继承</td><td>✅ MD Header 优先级 + 标题层级继承</td><td>✅ H1-H6 正则标题树解析</td></tr>
          <tr><td><strong>代码块保护</strong></td><td>❌ 无专门保护</td><td>✅ ``` 围栏计数保护</td><td>✅ mask_code_blocks 代码遮蔽</td></tr>
          <tr><td><strong>表格感知</strong></td><td>✅ 表格类型分块器 + 上下文附加</td><td>✅ HTML 表格边界保护</td><td>✅ Markdown 表格保留</td></tr>
          <tr><td><strong>场景优化</strong></td><td>✅ 论文/法律/书籍/简历/邮件/演示文稿/音频...</td><td>❌ 通用递归分割</td><td>❌ 通用分割，无场景专用策略</td></tr>
          <tr><td><strong>自动增强</strong></td><td>✅ LLM关键词/问题/元数据生成</td><td>✅ LLM QA对 + 摘要索引 + 问题索引</td><td>✅ LLM 问题生成 (Celery异步)</td></tr>
          <tr><td><strong>Token计数</strong></td><td>tiktoken (cl100k_base)</td><td>getTextValidLength (非空白字符)</td><td>字符长度 (非Token)</td></tr>
        </tbody>
      </table>
      <div class="highlight-block">
        <strong>结论</strong>：RAGFlow 的 15种专用分块器在场景覆盖上绝对领先。FastGPT 的递归优先级链最灵活（12+规则）。MaxKB 的标题树递归解析+子分块系统是独特设计，但策略数量最少。
      </div>
    </div>

    <!-- 10.6 向量化对比 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔢</span> 10.6 向量化对比</div>
      <table class="data-table">
        <thead><tr><th>维度</th><th>RAGFlow</th><th>FastGPT</th><th>MaxKB</th></tr></thead>
        <tbody>
          <tr><td><strong>Embedding 提供商</strong></td><td>35+ (OpenAI/Azure/Cohere/Jina/通义/智谱/Ollama/TEI...)</td><td>主要 OpenAI text-embedding-3-small</td><td>14家 (OpenAI/Azure/Ollama/Gemini/千帆/百炼/Bedrock/火山/混元/SiliconCloud/Xinference/VLLM...)</td></tr>
          <tr><td><strong>向量引擎</strong></td><td>4种 (ES/Infinity/OpenSearch/OceanBase)</td><td>5种 (pgvector/Milvus/OceanBase/openGauss/SeekDB)</td><td>1种 (仅 pgvector)</td></tr>
          <tr><td><strong>向量维度</strong></td><td>动态 (由模型决定)</td><td>固定 1536 维</td><td>由模型决定</td></tr>
          <tr><td><strong>距离度量</strong></td><td>cosine</td><td>cosine (HNSW)</td><td>cosine (pgvector &lt;=&gt;)</td></tr>
          <tr><td><strong>本地部署</strong></td><td>✅ TEI / Ollama / Xinference / VLLM</td><td>❌ 无本地方案</td><td>✅ Ollama / Xinference / VLLM</td></tr>
          <tr><td><strong>多向量索引</strong></td><td>❌ 每个 chunk 一个向量</td><td>✅ 5种索引类型 (default/custom/summary/question/image)</td><td>❌ 段落+问题双源索引</td></tr>
          <tr><td><strong>双存储</strong></td><td>—</td><td>—</td><td>✅ VectorField + SearchVectorField (pgvector + tsvector)</td></tr>
          <tr><td><strong>任务去重</strong></td><td>—</td><td>—</td><td>✅ QueueOnce (celery-once)</td></tr>
          <tr><td><strong>模型缓存</strong></td><td>—</td><td>—</td><td>✅ ModelManage (8h TTL)</td></tr>
        </tbody>
      </table>
      <div class="highlight-block">
        <strong>结论</strong>：RAGFlow 在模型生态广度上碾压（35+提供商）。MaxKB 的 14家提供商和本地部署支持仅次于 RAGFlow。FastGPT 的多向量索引策略仍是独有亮点。MaxKB 的 pgvector+tsvector 双存储设计简洁高效。
      </div>
    </div>

    <!-- 10.7 检索系统对比 -->
    <div class="card">
      <div class="card-title"><span class="icon">🔍</span> 10.7 检索系统对比</div>
      <table class="data-table">
        <thead><tr><th>维度</th><th>RAGFlow</th><th>FastGPT</th><th>MaxKB</th></tr></thead>
        <tbody>
          <tr><td><strong>检索方式</strong></td><td>混合检索 (5%文本 + 95%向量)</td><td>双路检索 + RRF 融合</td><td>三种模式：向量/全文/混合</td></tr>
          <tr><td><strong>融合算法</strong></td><td>weighted_sum (固定权重)</td><td>RRF (Reciprocal Rank Fusion)</td><td>简单加性融合 (非归一化)</td></tr>
          <tr><td><strong>全文检索</strong></td><td>ES query_string + 7级字段权重</td><td>MongoDB $text + Jieba 分词</td><td>PostgreSQL tsvector + jieba 分词</td></tr>
          <tr><td><strong>查询扩展</strong></td><td>同义词扩展 + 词权重 (BM25-like)</td><td>LLM 10候选 → 亚模优化 → Top3</td><td>❌ 无查询扩展</td></tr>
          <tr><td><strong>Rerank</strong></td><td>18+ 提供商 (对话管道内置)</td><td>外部 Cross-Encoder + rerankWeight</td><td>8提供商 (仅工作流模式可用)</td></tr>
          <tr><td><strong>检索模式</strong></td><td>单一混合模式</td><td>3种: embedding/fullTextRecall/mixedRecall</td><td>3种: embedding/keywords/blend</td></tr>
          <tr><td><strong>候选数量</strong></td><td>top_k=1024, top_n=6</td><td>embedding:100 / fullText:100 / mixed:80+60</td><td>SQL LIMIT 可配</td></tr>
          <tr><td><strong>GraphRAG</strong></td><td>✅ 实体/关系/社区三级检索</td><td>❌ 不支持</td><td>❌ 不支持</td></tr>
          <tr><td><strong>评分溯源</strong></td><td>similarity_threshold + rank_feature</td><td>4种评分 (embedding/fullText/reRank/rrf)</td><td>comprehensive_score (1-cosine_distance)</td></tr>
          <tr><td><strong>去重策略</strong></td><td>—</td><td>哈希 q+a 去重</td><td>DISTINCT ON (paragraph_id) 段落去重</td></tr>
          <tr><td><strong>相似度阈值</strong></td><td>0.2 (可配)</td><td>可配</td><td>0.65 (硬编码)</td></tr>
          <tr><td><strong>混合检索质量</strong></td><td>⭐⭐⭐⭐</td><td>⭐⭐⭐⭐</td><td>⭐⭐ (非归一化加性融合)</td></tr>
        </tbody>
      </table>
      <div class="highlight-block">
        <strong>结论</strong>：RAGFlow 的 GraphRAG + 7级字段权重 + 18+Reranker(内置) 检索能力最强。FastGPT 的 RRF + 亚模查询扩展设计最精巧。MaxKB 检索功能最基础——混合检索使用简单加性融合（非归一化），重排序仅在高级工作流模式下可用，且相似度阈值硬编码。
      </div>
    </div>

    <!-- 10.8 综合能力评分对比 -->
    <div class="card">
      <div class="card-title"><span class="icon">📊</span> 10.8 综合能力评分对比</div>
      <div ref="chartRef" class="chart-container"></div>
      <table class="data-table">
        <thead><tr><th>能力维度</th><th>RAGFlow</th><th>FastGPT</th><th>MaxKB</th><th>说明</th></tr></thead>
        <tbody>
          <tr v-for="item in scoreData" :key="item.dimension">
            <td><strong>{{ item.dimension }}</strong></td>
            <td>{{ item.ragflow }}</td>
            <td>{{ item.fastgpt }}</td>
            <td>{{ item.maxkb }}</td>
            <td>{{ item.desc }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 10.9 核心差异总结 -->
    <div class="card">
      <div class="card-title"><span class="icon">🏆</span> 10.9 核心差异总结</div>
      <div class="two-col">
        <div class="card">
          <div class="card-title"><span class="icon">🟢</span> RAGFlow 独有优势</div>
          <ul class="feature-list">
            <li v-for="item in ragflowAdvantages" :key="item">{{ item }}</li>
          </ul>
        </div>
        <div class="card">
          <div class="card-title"><span class="icon">🔵</span> FastGPT 独有优势</div>
          <ul class="feature-list">
            <li v-for="item in fastgptAdvantages" :key="item">{{ item }}</li>
          </ul>
        </div>
      </div>
      <div class="card">
        <div class="card-title"><span class="icon">🟡</span> MaxKB 独有优势</div>
        <ul class="feature-list">
          <li v-for="item in maxkbAdvantages" :key="item">{{ item }}</li>
        </ul>
      </div>
    </div>

    <!-- 10.10 共同不足对比 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚠️</span> 10.10 共同不足对比</div>
      <table class="data-table">
        <thead><tr><th>不足</th><th>RAGFlow</th><th>FastGPT</th><th>MaxKB</th></tr></thead>
        <tbody>
          <tr><td><strong>文档级去重</strong></td><td>❌ 仅 chunk 级 xxhash</td><td>✅ 哈希 q+a 去重</td><td>✅ SHA256 文件级去重</td></tr>
          <tr><td><strong>样板/噪声检测</strong></td><td>❌ 无</td><td>❌ 无</td><td>❌ 无</td></tr>
          <tr><td><strong>语义级分块</strong></td><td>❌ 基于 token 数</td><td>❌ 基于字符数</td><td>❌ 基于字符数</td></tr>
          <tr><td><strong>动态检索权重</strong></td><td>❌ fusion weights 硬编码</td><td>✅ 可配置</td><td>❌ 简单加性融合</td></tr>
          <tr><td><strong>模型切换成本</strong></td><td>❌ 需重建索引</td><td>❌ 固定1536维缓解</td><td>❌ 需重建索引</td></tr>
          <tr><td><strong>OCR (MaxKB/FastGPT)</strong></td><td>✅ 自研模型</td><td>❌ 依赖第三方</td><td>❌ 完全缺失</td></tr>
          <tr><td><strong>表格提取 (FastGPT/MaxKB)</strong></td><td>✅ TSR模型</td><td>❌ 仅边界保护</td><td>❌ PDF不支持表格</td></tr>
          <tr><td><strong>混合检索质量 (MaxKB)</strong></td><td>⭐ 加权融合</td><td>⭐ RRF融合</td><td>⚠️ 非归一化加性融合</td></tr>
        </tbody>
      </table>
    </div>

    <!-- 10.11 选型建议 -->
    <div class="card">
      <div class="card-title"><span class="icon">🎯</span> 10.11 选型建议</div>
      <table class="data-table">
        <thead><tr><th>场景</th><th>推荐</th><th>理由</th></tr></thead>
        <tbody>
          <tr v-for="item in recommendations" :key="item.scene">
            <td><strong>{{ item.scene }}</strong></td>
            <td><span class="tag">{{ item.pick }}</span></td>
            <td>{{ item.reason }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

// 综合评分数据
const scoreData = ref([
  { dimension: '知识库管理', ragflow: '⭐⭐⭐⭐ (4)', fastgpt: '⭐⭐⭐ (3)', maxkb: '⭐⭐⭐⭐ (4)', desc: 'RAGFlow: GraphRAG; MaxKB: 5种KB类型+文件夹; FastGPT: 四层模型' },
  { dimension: '文档上传', ragflow: '⭐⭐⭐⭐ (4)', fastgpt: '⭐⭐⭐ (3)', maxkb: '⭐⭐⭐⭐ (4)', desc: 'RAGFlow: 6种存储; MaxKB: SHA256去重+ZIP压缩; FastGPT: 仅MinIO' },
  { dimension: '文档解析', ragflow: '⭐⭐⭐⭐⭐ (5)', fastgpt: '⭐⭐⭐ (3)', maxkb: '⭐⭐⭐⭐ (4)', desc: 'RAGFlow: 自研ONNX; MaxKB: PDF三策略; FastGPT: pdfjs-dist' },
  { dimension: '数据清洗', ragflow: '⭐⭐⭐ (3)', fastgpt: '⭐⭐⭐ (3)', maxkb: '⭐⭐⭐ (3)', desc: '三者持平: 各有特色' },
  { dimension: '文本分块', ragflow: '⭐⭐⭐⭐⭐ (5)', fastgpt: '⭐⭐⭐⭐ (4)', maxkb: '⭐⭐⭐⭐ (4)', desc: 'RAGFlow: 15种策略; FastGPT: 12+规则; MaxKB: 标题树+子分块' },
  { dimension: '向量化', ragflow: '⭐⭐⭐⭐⭐ (5)', fastgpt: '⭐⭐⭐⭐ (4)', maxkb: '⭐⭐⭐⭐ (4)', desc: 'RAGFlow: 35+提供商; MaxKB: 14家; FastGPT: 多向量索引' },
  { dimension: '检索', ragflow: '⭐⭐⭐⭐ (4)', fastgpt: '⭐⭐⭐⭐ (4)', maxkb: '⭐⭐⭐ (3)', desc: 'RAGFlow: GraphRAG; FastGPT: RRF; MaxKB: 基础混合' },
  { dimension: '总分', ragflow: '30/35', fastgpt: '25/35', maxkb: '26/35', desc: '—' }
])

// RAGFlow 独有优势
const ragflowAdvantages = ref([
  '深度文档理解 (DeepDoc)：自研 OCR + 布局识别 + 表格结构识别 ONNX 模型链，最大技术壁垒',
  '6 种 PDF 解析策略：DeepDoc / plaintext / vision / MinerU / Docling / PaddleOCR / TCADP',
  '15 种专用分块器：针对论文/法律/书籍/简历/邮件等场景深度优化',
  'GraphRAG 支持：实体/关系/社区三级知识图谱检索，支持多跳推理',
  '35+ Embedding 提供商：无与伦比的模型生态，支持本地部署',
  '18+ Reranker (内置)：对话管道中直接可用，非工作流限定'
])

// FastGPT 独有优势
const fastgptAdvantages = ref([
  '多向量索引策略：同一 chunk 生成 default/summary/question/image 多种索引',
  '亚模优化查询扩展：LLM 10候选 → Lazy Greedy + 余弦相似度 → Top3',
  'RRF 融合检索：标准 Reciprocal Rank Fusion，比固定权重更灵活',
  'Markdown 感知分块：标题层级继承 + 代码块围栏保护',
  'TypeScript 全栈：Monorepo 架构，前后端类型共享',
  '评分溯源：4种评分类型完整追踪，结果可解释性最强'
])

// MaxKB 独有优势
const maxkbAdvantages = ref([
  '架构最简洁：Django + PG + Redis 三件套，部署运维成本最低',
  '知识库类型最丰富：通用/Web站点/飞书/语雀/工作流 5种类型',
  '树形文件夹组织：MPTT 树形目录管理知识库，层级清晰',
  '工作流引擎：37种节点类型，灵活编排 RAG 管道',
  '文件级去重：SHA256 + Large Object 共享存储，节省空间',
  'PDF 三策略递降：TOC→链接→字体分析，无需OCR也能提取结构',
  'pgvector + tsvector 双存储：同一 Embedding 表同时存储向量和全文索引'
])

// 选型建议
const recommendations = ref([
  { scene: '复杂 PDF/扫描件/学术论文', pick: 'RAGFlow', reason: 'DeepDoc 自研模型链 + 6种PDF策略' },
  { scene: '法律/合规文档', pick: 'RAGFlow', reason: 'laws 分块器专用优化' },
  { scene: '技术文档/代码仓库', pick: 'FastGPT', reason: 'Markdown 感知 + 代码块保护' },
  { scene: '多语言/多模型需求', pick: 'RAGFlow', reason: '35+ Embedding + 18+ Reranker' },
  { scene: '快速部署/轻量场景', pick: 'MaxKB', reason: 'Django+PG+Redis 三件套，架构最简洁' },
  { scene: '知识图谱/深度推理', pick: 'RAGFlow', reason: 'GraphRAG 实体/关系/社区检索' },
  { scene: '企业级权限管理', pick: 'RAGFlow', reason: 'me/team 权限 + 6种存储后端' },
  { scene: '多角度内容检索', pick: 'FastGPT', reason: '多向量索引策略 (summary/question)' },
  { scene: '飞书/语雀文档集成', pick: 'MaxKB', reason: '原生支持飞书+语雀知识库类型' },
  { scene: '工作流编排/Agent', pick: 'MaxKB', reason: '37种工作流节点，灵活编排' },
  { scene: '中小企业快速上线', pick: 'MaxKB', reason: '架构简单、中文优化、部署成本低' },
  { scene: '高精度场景(学术论文)', pick: 'RAGFlow', reason: '论文专用分块器(标题频率+两栏检测)' },
  { scene: 'Web站点知识采集', pick: 'MaxKB', reason: '原生Web知识库 + CSS选择器爬取' }
])

// ECharts 分组柱状图
const chartRef = ref(null)
let chartInstance = null

onMounted(() => {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['RAGFlow', 'FastGPT', 'MaxKB'],
      textStyle: {
        color: '#e2e8f0',
        fontSize: 13
      },
      top: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '40px',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['知识库管理', '文档上传', '文档解析', '数据清洗', '文本分块', '向量化', '检索'],
      axisLabel: {
        color: '#e2e8f0',
        fontSize: 12
      },
      axisLine: {
        lineStyle: { color: 'rgba(148, 163, 184, 0.2)' }
      }
    },
    yAxis: {
      type: 'value',
      max: 5,
      min: 0,
      interval: 1,
      axisLabel: {
        color: '#e2e8f0',
        fontSize: 12
      },
      splitLine: {
        lineStyle: { color: 'rgba(148, 163, 184, 0.1)' }
      }
    },
    series: [
      {
        name: 'RAGFlow',
        type: 'bar',
        data: [4, 4, 5, 3, 5, 5, 4],
        itemStyle: { color: '#10b981' },
        barMaxWidth: 30
      },
      {
        name: 'FastGPT',
        type: 'bar',
        data: [3, 3, 3, 3, 4, 4, 4],
        itemStyle: { color: '#3b82f6' },
        barMaxWidth: 30
      },
      {
        name: 'MaxKB',
        type: 'bar',
        data: [4, 4, 4, 3, 4, 4, 3],
        itemStyle: { color: '#f59e0b' },
        barMaxWidth: 30
      }
    ]
  })
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})

function handleResize() {
  chartInstance?.resize()
}
</script>
