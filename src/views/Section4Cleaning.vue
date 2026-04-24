<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§4 数据清洗</h2>
      <p>多格式文档清洗策略 — PDF、DOCX 及通用文本的规范化处理流程</p>
    </div>

    <div class="source-ref-list">
      <div class="ref-title">&#128204; 核心源码</div>
      <div class="source-ref-item"><span class="ref-file">packages/service/common/file/read/utils.ts</span> <span class="ref-desc">文件读取编排(readFileContentByBuffer)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/worker/readFile/extension/pdf.ts</span> <span class="ref-desc">PDF头尾过滤(top5%/bottom5%)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/worker/htmlStr2Md/utils.ts</span> <span class="ref-desc">HTML清理(turndown+base64提取)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/global/common/string/textSplitter.ts</span> <span class="ref-desc">文本清理(空白/特殊字符)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/global/common/string/markdown.ts</span> <span class="ref-desc">Markdown处理(simpleMarkdownText)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/common/string/jieba/index.ts</span> <span class="ref-desc">中文分词(停用词过滤)</span></div>
    </div>

    <div class="two-col">
      <!-- PDF清洗策略 -->
      <div class="card">
        <div class="card-title"><span class="icon">📄</span> PDF清洗策略</div>
        <ul class="feature-list">
          <li v-for="f in pdfStrategies" :key="f.title">
            <strong>{{ f.title }}：</strong>{{ f.desc }}
          </li>
        </ul>
      </div>

      <!-- DOCX清洗策略 -->
      <div class="card">
        <div class="card-title"><span class="icon">📝</span> DOCX清洗策略</div>
        <ul class="feature-list">
          <li v-for="f in docxStrategies" :key="f.title">
            <strong>{{ f.title }}：</strong>{{ f.desc }}
          </li>
        </ul>
      </div>
    </div>

    <div class="collapsible-code">
      <div class="collapsible-header" onclick="this.querySelector('.toggle-icon').classList.toggle('open');this.nextElementSibling.classList.toggle('open')">
        <span class="title"><span class="icon">&#128196;</span> PDF清洗源码 (页眉页脚过滤)</span>
        <span class="toggle-icon">&#9654;</span>
      </div>
      <div class="collapsible-body">
        <div class="code-block">
          <span class="lang-tag">TypeScript</span>
          <pre><span class="code-comment">// packages/service/worker/readFile/extension/pdf.ts</span>
<span class="code-comment">// 页面高度上下5%区域视为页眉页脚, 过滤该区域内的token</span>

<span class="code-comment">// 计算页眉/页脚边界</span>
<span class="code-keyword">const</span> headerBoundary = pageHeight * <span class="code-number">0.05</span>;
<span class="code-keyword">const</span> footerBoundary = pageHeight * <span class="code-number">0.95</span>;

<span class="code-comment">// 遍历页面token, 过滤页眉页脚区域</span>
pageTokens.<span class="code-func">forEach</span>(token => {
  <span class="code-keyword">const</span> y = token.transform[<span class="code-number">5</span>];
  <span class="code-keyword">if</span> (y > headerBoundary && y < footerBoundary) {
    validTokens.<span class="code-func">push</span>(token);
  }
});

<span class="code-comment">// 段落结束检测正则 — 识别中英文句末标点与换行</span>
<span class="code-keyword">const</span> paragraphEndReg = <span class="code-string">/([。？！.?!\n\r])/</span>;

<span class="code-comment">// 空token合并: 连续空白token压缩为单一分隔符</span>
<span class="code-keyword">if</span> (lastToken) {
  <span class="code-keyword">const</span> distX = <span class="code-func">Math</span>.<span class="code-func">abs</span>(token.x - lastToken.x);
  <span class="code-keyword">if</span> (distX > maxSpaceDist) {
    text += <span class="code-string">' '</span>;
  }
}</pre>
        </div>
      </div>
    </div>

    <div class="collapsible-code">
      <div class="collapsible-header" onclick="this.querySelector('.toggle-icon').classList.toggle('open');this.nextElementSibling.classList.toggle('open')">
        <span class="title"><span class="icon">&#128196;</span> DOCX清洗源码 (HTML→Markdown)</span>
        <span class="toggle-icon">&#9654;</span>
      </div>
      <div class="collapsible-body">
        <div class="code-block">
          <span class="lang-tag">TypeScript</span>
          <pre><span class="code-comment">// packages/service/worker/htmlStr2Md/utils.ts</span>

