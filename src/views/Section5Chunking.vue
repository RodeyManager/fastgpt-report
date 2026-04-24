<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§5 文本分块</h2>
      <p>递归多策略文本分割算法 — 按优先级逐层递归拆分, 12+ 规则确保语义完整性</p>
    </div>

    <div class="source-ref-list">
      <div class="ref-title">&#128204; 核心源码</div>
      <div class="source-ref-item"><span class="ref-file">packages/global/common/string/textSplitter.ts</span> <span class="ref-desc">核心分块算法(commonSplit)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/worker/text2Chunks/index.ts</span> <span class="ref-desc">Worker线程分块入口</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/core/dataset/read.ts</span> <span class="ref-desc">数据集读取编排(rawText2Chunks)</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/service/core/dataset/collection/utils.ts</span> <span class="ref-desc">分块配置获取</span></div>
      <div class="source-ref-item"><span class="ref-file">packages/global/core/dataset/constants.ts</span> <span class="ref-desc">分块参数常量定义</span></div>
    </div>

    <!-- 核心算法 -->
    <div class="card">
      <div class="card-title"><span class="icon">🧠</span> 核心算法 commonSplit()</div>
      <div class="highlight-block">
        <code>commonSplit()</code> 采用递归多轮分割策略：按优先级从高到低依次尝试 12+ 条分割规则。
        每轮以当前规则的分隔符对超长文本进行拆分，若某片段仍超过阈值，则递归进入下一优先级规则继续分割，
        直至所有片段均满足长度约束或规则耗尽。该策略兼顾<strong>结构完整性</strong>与<strong>粒度可控性</strong>。
      </div>
    </div>

    <!-- 分割规则优先级 -->
    <div class="card">
      <div class="card-title"><span class="icon">📊</span> 分割规则优先级</div>
      <table class="data-table">
        <thead>
          <tr>
            <th>优先级</th><th>规则</th><th>最大长度</th><th>重叠</th><th>说明</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in rules" :key="r.priority">
            <td><span :class="['tag', r.tag]">{{ r.priority }}</span></td>
            <td><code>{{ r.rule }}</code></td>
            <td>{{ r.maxLen }}</td>
            <td>{{ r.overlap }}</td>
            <td>{{ r.desc }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ECharts 优先级可视化 -->
    <div class="card">
      <div class="card-title"><span class="icon">📈</span> 分割优先级可视化</div>
      <div id="chart-split-priority" class="chart-container"></div>
    </div>

    <!-- 配置参数 -->
    <div class="card">
      <div class="card-title"><span class="icon">⚙️</span> 配置参数</div>
      <table class="data-table">
        <thead><tr><th>参数</th><th>默认值</th><th>说明</th></tr></thead>
        <tbody>
          <tr v-for="p in params" :key="p.name">
            <td><code>{{ p.name }}</code></td>
            <td>{{ p.default }}</td>
            <td>{{ p.desc }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="two-col">
      <!-- LLM 段落增强 -->
      <div class="card">
        <div class="card-title"><span class="icon">🤖</span> LLM段落增强</div>
        <table class="data-table">
          <thead><tr><th>模式</th><th>行为</th></tr></thead>
          <tbody>
            <tr v-for="m in llmModes" :key="m.mode">
              <td><span :class="['tag', m.tag]">{{ m.mode }}</span></td>
              <td>{{ m.desc }}</td>
            </tr>
          </tbody>
        </table>
        <div class="highlight-block" style="margin-top:14px">
          使用LLM重构文本结构, 补全缺失标题、优化段落层次, 以提升分块的语义连贯性。
        </div>
      </div>

      <!-- 重叠机制 -->
      <div class="card">
        <div class="card-title"><span class="icon">🔗</span> 重叠(Overlap)机制</div>
        <div class="code-block">
          <span class="lang-tag">TypeScript</span>
          <pre><span class="code-keyword">const</span> overlapLen = chunkSize * overlapRatio;  <span class="code-comment">// 默认15%重叠</span>
<span class="code-keyword">const</span> maxOverlap = chunkSize * <span class="code-number">0.4</span>;           <span class="code-comment">// 最大不超过40%</span>
<span class="code-comment">// 从当前块末尾提取重叠文本, 添加到下一块开头</span>
<span class="code-keyword">const</span> overlapText = currentChunk.slice(-overlapLen);
nextChunk = overlapText + nextChunk;</pre>
        </div>
      </div>
    </div>
    <div class="collapsible-code">
      <div class="collapsible-header" onclick="this.querySelector('.toggle-icon').classList.toggle('open');this.nextElementSibling.classList.toggle('open')">
        <span class="title"><span class="icon">&#9881;</span> commonSplit 递归分割完整源码</span>
        <span class="toggle-icon open">&#9654;</span>
      </div>
      <div class="collapsible-body open">
        <div class="code-block">
          <span class="lang-tag">TypeScript</span>
          <pre><span class="code-comment">// packages/global/common/string/textSplitter.ts — 完整算法流程</span>

<span class="code-keyword">function</span> <span class="code-func">commonSplit</span>({
  text, chunkSize, maxSize, overlapRatio,
  paragraphChunkDeep, customReg
}: SplitProps): <span class="code-type">string[]</span> {

  <span class="code-comment">// ═══ Step 1: 构建优先级分割规则链 stepReges ═══</span>
  <span class="code-keyword">const</span> stepReges: <span class="code-type">StepReg[]</span> = [
    <span class="code-comment">// [优先级1] 用户自定义正则 — 最先尝试, 不启用重叠</span>
    ...customReg.map(r => ({ reg: r, useOverlap: <span class="code-keyword">false</span> })),

    <span class="code-comment">// [优先级2] Markdown标题 #~###### — 子块继承父标题</span>
    ...Array.from({ length: paragraphChunkDeep }, (_, i) => ({
      reg: <span class="code-keyword">new</span> RegExp(<span class="code-string">`^#{${i + <span class="code-number">1</span>}}\\s.+`</span>, <span class="code-string">'gm'</span>),
      useOverlap: <span class="code-keyword">false</span>
    })),

    <span class="code-comment">// [优先级3] 代码块 ```...``` — 保持完整性</span>
    { reg: <span class="code-string">/```[\s\S]*?```/g</span>, useOverlap: <span class="code-keyword">false</span> },

    <span class="code-comment">// [优先级4] Markdown表格 — 行感知, 保留表头</span>
    { reg: <span class="code-string">/^\|.+\|$/gm</span>, useOverlap: <span class="code-keyword">false</span> },

    <span class="code-comment">// [优先级5] 双换行(段落边界)</span>
    { reg: <span class="code-string">/\n\n/g</span>, useOverlap: <span class="code-keyword">false</span> },

    <span class="code-comment">// [优先级6] 单换行(行边界)</span>
    { reg: <span class="code-string">/\n/g</span>, useOverlap: <span class="code-keyword">false</span> },

    <span class="code-comment">// [优先级7~11] 标点符号 — 启用重叠(overlap)</span>
    { reg: <span class="code-string">/[。.]+/g</span>, useOverlap: <span class="code-keyword">true</span> },
    { reg: <span class="code-string">/[!！]+/g</span>, useOverlap: <span class="code-keyword">true</span> },
    { reg: <span class="code-string">/[?？]+/g</span>, useOverlap: <span class="code-keyword">true</span> },
    { reg: <span class="code-string">/[;；]+/g</span>, useOverlap: <span class="code-keyword">true</span> },
    { reg: <span class="code-string">/[,，]+/g</span>, useOverlap: <span class="code-keyword">true</span> },
  ];

  <span class="code-comment">// ═══ Step 2: 递归分割 splitByStep ═══</span>
  <span class="code-keyword">function</span> <span class="code-func">splitByStep</span>(src: <span class="code-type">string</span>, step: <span class="code-type">StepReg</span>): <span class="code-type">string[]</span> {
    <span class="code-keyword">const</span> marker = <span class="code-string">`CODE_BLOCK_LINE_MARKER`</span>;
    <span class="code-comment">// 保护代码块: 用临时标记替换代码块内换行, 防止被错误分割</span>
    <span class="code-keyword">const</span> protectedText = src.replace(<span class="code-string">/```[\s\S]*?```/g</span>,
      m => m.replace(<span class="code-string">/\n/g</span>, marker)
    );

    <span class="code-keyword">const</span> parts = protectedText.split(step.reg);
    <span class="code-comment">// 恢复代码块内的换行符</span>
    <span class="code-keyword">return</span> parts.map(p => p.replaceAll(marker, <span class="code-string">'\n'</span>));
  }

  <span class="code-comment">// ═══ Step 3: 逐级递归尝试分割 ═══</span>
  <span class="code-keyword">for</span> (<span class="code-keyword">const</span> step <span class="code-keyword">of</span> stepReges) {
    <span class="code-keyword">const</span> chunks = <span class="code-func">splitByStep</span>(text, step);
    <span class="code-keyword">if</span> (chunks.length <= <span class="code-number">1</span>) <span class="code-keyword">continue</span>;  <span class="code-comment">// 当前规则无法分割, 降级</span>

    <span class="code-keyword">return</span> chunks.flatMap(chunk => {
      <span class="code-comment">// ═══ Step 4: maxSize 硬限检查 ═══</span>
      <span class="code-keyword">if</span> (chunk.length > maxSize) {
        <span class="code-comment">// 超过绝对上限, 递归进入下一优先级继续分割</span>
        <span class="code-keyword">return</span> <span class="code-func">commonSplit</span>({ ...params, text: chunk });
      }

      <span class="code-comment">// ═══ Step 5: 重叠机制(仅标点级) ═══</span>
      <span class="code-keyword">if</span> (step.useOverlap) {
        <span class="code-keyword">const</span> overlapLen = chunkSize * overlapRatio;  <span class="code-comment">// 默认15%</span>
        <span class="code-keyword">const</span> maxOverlap = chunkSize * <span class="code-number">0.4</span>;           <span class="code-comment">// 上限40%</span>
        <span class="code-keyword">const</span> actual = Math.min(overlapLen, maxOverlap);
        chunk = prevChunk.slice(-actual) + chunk;  <span class="code-comment">// 前块尾部→当前块头部</span>
      }

      <span class="code-comment">// ═══ Step 6: Markdown标题继承 ═══</span>
      <span class="code-keyword">if</span> (headingStack.length) {
        chunk = headingStack.join(<span class="code-string">'\n'</span>) + <span class="code-string">'\n'</span> + chunk;
      }

      <span class="code-keyword">return</span> [chunk];
    });
  }

  <span class="code-comment">// 所有规则耗尽, 返回原始文本(受maxSize保护)</span>
  <span class="code-keyword">return</span> [text];
}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import * as echarts from 'echarts'

const rules = [
  { priority: '1~N', rule: '自定义正则', maxLen: 'maxSize', overlap: '无', desc: '用户自定义分割符', tag: 'tag-purple' },
  { priority: 'N+1', rule: '# ~ ######', maxLen: 'chunkSize', overlap: '无', desc: '标题继承(子块保留父标题)', tag: 'tag-blue' },
  { priority: '→', rule: '``` 代码块', maxLen: 'maxSize', overlap: '无', desc: '保持代码块完整性', tag: 'tag-cyan' },
  { priority: '→', rule: 'Markdown表格', maxLen: 'chunkSize×1.2', overlap: '无', desc: '行感知, 表头保留', tag: 'tag-cyan' },
  { priority: '→', rule: '双换行(段落)', maxLen: 'chunkSize', overlap: '无', desc: '段落边界', tag: 'tag-green' },
  { priority: '→', rule: '单换行', maxLen: 'chunkSize', overlap: '无', desc: '行边界', tag: 'tag-green' },
  { priority: '→', rule: '。 / .', maxLen: 'chunkSize', overlap: '有(15%)', desc: '句子边界', tag: 'tag-orange' },
  { priority: '→', rule: '! / ！', maxLen: 'chunkSize', overlap: '有(15%)', desc: '感叹号分割', tag: 'tag-orange' },
  { priority: '→', rule: '? / ？', maxLen: 'chunkSize', overlap: '有(15%)', desc: '问号分割', tag: 'tag-orange' },
  { priority: '→', rule: '; / ；', maxLen: 'chunkSize', overlap: '有(15%)', desc: '分号分割', tag: 'tag-orange' },
  { priority: '→', rule: ', / ，', maxLen: 'chunkSize', overlap: '有(15%)', desc: '逗号分割', tag: 'tag-orange' }
]

const params = [
  { name: 'chunkSize', default: '1000', desc: '目标块大小(字符, 不含空白)' },
  { name: 'maxSize', default: '8000', desc: '绝对最大值' },
  { name: 'overlapRatio', default: '0.15', desc: '重叠比例(仅标点级生效)' },
  { name: 'paragraphChunkDeep', default: '5', desc: 'Markdown标题深度(最大8)' },
  { name: 'paragraphChunkMinSize', default: '100', desc: '最小块大小(小于此值合并)' }
]

const llmModes = [
  { mode: 'auto', desc: '无标题时自动启用LLM增强', tag: 'tag-cyan' },
  { mode: 'force', desc: '始终启用LLM增强', tag: 'tag-green' },
  { mode: 'forbid', desc: '禁用LLM增强', tag: 'tag-red' }
]

onMounted(() => {
  const chart = echarts.init(document.getElementById('chart-split-priority'))
  const labels = ['自定义正则','Markdown标题','代码块','Markdown表格','双换行(段落)','单换行','句号(.。)','感叹号(!！)','问号(?？)','分号(;；)','逗号(,，)']
  const colors = ['#8b5cf6','#6366f1','#06b6d4','#0891b2','#10b981','#059669','#f59e0b','#fb923c','#ef4444','#e11d48','#a855f7']
  const hasOverlap = [0,0,0,0,0,0,1,1,1,1,1]

  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 130, right: 60, top: 10, bottom: 30 },
    xAxis: { type: 'value', name: '优先级(高→低)', nameLocation: 'center', nameGap: 25,
      axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: 'rgba(99,102,241,0.1)' } } },
    yAxis: { type: 'category', data: labels.reverse(),
      axisLabel: { color: '#c9d1d9', fontSize: 12 }, axisLine: { lineStyle: { color: '#333' } } },
    series: [{
      type: 'bar', barWidth: 16,
      data: labels.map((_, i) => ({
        value: labels.length - i,
        itemStyle: { color: colors[colors.length - 1 - i], borderRadius: [0,4,4,0] }
      })),
      label: { show: true, position: 'right', color: '#94a3b8', fontSize: 11,
        formatter: p => hasOverlap[hasOverlap.length - 1 - p.dataIndex] ? '有重叠(15%)' : '' }
    }]
  })
  window.addEventListener('resize', () => chart.resize())
})
</script>