<span class="code-comment">// Step 1: mammoth 将 DOCX 转为 HTML</span>
<span class="code-keyword">const</span> result = <span class="code-keyword">await</span> <span class="code-func">mammoth</span>.<span class="code-func">convertToHtml</span>(
  { buffer: fileBuffer },
  {
    ignoreEmptyParagraphs: <span class="code-keyword">false</span>,  <span class="code-comment">// 保留空段落维持文档结构</span>
    convertImage: mammoth.images.<span class="code-func">imgElement</span>(
      <span class="code-keyword">function</span>(image) {
        <span class="code-keyword">return</span> image.<span class="code-func">read</span>(<span class="code-string">"base64then"</span>)
          .<span class="code-func">then</span>(imageBuffer => ({
            src: <span class="code-string">`data:${image.contentType};base64,`</span> + imageBuffer
          }));
      }
    )
  }
);

<span class="code-comment">// Step 2: 移除非内容HTML标签 (script, style, iframe)</span>
<span class="code-keyword">const</span> cleanHtml = html
  .<span class="code-func">replace</span>(<span class="code-string">/&lt;script[^&gt;]*&gt;[\s\S]*?&lt;\/script&gt;/gi</span>, <span class="code-string">''</span>)
  .<span class="code-func">replace</span>(<span class="code-string">/&lt;style[^&gt;]*&gt;[\s\S]*?&lt;\/style&gt;/gi</span>, <span class="code-string">''</span>)
  .<span class="code-func">replace</span>(<span class="code-string">/&lt;iframe[^&gt;]*&gt;[\s\S]*?&lt;\/iframe&gt;/gi</span>, <span class="code-string">''</span>);

<span class="code-comment">// Step 3: turndown 将 HTML 转为 Markdown</span>
<span class="code-keyword">const</span> turndownService = <span class="code-keyword">new</span> <span class="code-type">TurndownService</span>();
<span class="code-keyword">const</span> markdown = turndownService.<span class="code-func">turndown</span>(cleanHtml);

<span class="code-comment">// Step 4: 提取base64图片, UUID替换src属性</span>
<span class="code-keyword">const</span> base64Regex = <span class="code-string">/data:image\/[^;]+;base64,([A-Za-z0-9+/=]+)/g</span>;
markdown = markdown.<span class="code-func">replace</span>(base64Regex, (match, base64) => {
  <span class="code-keyword">const</span> uuid = <span class="code-func">generateUUID</span>();
  <span class="code-func">saveImageToDataset</span>(uuid, base64);
  <span class="code-keyword">return</span> uuid;
});</pre>
        </div>
      </div>
    </div>

    <div class="two-col">
      <!-- 通用文本清洗 -->
      <div class="card">
        <div class="card-title"><span class="icon">🔧</span> 通用文本清洗</div>
        <ul class="feature-list">
          <li v-for="f in textStrategies" :key="f.title">
            <strong>{{ f.title }}：</strong>{{ f.desc }}
          </li>
        </ul>
      </div>

      <!-- 自定义清洗规则 -->
      <div class="card">
        <div class="card-title"><span class="icon">⚙️</span> 自定义清洗规则</div>
        <div class="highlight-block">
          用户可通过 <code>customReg</code> 参数定义自定义分割正则表达式，作为最高优先级分割规则，灵活适配各类文档格式。
        </div>
      </div>
    </div>

    <div class="collapsible-code">
      <div class="collapsible-header" onclick="this.querySelector('.toggle-icon').classList.toggle('open');this.nextElementSibling.classList.toggle('open')">
        <span class="title"><span class="icon">&#128196;</span> 通用文本清洗源码</span>
        <span class="toggle-icon">&#9654;</span>
      </div>
      <div class="collapsible-body">
        <div class="code-block">
          <span class="lang-tag">TypeScript</span>
          <pre><span class="code-comment">// packages/global/common/string/textSplitter.ts</span>

<span class="code-comment">// Step 1: 换行规范化 — 3个以上连续换行折叠为2个</span>
text = text.<span class="code-func">replace</span>(<span class="code-string">/\n{3,}/g</span>, <span class="code-string">'\n\n'</span>);

<span class="code-comment">// Step 2: 代码块保护 — 代码块内换行替换为MARKER</span>
<span class="code-keyword">const</span> CODE_BLOCK_LINE_MARKER = <span class="code-string">'@@CODE_LINE@@'</span>;
text = text.<span class="code-func">replace</span>(<span class="code-string">/```([\s\S]*?)```/g</span>, (match) => {
  <span class="code-keyword">return</span> match.<span class="code-func">replace</span>(<span class="code-string">/\n/g</span>, CODE_BLOCK_LINE_MARKER);
});

<span class="code-comment">// Step 3: simpleMarkdownText 后处理</span>
<span class="code-keyword">export</span> <span class="code-keyword">function</span> <span class="code-func">simpleMarkdownText</span>(text: <span class="code-type">string</span>) {
  <span class="code-comment">// 移除多余中文空格</span>
  text = text.<span class="code-func">replace</span>(<span class="code-string">/([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])/g</span>, <span class="code-string">'$1$2'</span>);
  <span class="code-comment">// 规范化换行符</span>
  text = text.<span class="code-func">replace</span>(<span class="code-string">/\r\n/g</span>, <span class="code-string">'\n'</span>);
  <span class="code-keyword">return</span> text.<span class="code-func">trim</span>();
}

<span class="code-comment">// Step 4: simpleText 纯文本后处理</span>
<span class="code-keyword">export</span> <span class="code-keyword">function</span> <span class="code-func">simpleText</span>(text: <span class="code-type">string</span>) {
  text = <span class="code-func">simpleMarkdownText</span>(text);
  <span class="code-comment">// 移除连续空格</span>
  text = text.<span class="code-func">replace</span>(<span class="code-string">/ {2,}/g</span>, <span class="code-string">' '</span>);
  <span class="code-keyword">return</span> text;
}

<span class="code-comment">// Step 5: 恢复代码块内的换行</span>
text = text.<span class="code-func">replace</span>(<span class="code-keyword">new</span> <span class="code-type">RegExp</span>(CODE_BLOCK_LINE_MARKER, <span class="code-string">'g'</span>), <span class="code-string">'\n'</span>);</pre>
        </div>
      </div>
    </div>

    <!-- 核心代码示例 -->
    <div class="card">
      <div class="card-title"><span class="icon">💻</span> 段落检测与换行折叠</div>
      <pre class="code-block"><code>// 段落结束检测正则
const paragraphEndRegex = /([。？！.?!\n\r])/;

// 连续空行折叠
text = text.replace(/\n{3,}/g, '\n\n');</code></pre>
    </div>
  </div>
</template>

<script setup>
const pdfStrategies = [
  { title: '页眉页脚区域过滤', desc: '顶部5%和底部5%的页面高度区域被排除' },
  { title: '空Token合并', desc: '连续空token合并为单一分隔符' },
  { title: '段落结束检测', desc: '使用正则表达式 ([。？！.?!\n\r]) 识别段落边界' },
  { title: '表格结构保留', desc: '保持PDF中表格的行列关系' }
]

const docxStrategies = [
  { title: '空段落处理', desc: 'ignoreEmptyParagraphs=false 保留文档结构' },
  { title: 'HTML标签过滤', desc: '移除 script, style, iframe 等非内容标签' },
  { title: '图片提取', desc: 'mammoth将嵌入图片转为base64, UUID替换src属性' }
]

const textStrategies = [
  { title: '换行规范化', desc: '3个以上连续换行折叠为2个' },
  { title: '编码规范化', desc: 'iconv-lite 自动检测并转换字符编码' },
  { title: '代码块保护', desc: '代码块内换行替换为CODE_BLOCK_LINE_MARKER, 分割后恢复' },
  { title: '后处理', desc: 'simpleText() 移除多余中文空格, 规范化换行符' }
]
</script>
