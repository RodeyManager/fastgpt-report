<template>
  <div class="demo-page">
    <div class="demo-header">
      <h2>§14 Demo演示</h2>
      <p>交互式文档处理流水线演示：上传文件 → 文档解析 → Markdown转换 → 数据清洗 → 文本分块 → 图片索引</p>
    </div>

    <div
      class="demo-upload-zone"
      :class="{ 'drag-over': isDragOver }"
      @click="triggerUpload"
      @dragover.prevent="isDragOver = true"
      @dragleave.prevent="isDragOver = false"
      @drop.prevent="handleDrop"
    >
      <span class="upload-icon">📄</span>
      <div class="upload-text">拖拽文件到此处 或 点击选择文件</div>
      <div class="upload-hint">支持 PDF / DOCX / CSV / XLSX / TXT / HTML / 图片 等格式</div>
      <input ref="fileInput" type="file" style="display:none" @change="handleFileSelect" />
    </div>

    <div v-if="fileInfo" class="demo-file-info">
      <div class="info-card">
        <span class="info-label">文件名：</span>
        <span class="info-value">{{ fileInfo.name }}</span>
      </div>
      <div class="info-card">
        <span class="info-label">大小：</span>
        <span class="info-value">{{ formatSize(fileInfo.size) }}</span>
      </div>
      <div class="info-card">
        <span class="info-label">类型：</span>
        <span class="info-value">{{ fileInfo.ext.toUpperCase() }}</span>
      </div>
    </div>

    <div v-if="uploadedFile" class="demo-steps">
      <button
        v-for="(step, idx) in steps"
        :key="idx"
        class="demo-step-tab"
        :class="{ active: activeStep === idx }"
        @click="activeStep = idx"
      >{{ step.label }}</button>
    </div>

    <div v-if="loading" class="demo-loading">
      <div class="spinner"></div>
      <span>处理中...</span>
    </div>

    <div v-if="errorMsg" class="demo-error">
      <span>⚠</span> {{ errorMsg }}
    </div>

    <template v-if="uploadedFile && !loading">
      <div class="demo-stats-bar">
        <div class="stat-item" v-if="activeStep === 0">
          <span class="stat-value">{{ rawText.length }}</span>
          <span class="stat-label">原始字符数</span>
        </div>
        <div class="stat-item" v-if="activeStep === 1">
          <span class="stat-value">{{ rawText.length }}</span>
          <span class="stat-label">转换前</span>
        </div>
        <div class="stat-item" v-if="activeStep === 1">
          <span class="stat-value">{{ markdownText?.length || 0 }}</span>
          <span class="stat-label">转换后</span>
        </div>
        <div class="stat-item" v-if="activeStep === 2">
          <span class="stat-value">{{ textBeforeClean.length }}</span>
          <span class="stat-label">清洗前</span>
        </div>
        <div class="stat-item" v-if="activeStep === 2">
          <span class="stat-value">{{ cleanedText.length }}</span>
          <span class="stat-label">清洗后</span>
        </div>
        <div class="stat-item" v-if="activeStep === 2">
          <span class="stat-value">{{ textBeforeClean.length > 0 ? ((1 - cleanedText.length / textBeforeClean.length) * 100).toFixed(1) : 0 }}%</span>
          <span class="stat-label">缩减率</span>
        </div>
        <div class="stat-item" v-if="activeStep === 3">
          <span class="stat-value">{{ chunks.length }}</span>
          <span class="stat-label">分块数量</span>
        </div>
        <div class="stat-item" v-if="activeStep === 3">
          <span class="stat-value">{{ avgChunkSize }}</span>
          <span class="stat-label">平均块大小</span>
        </div>
        <div class="stat-item" v-if="activeStep === 3">
          <span class="stat-value">{{ cleanedText.length }}</span>
          <span class="stat-label">总字符数</span>
        </div>
      </div>

      <div class="demo-layout">
        <div class="demo-result-panel">
          <div class="result-label">{{ steps[activeStep]?.label }} 结果</div>

          <!-- Step 0: 文档解析 -->
          <div v-if="activeStep === 0">
            <div v-if="hasMultipleResults" class="compare-view">
              <div class="compare-column">
                <div class="compare-label">FastGPT 默认</div>
                <div class="result-content" :class="{ 'html-content': parseMethod === 'html' }" v-html="engineResults.fastgpt?.html_preview || ''"></div>
                <div class="compare-stat">{{ (engineResults.fastgpt?.raw_text || '').length }} 字符</div>
              </div>
              <div class="compare-column">
                <div class="compare-label">MinerU</div>
                <div class="result-content" :class="{ 'html-content': parseMethod === 'html' }" v-html="engineResults.mineru?.html_preview || ''"></div>
                <div class="compare-stat">{{ (engineResults.mineru?.raw_text || '').length }} 字符</div>
              </div>
            </div>
            <template v-else>
              <div v-if="parsedResult" class="result-content" :class="{ 'html-content': parseMethod === 'html' }" v-html="parsedResult"></div>
              <div v-else class="empty-state">点击右侧「开始解析」按钮进行文档解析</div>
            </template>
          </div>

          <!-- Step 1: Markdown转换 -->
          <div v-if="activeStep === 1">
            <div v-if="convertResults.length > 0" style="display:flex;flex-direction:column;gap:16px">
              <div>
                <div style="font-size:0.75rem;color:var(--text-muted);margin-bottom:6px">原始解析输出 ({{ rawText.length }} 字符)</div>
                <div class="result-content demo-fulltext-box" v-if="isDocxHtmlMode" v-html="rawText"></div>
                <div class="result-content demo-fulltext-box" v-else>{{ rawText }}</div>
              </div>
              <div v-if="convertResults.length === 2" style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
                <div v-for="r in convertResults" :key="r.tool">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                    <span style="font-size:0.82rem;font-weight:600;color:var(--accent-green)">{{ r.tool === 'markdownify' ? 'Markdownify' : 'MarkItDown' }}</span>
                    <span style="font-size:0.72rem;color:var(--text-muted)">{{ r.duration_ms.toFixed(1) }}ms</span>
                  </div>
                  <div class="result-content demo-fulltext-box" style="background:rgba(0,255,136,0.04);border-color:rgba(0,255,136,0.15);font-size:0.85rem;max-height:400px;overflow-y:auto">{{ r.markdown }}</div>
                </div>
              </div>
              <div v-else>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                  <span style="font-size:0.75rem;color:var(--accent-green)">Markdown 转换结果 ({{ markdownText.length }} 字符)</span>
                  <span style="font-size:0.72rem;color:var(--text-muted)" v-if="convertResults[0]">{{ convertResults[0].duration_ms.toFixed(1) }}ms</span>
                </div>
                <div class="result-content demo-fulltext-box" style="background:rgba(0,255,136,0.04);border-color:rgba(0,255,136,0.15)">{{ markdownText }}</div>
              </div>
              <div v-if="mdConversionNote" style="font-size:0.78rem;color:var(--text-muted);padding:8px 12px;background:rgba(99,102,241,0.05);border-radius:6px;border-left:3px solid var(--accent-blue)">
                {{ mdConversionNote }}
              </div>
            </div>
            <div v-else-if="markdownText !== null" style="display:flex;flex-direction:column;gap:16px">
              <div>
                <div style="font-size:0.75rem;color:var(--text-muted);margin-bottom:6px">原始解析输出 ({{ rawText.length }} 字符)</div>
                <div class="result-content demo-fulltext-box" v-if="isDocxHtmlMode" v-html="rawText"></div>
                <div class="result-content demo-fulltext-box" v-else>{{ rawText }}</div>
              </div>
              <div>
                <div style="font-size:0.75rem;color:var(--accent-green);margin-bottom:6px">Markdown 转换结果 ({{ markdownText.length }} 字符)</div>
                <div class="result-content demo-fulltext-box" style="background:rgba(0,255,136,0.04);border-color:rgba(0,255,136,0.15)">{{ markdownText }}</div>
              </div>
            </div>
            <div v-else class="empty-state">请先完成文档解析，再点击「转换为Markdown」</div>
          </div>

          <!-- Step 2: 数据清洗 -->
          <div v-if="activeStep === 2">
            <div v-if="cleanedText !== null" style="display:flex;flex-direction:column;gap:16px">
              <div>
                <div style="font-size:0.75rem;color:var(--text-muted);margin-bottom:6px">清洗前 ({{ textBeforeClean.length }} 字符)</div>
                <div class="result-content demo-fulltext-box">{{ textBeforeClean }}</div>
              </div>
              <div>
                <div style="font-size:0.75rem;color:var(--accent-cyan);margin-bottom:6px">清洗后 ({{ cleanedText.length }} 字符)</div>
                <div class="result-content demo-fulltext-box" style="background:rgba(6,182,212,0.06);border-color:rgba(6,182,212,0.15)">{{ cleanedText }}</div>
              </div>
            </div>
            <div v-else class="empty-state">请先完成 Markdown 转换，再点击「执行清洗」</div>
          </div>

          <!-- Step 3: 文本分块 -->
          <div v-if="activeStep === 3">
            <div v-if="chunks.length > 0">
              <div v-for="(chunk, idx) in chunks" :key="idx" class="demo-chunk-item">
                <div class="chunk-header">
                  <span class="chunk-index">Chunk #{{ idx + 1 }}</span>
                  <span class="chunk-size">{{ chunk.length }} 字符</span>
                </div>
                <div class="chunk-text">{{ chunk }}</div>
              </div>
            </div>
            <div v-else class="empty-state">请先完成数据清洗，再点击「执行分块」</div>
          </div>

          <!-- Step 4: 图片索引 -->
          <div v-if="activeStep === 4">
            <div v-if="imagePreview">
              <img :src="imagePreview" class="demo-image-preview" alt="preview" />
              <div class="result-content">
                <div style="margin-bottom:12px;color:var(--text-primary);font-family:var(--font-body);font-size:0.9rem">
                  图片索引使用 VLM（视觉语言模型）对图片内容进行理解与描述，生成可用于检索的文本向量。
                </div>
                <div v-if="imageDescription" style="margin-top:8px;padding:10px;background:rgba(6,182,212,0.06);border-radius:6px;border-left:3px solid var(--accent-cyan)">
                  <div style="font-size:0.78rem;color:var(--accent-cyan);margin-bottom:4px">VLM 描述结果</div>
                  <div style="font-size:0.85rem;color:var(--text-primary)">{{ imageDescription }}</div>
                  <div v-if="imageMeta" style="font-size:0.75rem;color:var(--text-muted);margin-top:6px">
                    {{ imageMeta.width }}×{{ imageMeta.height }} {{ imageMeta.format }} {{ formatSize(imageMeta.size_bytes) }}
                  </div>
                </div>
                <div v-else style="color:var(--text-muted);font-size:0.82rem">
                  流程：图片上传 → VLM 模型描述 → 文本向量化 → 存入向量数据库 → 支持语义检索
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              上传图片文件以预览索引效果<br />
              <span style="font-size:0.8rem;color:var(--text-muted)">当前文件非图片格式</span>
            </div>
          </div>
        </div>

        <div class="demo-options-panel">
          <!-- Step 0 Options: 文档解析 -->
          <template v-if="activeStep === 0">
            <div class="option-title">解析选项</div>
            <div class="demo-option-item">
              <span>解析引擎：</span>
              <select v-model="selectedEngine">
                <option v-for="e in engines" :key="e.value" :value="e.value">{{ e.label }}</option>
              </select>
            </div>
            <div v-if="!isMineruAvailable && fileInfo" style="font-size:0.78rem;color:var(--text-secondary);padding:2px 0">
              MinerU 仅支持 PDF/DOCX/PPTX/图片格式
            </div>
            <div class="demo-option-item">
              <span>解析方式：</span>
              <select v-model="parseMethod">
                <option v-for="m in parseMethods" :key="m.value" :value="m.value">{{ m.label }}</option>
              </select>
            </div>
            <div v-if="sheetNames.length > 1" class="demo-option-item">
              <span>工作表：</span>
              <select v-model="selectedSheet">
                <option v-for="s in sheetNames" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
            <div v-if="fileInfo && fileInfo.ext === 'pdf'" class="demo-slider-group" style="margin-top:6px">
              <label>页眉页脚过滤 <span>{{ (headerFooterRatio * 100).toFixed(0) }}%</span></label>
              <input type="range" v-model.number="headerFooterRatio" min="0" max="0.2" step="0.01" />
              <div style="font-size:0.72rem;color:var(--text-muted)">设为 0% 可禁用页眉页脚过滤</div>
            </div>
            <button class="demo-action-btn" @click="runParse">
              <span>▶</span> 开始解析
            </button>
            <div class="highlight-block" style="font-size:0.82rem;margin-top:8px">
              不同文件类型支持不同的解析策略：PDF 可按页提取文本；DOCX 可获取 HTML 或纯文本；CSV/XLSX 支持表头识别与结构化解析。
            </div>
          </template>

          <!-- Step 1 Options: Markdown转换 -->
          <template v-if="activeStep === 1">
            <div class="option-title">Markdown 转换</div>
            <div class="demo-option-item" style="flex-direction:column;align-items:flex-start;gap:4px">
              <div style="font-size:0.82rem;color:var(--text-secondary)">当前文件类型: <code style="color:var(--accent-cyan)">{{ fileInfo?.ext?.toUpperCase() }}</code></div>
              <div style="font-size:0.82rem;color:var(--text-secondary)">转换方式: <code style="color:var(--accent-green)">{{ mdConversionMethod }}</code></div>
              <div style="font-size:0.82rem;color:var(--text-secondary)">输出格式: <code :style="{ color: isMarkdownOutput ? 'var(--accent-green)' : 'var(--accent-orange)' }">{{ isMarkdownOutput ? 'Markdown' : '纯文本(无MD转换)' }}</code></div>
            </div>
            <div data-testid="md-tool-selector" style="margin-top:8px">
              <div class="option-title">转换工具</div>
              <div v-for="tool in mdTools" :key="tool.value" class="demo-option-item">
                <input type="checkbox" :checked="selectedMdTools.includes(tool.value)" @change="toggleMdTool(tool.value)" />
                <span>{{ tool.label }}</span>
              </div>
              <div style="font-size:0.75rem;color:var(--text-muted)">可选择 1-2 个工具进行对比</div>
            </div>
            <button class="demo-action-btn" @click="runMarkdownConvert">
              <span>▶</span> 转换为 Markdown
            </button>
            <div class="highlight-block" style="font-size:0.82rem;margin-top:8px">
              <div style="font-weight:600;color:var(--text-primary);margin-bottom:6px">转换链路说明</div>
              <div>Markdown 转换由后端 FastAPI 服务完成。支持 DOCX (HTML→MD)、CSV/XLSX (表格→MD)、MD (原样保留)、PDF (纯文本) 等多种转换策略。</div>
            </div>
          </template>

          <!-- Step 2 Options: 数据清洗 -->
          <template v-if="activeStep === 2">
            <div class="option-title">清洗选项</div>
            <div class="demo-option-item" style="margin-bottom:8px;padding-bottom:8px;border-bottom:1px solid var(--border-color)">
              <span style="font-size:0.82rem;font-weight:500">清洗预设</span>
              <select v-model="selectedProfile" @change="applyProfile(selectedProfile)" style="margin-left:auto;font-size:0.78rem;padding:2px 6px;border:1px solid var(--border-color);border-radius:4px;background:var(--bg-primary);color:var(--text-primary)">
                <option v-for="(p, key) in CLEAN_PROFILES" :key="key" :value="key">{{ p.label }}</option>
              </select>
            </div>
            <div class="demo-option-item">
              <input type="checkbox" v-model="cleanOptions.trim" />
              <span>去除首尾空白</span>
              <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.trim.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.trim.examples" :key="ex">{{ ex }}</span></span></span></span>
            </div>
            <div class="demo-option-item">
              <input type="checkbox" v-model="cleanOptions.normalize_unicode" />
              <span>Unicode NFKC 标准化</span>
              <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.normalize_unicode.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.normalize_unicode.examples" :key="ex">{{ ex }}</span></span></span></span>
            </div>
            <div class="demo-option-item">
              <input type="checkbox" v-model="cleanOptions.remove_invisible_chars" />
              <span>移除不可见字符</span>
              <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.remove_invisible_chars.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.remove_invisible_chars.examples" :key="ex">{{ ex }}</span></span></span></span>
            </div>
            <div class="demo-option-item">
              <input type="checkbox" v-model="cleanOptions.remove_chinese_space" />
              <span>移除中文字符间空格</span>
              <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.remove_chinese_space.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.remove_chinese_space.examples" :key="ex">{{ ex }}</span></span></span></span>
            </div>
            <div class="demo-option-item">
              <input type="checkbox" v-model="cleanOptions.normalize_newline" />
              <span>规范化换行符</span>
              <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.normalize_newline.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.normalize_newline.examples" :key="ex">{{ ex }}</span></span></span></span>
            </div>
            <div class="demo-option-item">
              <input type="checkbox" v-model="cleanOptions.fix_hyphenation" />
              <span>连字符断行修复</span>
              <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.fix_hyphenation.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.fix_hyphenation.examples" :key="ex">{{ ex }}</span></span></span></span>
            </div>
            <div class="demo-option-item">
              <input type="checkbox" v-model="cleanOptions.collapse_whitespace" />
              <span>合并连续空白</span>
              <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.collapse_whitespace.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.collapse_whitespace.examples" :key="ex">{{ ex }}</span></span></span></span>
            </div>
            <div class="demo-option-item">
              <input type="checkbox" v-model="cleanOptions.remove_empty_lines" />
              <span>移除空行</span>
              <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.remove_empty_lines.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.remove_empty_lines.examples" :key="ex">{{ ex }}</span></span></span></span>
            </div>
            <div style="border-top:1px solid var(--border-color);margin:6px 0;padding-top:6px">
              <div style="font-size:0.78rem;color:var(--accent-orange);margin-bottom:4px;font-weight:500">高级选项</div>
              <div class="demo-option-item">
                <input type="checkbox" v-model="cleanOptions.filter_watermark" />
                <span>水印文本过滤</span>
                <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.filter_watermark.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.filter_watermark.examples" :key="ex">{{ ex }}</span></span></span></span>
              </div>
              <div v-if="cleanOptions.filter_watermark" class="demo-option-item" style="padding-left:20px;flex-direction:column;align-items:flex-start;gap:4px">
                <span style="font-size:0.78rem;color:var(--text-muted)">自定义关键词（逗号分隔）</span>
                <input type="text" v-model="cleanOptions.watermark_keywords" placeholder="例如：内部资料,仅供查看" class="watermark-keywords-input" />
              </div>
              <div class="demo-option-item">
                <input type="checkbox" v-model="cleanOptions.deduplicate_paragraphs" />
                <span>段落去重</span>
                <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.deduplicate_paragraphs.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.deduplicate_paragraphs.examples" :key="ex">{{ ex }}</span></span></span></span>
              </div>
              <div v-if="cleanOptions.deduplicate_paragraphs" class="demo-option-item" style="padding-left:20px">
                <input type="checkbox" v-model="cleanOptions.dedup_fuzzy" />
                <span style="font-size:0.78rem">模糊去重</span>
              </div>
              <div class="demo-option-item">
                <input type="checkbox" v-model="cleanOptions.clean_table" />
                <span>表格清洗</span>
                <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.clean_table.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.clean_table.examples" :key="ex">{{ ex }}</span></span></span></span>
              </div>
              <div class="demo-option-item">
                <input type="checkbox" v-model="cleanOptions.mask_sensitive" />
                <span>敏感信息脱敏</span>
                <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.mask_sensitive.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.mask_sensitive.examples" :key="ex">{{ ex }}</span></span></span></span>
              </div>
              <div class="demo-option-item">
                <input type="checkbox" v-model="cleanOptions.filter_special_chars" />
                <span>特殊字符过滤（白名单）</span>
                <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.filter_special_chars.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.filter_special_chars.examples" :key="ex">{{ ex }}</span></span></span></span>
              </div>
              <div style="border-top:1px solid var(--border-color);margin:6px 0;padding-top:6px">
                <div style="font-size:0.78rem;color:var(--accent-orange);margin-bottom:4px;font-weight:500">结构级选项</div>
                <div class="demo-option-item">
                  <input type="checkbox" v-model="cleanOptions.filter_toc" />
                  <span>目录区域过滤</span>
                  <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.filter_toc.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.filter_toc.examples" :key="ex">{{ ex }}</span></span></span></span>
                </div>
                <div class="demo-option-item">
                  <input type="checkbox" v-model="cleanOptions.filter_page_numbers" />
                  <span>页码过滤</span>
                  <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.filter_page_numbers.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.filter_page_numbers.examples" :key="ex">{{ ex }}</span></span></span></span>
                </div>
                <div class="demo-option-item">
                  <input type="checkbox" v-model="cleanOptions.process_footnotes" />
                  <span>脚注/尾注处理</span>
                  <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.process_footnotes.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.process_footnotes.examples" :key="ex">{{ ex }}</span></span></span></span>
                </div>
                <div v-if="cleanOptions.process_footnotes" class="demo-option-item" style="padding-left:20px">
                  <span style="font-size:0.78rem;color:var(--text-muted)">操作</span>
                  <select v-model="cleanOptions.footnote_action" style="margin-left:8px;font-size:0.78rem;padding:2px 4px;border:1px solid var(--border-color);border-radius:4px;background:var(--bg-primary);color:var(--text-primary)">
                    <option value="remove">移除</option>
                    <option value="keep">保留</option>
                  </select>
                </div>
              </div>
              <div style="border-top:1px solid var(--border-color);margin:6px 0;padding-top:6px">
                <div style="font-size:0.78rem;color:var(--accent-orange);margin-bottom:4px;font-weight:500">HTML 选项</div>
                <div class="demo-option-item">
                  <input type="checkbox" v-model="cleanOptions.remove_html_comments" />
                  <span>HTML 注释移除</span>
                  <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.remove_html_comments.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.remove_html_comments.examples" :key="ex">{{ ex }}</span></span></span></span>
                </div>
                <div class="demo-option-item">
                  <input type="checkbox" v-model="cleanOptions.normalize_html_entities" />
                  <span>HTML 实体转换</span>
                  <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.normalize_html_entities.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.normalize_html_entities.examples" :key="ex">{{ ex }}</span></span></span></span>
                </div>
                <div class="demo-option-item">
                  <input type="checkbox" v-model="cleanOptions.filter_html_noise" />
                  <span>网页噪声过滤</span>
                  <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.filter_html_noise.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.filter_html_noise.examples" :key="ex">{{ ex }}</span></span></span></span>
                </div>
              </div>
              <div style="border-top:1px solid var(--border-color);margin:6px 0;padding-top:6px">
                <div style="font-size:0.78rem;color:var(--accent-orange);margin-bottom:4px;font-weight:500">Markdown 选项</div>
                <div class="demo-option-item">
                  <input type="checkbox" v-model="cleanOptions.clean_markdown_links" />
                  <span>Markdown 链接清理</span>
                  <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.clean_markdown_links.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.clean_markdown_links.examples" :key="ex">{{ ex }}</span></span></span></span>
                </div>
                <div class="demo-option-item">
                  <input type="checkbox" v-model="cleanOptions.remove_md_escapes" />
                  <span>Markdown 转义移除</span>
                  <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.remove_md_escapes.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.remove_md_escapes.examples" :key="ex">{{ ex }}</span></span></span></span>
                </div>
                <div class="demo-option-item">
                  <input type="checkbox" v-model="cleanOptions.clean_md_structure" />
                  <span>Markdown 结构清理</span>
                  <span class="rule-info-trigger" tabindex="0">ℹ<span class="rule-info-tooltip"><span class="tooltip-desc">{{ CLEAN_RULE_DESCRIPTIONS.clean_md_structure.desc }}</span><span class="tooltip-examples"><span class="example-label">示例</span><span class="example-item" v-for="ex in CLEAN_RULE_DESCRIPTIONS.clean_md_structure.examples" :key="ex">{{ ex }}</span></span></span></span>
                </div>
              </div>
            </div>
            <button class="demo-action-btn" @click="runCleaning">
              <span>▶</span> 执行清洗
            </button>
          </template>

          <!-- Step 3 Options: 文本分块 -->
          <template v-if="activeStep === 3">
            <div class="option-title">分块参数</div>
            <div class="demo-slider-group">
              <label>块大小 <span>{{ chunkParams.chunkSize }}</span></label>
              <input type="range" v-model.number="chunkParams.chunkSize" min="100" max="8000" step="100" />
            </div>
            <div class="demo-slider-group">
              <label>重叠率 <span>{{ (chunkParams.overlapRatio * 100).toFixed(0) }}%</span></label>
              <input type="range" v-model.number="chunkParams.overlapRatio" min="0" max="0.4" step="0.05" />
            </div>
            <div class="demo-slider-group">
              <label>段落深度 <span>{{ chunkParams.paragraphChunkDeep }}</span></label>
              <input type="range" v-model.number="chunkParams.paragraphChunkDeep" min="1" max="5" step="1" />
            </div>
            <button class="demo-action-btn" @click="runChunking">
              <span>▶</span> 执行分块
            </button>
            <div class="highlight-block" style="font-size:0.82rem;margin-top:8px">
              递归多级分块策略：依次尝试 Markdown 标题 → 段落 → 标点 → 固定长度，确保语义完整性。
            </div>
          </template>

          <!-- Step 4 Options: 图片索引 -->
          <template v-if="activeStep === 4">
            <div class="option-title">图片索引信息</div>
            <div v-if="fileInfo" class="demo-option-item" style="flex-direction:column;align-items:flex-start;gap:4px">
              <div>文件名: <span style="color:var(--accent-cyan)">{{ fileInfo.name }}</span></div>
              <div>文件大小: <span style="color:var(--accent-cyan)">{{ formatSize(fileInfo.size) }}</span></div>
              <div>文件类型: <span style="color:var(--accent-cyan)">{{ fileInfo.type || '未知' }}</span></div>
            </div>
            <button
              v-if="isImageFile && !imageDescription"
              class="demo-action-btn"
              @click="runImageIndex"
            >
              <span>▶</span> 生成图片描述
            </button>
            <div class="highlight-block" style="font-size:0.82rem;margin-top:8px">
              <div style="font-weight:600;color:var(--text-primary);margin-bottom:6px">VLM 训练模式</div>
              <div>图片通过视觉语言模型自动生成描述文本，支持：</div>
              <div style="margin-top:4px">• 自动识别图中文字 (OCR)</div>
              <div>• 场景与物体描述</div>
              <div>• 图表数据解读</div>
              <div>• 生成可检索的语义向量</div>
            </div>
          </template>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const fileInput = ref(null)
const activeStep = ref(0)
const uploadedFile = ref(null)
const rawText = ref('')
const formatText = ref('')
const parsedResult = ref('')
const markdownText = ref(null)
const convertResults = ref([])
const mdConversionNote = ref('')
const cleanedText = ref('')
const textBeforeClean = ref('')
const chunks = ref([])
const loading = ref(false)
const errorMsg = ref('')
const fileInfo = ref(null)
const parseMethod = ref('text')
const isDragOver = ref(false)
const imagePreview = ref(null)
const imageDescription = ref('')
const imageMeta = ref(null)
const selectedSheet = ref(null)
const sheetNames = ref([])

const cleanOptions = ref({
  trim: true,
  normalize_unicode: true,
  remove_invisible_chars: true,
  remove_chinese_space: true,
  normalize_newline: true,
  fix_hyphenation: true,
  collapse_whitespace: true,
  remove_empty_lines: true,
  remove_html_comments: false,
  normalize_html_entities: false,
  filter_html_noise: false,
  html_noise_patterns: '',
  html_ad_keywords: '',
  filter_watermark: false,
  watermark_keywords: '',
  filter_toc: false,
  filter_page_numbers: false,
  process_footnotes: false,
  footnote_action: 'remove',
  deduplicate_paragraphs: false,
  dedup_fuzzy: false,
  clean_table: false,
  clean_markdown_links: true,
  remove_md_escapes: true,
  clean_md_structure: true,
  mask_sensitive: false,
  filter_special_chars: false
})

const CLEAN_PROFILES = {
  default: { label: '默认', options: { trim: true, normalize_unicode: true, remove_invisible_chars: true, remove_chinese_space: true, normalize_newline: true, fix_hyphenation: true, collapse_whitespace: true, remove_empty_lines: true, remove_html_comments: false, normalize_html_entities: false, filter_html_noise: false, html_noise_patterns: '', html_ad_keywords: '', filter_watermark: false, watermark_keywords: '', filter_toc: false, filter_page_numbers: false, process_footnotes: false, footnote_action: 'remove', deduplicate_paragraphs: false, dedup_fuzzy: false, clean_table: false, clean_markdown_links: true, remove_md_escapes: true, clean_md_structure: true, mask_sensitive: false, filter_special_chars: false } },
  pdf_academic: { label: '学术论文 PDF', options: { trim: true, normalize_unicode: true, remove_invisible_chars: true, remove_chinese_space: true, normalize_newline: true, fix_hyphenation: true, collapse_whitespace: true, remove_empty_lines: true, remove_html_comments: false, normalize_html_entities: false, filter_html_noise: false, html_noise_patterns: '', html_ad_keywords: '', filter_watermark: false, watermark_keywords: '', filter_toc: true, filter_page_numbers: true, process_footnotes: true, footnote_action: 'keep', deduplicate_paragraphs: false, dedup_fuzzy: false, clean_table: false, clean_markdown_links: true, remove_md_escapes: true, clean_md_structure: true, mask_sensitive: false, filter_special_chars: false } },
  pdf_business: { label: '商务 PDF', options: { trim: true, normalize_unicode: true, remove_invisible_chars: true, remove_chinese_space: true, normalize_newline: true, fix_hyphenation: true, collapse_whitespace: true, remove_empty_lines: true, remove_html_comments: false, normalize_html_entities: false, filter_html_noise: false, html_noise_patterns: '', html_ad_keywords: '', filter_watermark: true, watermark_keywords: '', filter_toc: false, filter_page_numbers: true, process_footnotes: false, footnote_action: 'remove', deduplicate_paragraphs: false, dedup_fuzzy: false, clean_table: false, clean_markdown_links: true, remove_md_escapes: true, clean_md_structure: true, mask_sensitive: false, filter_special_chars: false } },
  docx_report: { label: 'DOCX 报告', options: { trim: true, normalize_unicode: true, remove_invisible_chars: true, remove_chinese_space: true, normalize_newline: true, fix_hyphenation: true, collapse_whitespace: true, remove_empty_lines: true, remove_html_comments: false, normalize_html_entities: false, filter_html_noise: false, html_noise_patterns: '', html_ad_keywords: '', filter_watermark: false, watermark_keywords: '', filter_toc: true, filter_page_numbers: false, process_footnotes: true, footnote_action: 'keep', deduplicate_paragraphs: false, dedup_fuzzy: false, clean_table: false, clean_markdown_links: true, remove_md_escapes: true, clean_md_structure: true, mask_sensitive: false, filter_special_chars: false } },
  table_data: { label: '表格数据', options: { trim: true, normalize_unicode: true, remove_invisible_chars: true, remove_chinese_space: true, normalize_newline: true, fix_hyphenation: true, collapse_whitespace: true, remove_empty_lines: true, remove_html_comments: false, normalize_html_entities: false, filter_html_noise: false, html_noise_patterns: '', html_ad_keywords: '', filter_watermark: false, watermark_keywords: '', filter_toc: false, filter_page_numbers: false, process_footnotes: false, footnote_action: 'remove', deduplicate_paragraphs: false, dedup_fuzzy: false, clean_table: true, clean_markdown_links: true, remove_md_escapes: true, clean_md_structure: true, mask_sensitive: false, filter_special_chars: false } },
  legal: { label: '法律文书', options: { trim: true, normalize_unicode: true, remove_invisible_chars: true, remove_chinese_space: true, normalize_newline: true, fix_hyphenation: true, collapse_whitespace: true, remove_empty_lines: true, remove_html_comments: false, normalize_html_entities: false, filter_html_noise: false, html_noise_patterns: '', html_ad_keywords: '', filter_watermark: false, watermark_keywords: '', filter_toc: true, filter_page_numbers: false, process_footnotes: true, footnote_action: 'keep', deduplicate_paragraphs: false, dedup_fuzzy: false, clean_table: false, clean_markdown_links: true, remove_md_escapes: true, clean_md_structure: true, mask_sensitive: false, filter_special_chars: false } },
  web_content: { label: '网页内容', options: { trim: true, normalize_unicode: true, remove_invisible_chars: true, remove_chinese_space: true, normalize_newline: true, fix_hyphenation: true, collapse_whitespace: true, remove_empty_lines: true, remove_html_comments: true, normalize_html_entities: true, filter_html_noise: true, html_noise_patterns: '', html_ad_keywords: '', filter_watermark: true, watermark_keywords: '', filter_toc: false, filter_page_numbers: false, process_footnotes: false, footnote_action: 'remove', deduplicate_paragraphs: false, dedup_fuzzy: false, clean_table: false, clean_markdown_links: true, remove_md_escapes: true, clean_md_structure: true, mask_sensitive: false, filter_special_chars: false } },
  custom: { label: '自定义', options: null },
}

const selectedProfile = ref('default')

function applyProfile(profileName) {
  const profile = CLEAN_PROFILES[profileName]
  if (profile && profile.options) {
    Object.assign(cleanOptions.value, JSON.parse(JSON.stringify(profile.options)))
    selectedProfile.value = profileName
  }
}

function isOptionsEqual(a, b) {
  if (!b) return false
  return Object.keys(b).every(key => a[key] === b[key])
}

watch(cleanOptions, (newVal) => {
  const currentProfile = CLEAN_PROFILES[selectedProfile.value]
  if (currentProfile && currentProfile.options && !isOptionsEqual(newVal, currentProfile.options)) {
    selectedProfile.value = 'custom'
  }
}, { deep: true })

const CLEAN_RULE_DESCRIPTIONS = {
  trim: {
    desc: '移除文本开头和结尾的空白字符（空格、Tab、换行等）',
    examples: ['  hello  → hello', '\\t文本\\t → 文本']
  },
  normalize_unicode: {
    desc: '使用 NFKC 形式统一全角/半角字符和兼容性字符，确保文本检索一致性',
    examples: ['ＡＢＣ → ABC', '１２３ → 123', '！？ → !?', '①②③ → 123', 'ﬁ → fi']
  },
  remove_invisible_chars: {
    desc: '移除零宽空格(U+200B)、BOM(U+FEFF)、软连字符(U+00AD)等不可见但影响匹配的字符',
    examples: ['hello\\u200Bworld → helloworld', '\\uFEFF文本 → 文本', 'soft\\u00ADhyphen → softhyphen']
  },
  remove_chinese_space: {
    desc: '移除中文字符之间的多余空格，保留中英文混排时的必要空格',
    examples: ['你好 世界 → 你好世界', 'hello 世界 → hello 世界']
  },
  normalize_newline: {
    desc: '将 Windows(\\r\\n) 和旧 Mac(\\r) 换行符统一为 Unix 格式(\\n)',
    examples: ['行1\\r\\n行2 → 行1\\n行2', '行1\\r行2 → 行1\\n行2']
  },
  fix_hyphenation: {
    desc: '修复 PDF 提取中因断行产生的连字符分割，还原完整单词',
    examples: ['com-\\nputer → computer', 'awe-\\nsome → awesome']
  },
  collapse_whitespace: {
    desc: '将 2 个及以上连续非换行空白字符合并为 1 个空格',
    examples: ['hello    world → hello world', 'a  \\t  b → a b']
  },
  remove_empty_lines: {
    desc: '将 3 行及以上连续换行压缩为 2 行，保留段落分隔',
    examples: ['行1\\n\\n\\n\\n行2 → 行1\\n\\n行2']
  },
  mask_sensitive: {
    desc: '使用占位符替换身份证号、银行卡号、护照号、军官证、手机号、邮箱、IP 地址等敏感信息（默认关闭）',
    examples: ['13812345678 → ***PHONE***', 'test@mail.com → ***EMAIL***', '110101199001011234 → ***IDCARD***', '6222021234567890 → ***BANKCARD***', 'E12345678 → ***PASSPORT***']
  },
  filter_special_chars: {
    desc: '仅保留中文、英文、数字、常用标点和括号，移除异常符号和乱码字符（默认关闭）',
    examples: ['你好★世界 → 你好世界', 'test♦123 → test123', '中文，标点！ → 中文，标点！']
  },
  filter_watermark: {
    desc: '过滤文档中的水印文本，检测重复出现的短行和内置水印关键词（如 CONFIDENTIAL、机密等）（默认关闭）',
    examples: ['重复3次的"CONFIDENTIAL" → 移除', '含"机密"的短行 → 移除', '支持自定义关键词']
  },
  deduplicate_paragraphs: {
    desc: '检测并移除重复段落，支持精确哈希去重和可选的模糊去重（基于编辑距离相似度）（默认关闭）',
    examples: ['完全相同的段落 → 保留一个', '相似度≥90%的段落 → 可选移除', '模糊去重需单独开启']
  },
  clean_table: {
    desc: '清洗 Markdown 表格，移除全空行和全空列，确保表头结构正确（默认关闭）',
    examples: ['| | | → 移除空行', '空列 → 移除空列', '保留有效数据和表头']
  },
  filter_toc: {
    desc: '检测并移除自动生成的目录区域，需连续 ≥3 行目录条目才触发过滤（默认关闭）',
    examples: ['1.1 概述 .... 12 → 移除', '第一章 引言 → 移除', '附录A 数据表 → 移除']
  },
  filter_page_numbers: {
    desc: '移除独立成行的页码文本，如纯数字行、带横线页码、中文/英文页码（默认关闭）',
    examples: ['独立行 "12" → 移除', '- 5 - → 移除', '第 12 页 → 移除', 'Page 42 → 移除']
  },
  process_footnotes: {
    desc: '识别脚注/尾注标记（如[1]、①），可选移除或保留脚注内容行（默认关闭）',
    examples: ['[1] 脚注说明 → 可移除', '①注释内容 → 可移除', '支持保留模式']
  },
  remove_html_comments: {
    desc: '移除 HTML 注释标记（<!-- ... -->），包括多行注释',
    examples: ['<!-- comment --> → 移除', '多行注释 → 移除']
  },
  normalize_html_entities: {
    desc: '将 HTML 命名实体（&amp;等）和数字引用（&#65;等）转换为 Unicode 字符',
    examples: ['&amp; → &', '&nbsp; → 空格', '&copy; → ©', '&#65; → A']
  },
  filter_html_noise: {
    desc: '移除版权声明、ICP备案、免责声明、广告关键词等网页噪声内容（默认关闭）',
    examples: ['copyright © 2024 → 移除', '沪ICP备xxx号 → 移除', '免责声明：... → 移除']
  },
  clean_markdown_links: {
    desc: '移除 Markdown 链接文本中的换行符，确保链接格式正确',
    examples: ['[hello\\nworld](url) → [helloworld](url)']
  },
  remove_md_escapes: {
    desc: '移除不必要的 Markdown 反斜杠转义，还原被转义的字符',
    examples: ['\\*bold\\* → *bold*', '\\#heading → #heading']
  },
  clean_md_structure: {
    desc: '移除 Markdown 结构元素（标题、代码块）前的多余空格',
    examples: ['  ## heading → ## heading', '  ```python → ```python']
  }
}

const chunkParams = ref({
  chunkSize: 500,
  overlapRatio: 0.2,
  paragraphChunkDeep: 2
})

const steps = [
  { label: '文档解析' },
  { label: 'Markdown转换' },
  { label: '数据清洗' },
  { label: '文本分块' },
  { label: '图片索引' }
]

const IMAGE_EXTS = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp']

const isImageFile = computed(() => {
  return fileInfo.value ? IMAGE_EXTS.includes(fileInfo.value.ext) : false
})

const selectedEngine = ref('fastgpt')
const engineResults = ref({})
const headerFooterRatio = ref(0.05)
const MINERU_SUPPORTED_EXTS = ['pdf', 'docx', 'doc', 'pptx', 'png', 'jpg', 'jpeg', 'gif', 'webp']

const mdTools = [
  { value: 'markitdown', label: 'MarkItDown' },
  { value: 'markdownify', label: 'Markdownify' },
]
const selectedMdTools = ref(['markitdown'])

function toggleMdTool(toolValue) {
  const idx = selectedMdTools.value.indexOf(toolValue)
  if (idx >= 0) {
    if (selectedMdTools.value.length <= 1) return
    selectedMdTools.value.splice(idx, 1)
  } else {
    if (selectedMdTools.value.length >= 2) return
    selectedMdTools.value.push(toolValue)
  }
}

const isMineruAvailable = computed(() => {
  if (!fileInfo.value) return false
  return MINERU_SUPPORTED_EXTS.includes(fileInfo.value.ext.toLowerCase())
})

const engines = computed(() => {
  const list = [{ value: 'fastgpt', label: 'FastGPT 默认' }]
  if (isMineruAvailable.value) {
    list.push({ value: 'mineru', label: 'MinerU' })
  }
  return list
})

const hasMultipleResults = computed(() => {
  return Object.keys(engineResults.value).filter(k => engineResults.value[k]).length > 1
})

const parseMethods = computed(() => {
  if (!fileInfo.value) return [{ value: 'text', label: '纯文本' }]
  const ext = fileInfo.value.ext
  const methods = []
  if (ext === 'pdf') {
    methods.push({ value: 'text', label: '文本提取' })
  } else if (ext === 'docx' || ext === 'doc') {
    methods.push({ value: 'html', label: 'HTML转换' })
    methods.push({ value: 'text', label: '纯文本提取' })
  } else if (ext === 'csv') {
    methods.push({ value: 'table', label: '表格解析' })
    methods.push({ value: 'raw', label: '原始文本' })
  } else if (ext === 'xlsx' || ext === 'xls') {
    methods.push({ value: 'table', label: '表格解析' })
  } else if (ext === 'html' || ext === 'htm') {
    methods.push({ value: 'html', label: 'HTML预览' })
    methods.push({ value: 'text', label: '纯文本提取' })
  } else if (['txt', 'md', 'json', 'js', 'ts', 'py'].includes(ext)) {
    methods.push({ value: 'text', label: '纯文本' })
  } else if (IMAGE_EXTS.includes(ext)) {
    methods.push({ value: 'image', label: '图片预览' })
  } else {
    methods.push({ value: 'text', label: '纯文本' })
  }
  return methods
})

const avgChunkSize = computed(() => {
  if (chunks.value.length === 0) return 0
  return Math.round(chunks.value.reduce((s, c) => s + c.length, 0) / chunks.value.length)
})

const isDocxHtmlMode = computed(() => {
  const ext = fileInfo.value?.ext
  return (ext === 'docx' || ext === 'doc' || ext === 'html' || ext === 'htm') && parseMethod.value === 'html'
})

const mdConversionMethod = computed(() => {
  if (!fileInfo.value) return '未知'
  const ext = fileInfo.value.ext
  if (ext === 'docx' || ext === 'doc') return 'turndown (HTML→MD)'
  if (ext === 'csv' || ext === 'xlsx' || ext === 'xls') return '字符串拼接 (表格→MD)'
  if (ext === 'html') return 'turndown (HTML→MD)'
  if (ext === 'md') return '原样保留'
  return '无转换 (纯文本)'
})

const isMarkdownOutput = computed(() => {
  const ext = fileInfo.value?.ext
  return ['docx', 'doc', 'csv', 'xlsx', 'xls', 'html', 'md'].includes(ext)
})

function getExt(filename) {
  return filename.split('.').pop().toLowerCase()
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

function triggerUpload() {
  fileInput.value?.click()
}

function handleFileSelect(e) {
  const file = e.target.files?.[0]
  if (file) processFile(file)
}

function handleDrop(e) {
  isDragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) processFile(file)
}

function processFile(file) {
  uploadedFile.value = file
  fileInfo.value = {
    name: file.name,
    size: file.size,
    ext: getExt(file.name),
    type: file.type
  }
  activeStep.value = 0
  chunks.value = []
  cleanedText.value = ''
  textBeforeClean.value = ''
  markdownText.value = null
  convertResults.value = []
  mdConversionNote.value = ''
  selectedMdTools.value = ['markitdown']
  formatText.value = ''
  parsedResult.value = ''
  rawText.value = ''
  imageDescription.value = ''
  imageMeta.value = null
  sheetNames.value = []
  selectedSheet.value = null
  errorMsg.value = ''
  engineResults.value = {}
  selectedEngine.value = 'fastgpt'

  if (fileInfo.value.ext === 'xlsx' || fileInfo.value.ext === 'xls') {
    parseMethod.value = 'table'
  } else {
    parseMethod.value = parseMethods.value[0]?.value || 'text'
  }

  if (IMAGE_EXTS.includes(fileInfo.value.ext)) {
    const reader = new FileReader()
    reader.onload = (e) => { imagePreview.value = e.target.result }
    reader.readAsDataURL(file)
  } else {
    imagePreview.value = null
  }
}

async function apiCall(path, options) {
  errorMsg.value = ''
  const res = await fetch(`${API_BASE}${path}`, options)
  if (!res.ok) {
    const errBody = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(errBody.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

async function runParse() {
  if (!uploadedFile.value) return
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadedFile.value)
    formData.append('method', 'auto')
    formData.append('engine', selectedEngine.value)
    formData.append('header_footer_ratio', headerFooterRatio.value)

    const data = await apiCall('/api/parse', { method: 'POST', body: formData })

    rawText.value = data.raw_text || ''
    formatText.value = data.format_text || ''
    parsedResult.value = data.html_preview || ''
    sheetNames.value = data.sheet_names || []

    engineResults.value[selectedEngine.value] = data

    if (sheetNames.value.length > 0 && !selectedSheet.value) {
      selectedSheet.value = sheetNames.value[0]
    }
  } catch (err) {
    parsedResult.value = `<div style="color:var(--accent-red)">解析失败: ${err.message}</div>`
    rawText.value = ''
    errorMsg.value = err.message
  }
  loading.value = false
}

async function runMarkdownConvert() {
  if (!rawText.value) {
    markdownText.value = ''
    mdConversionNote.value = '请先完成文档解析'
    return
  }

  loading.value = true
  try {
    const data = await apiCall('/api/convert', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        raw_text: rawText.value,
        format_text: formatText.value,
        file_ext: fileInfo.value.ext,
        tools: selectedMdTools.value
      })
    })
    convertResults.value = data.results || []
    markdownText.value = convertResults.value.length > 0
      ? convertResults.value[0].markdown
      : ''
    mdConversionNote.value = convertResults.value.length > 0
      ? convertResults.value[0].note
      : ''
  } catch (err) {
    markdownText.value = ''
    mdConversionNote.value = '转换失败: ' + err.message
    convertResults.value = []
    errorMsg.value = err.message
  }
  loading.value = false
}

async function runCleaning() {
  const source = markdownText.value !== null ? markdownText.value : rawText.value
  if (!source) {
    cleanedText.value = ''
    return
  }
  textBeforeClean.value = source

  loading.value = true
  try {
    const opts = { ...cleanOptions.value }
    if (opts.watermark_keywords && typeof opts.watermark_keywords === 'string') {
      opts.watermark_keywords = opts.watermark_keywords.split(/[,，]/).map(k => k.trim()).filter(k => k)
    } else {
      opts.watermark_keywords = []
    }
    if (opts.html_noise_patterns && typeof opts.html_noise_patterns === 'string') {
      opts.html_noise_patterns = opts.html_noise_patterns.split(/[,，]/).map(k => k.trim()).filter(k => k)
    } else {
      opts.html_noise_patterns = []
    }
    if (opts.html_ad_keywords && typeof opts.html_ad_keywords === 'string') {
      opts.html_ad_keywords = opts.html_ad_keywords.split(/[,，]/).map(k => k.trim()).filter(k => k)
    } else {
      opts.html_ad_keywords = []
    }
    const data = await apiCall('/api/clean', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: source,
        options: opts
      })
    })
    cleanedText.value = data.cleaned || ''
  } catch (err) {
    cleanedText.value = source
    errorMsg.value = err.message
  }
  loading.value = false
}

async function runChunking() {
  if (!cleanedText.value) { chunks.value = []; return }

  loading.value = true
  try {
    const data = await apiCall('/api/chunk', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: cleanedText.value,
        chunk_size: chunkParams.value.chunkSize,
        overlap_ratio: chunkParams.value.overlapRatio,
        paragraph_chunk_deep: chunkParams.value.paragraphChunkDeep
      })
    })
    chunks.value = data.chunks || []
  } catch (err) {
    chunks.value = []
    errorMsg.value = err.message
  }
  loading.value = false
}

async function runImageIndex() {
  if (!uploadedFile.value || !isImageFile.value) return

  loading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadedFile.value)

    const data = await apiCall('/api/index-image', { method: 'POST', body: formData })
    imageDescription.value = data.description || ''
    imageMeta.value = {
      width: data.width,
      height: data.height,
      format: data.format,
      size_bytes: data.size_bytes
    }
  } catch (err) {
    imageDescription.value = ''
    errorMsg.value = err.message
  }
  loading.value = false
}

watch(parseMethod, async () => {
  if (!uploadedFile.value || !rawText.value) return
})
</script>

<style scoped>
.demo-page {
  max-width: 1200px;
  margin: 0 auto;
}

.demo-header {
  margin-bottom: 20px;
}

.demo-header h2 {
  font-size: 1.4rem;
  font-weight: 600;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-green));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 6px;
}

.demo-header p {
  font-size: 0.85rem;
  color: var(--text-muted);
  line-height: 1.5;
}

/* Upload Zone */
.demo-upload-zone {
  border: 2px dashed var(--border-light);
  border-radius: 12px;
  padding: 36px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s ease;
  background: var(--bg-secondary);
  margin-bottom: 16px;
}

.demo-upload-zone:hover,
.demo-upload-zone.drag-over {
  border-color: var(--accent-cyan);
  background: rgba(6, 182, 212, 0.04);
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.08);
}

.upload-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 8px;
}

.upload-text {
  font-size: 0.95rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.upload-hint {
  font-size: 0.78rem;
  color: var(--text-muted);
}

/* File Info */
.demo-file-info {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.info-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 0.82rem;
}

.info-label {
  color: var(--text-muted);
}

.info-value {
  color: var(--accent-cyan);
  font-family: var(--font-mono);
}

/* Steps Tabs */
.demo-steps {
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.demo-step-tab {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-muted);
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: var(--font-body);
}

.demo-step-tab:hover {
  background: var(--bg-hover);
  color: var(--text-secondary);
  border-color: var(--border-light);
}

.demo-step-tab.active {
  background: rgba(6, 182, 212, 0.1);
  border-color: var(--accent-cyan);
  color: var(--accent-cyan);
  font-weight: 500;
}

/* Loading */
.demo-loading {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px;
  color: var(--accent-cyan);
  font-size: 0.9rem;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-light);
  border-top-color: var(--accent-cyan);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error */
.demo-error {
  padding: 10px 16px;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  color: var(--accent-red);
  font-size: 0.85rem;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Layout */
.demo-layout {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.compare-view {
  display: flex;
  gap: 16px;
}

.compare-column {
  flex: 1;
  min-width: 0;
}

.compare-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--accent-cyan);
  margin-bottom: 8px;
  padding: 4px 8px;
  background: rgba(99, 102, 241, 0.06);
  border-radius: 6px;
  display: inline-block;
}

.compare-stat {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-top: 4px;
}

@media (max-width: 768px) {
  .compare-view { flex-direction: column; }
}

.demo-result-panel {
  flex: 1;
  min-width: 0;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  overflow: hidden;
}

.demo-options-panel {
  width: 320px;
  flex-shrink: 0;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.result-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.result-content {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px;
  font-family: var(--font-mono);
  font-size: 0.82rem;
  line-height: 1.7;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 500px;
  overflow-y: auto;
}

.result-content.html-content {
  white-space: normal;
  font-family: var(--font-body);
}

.result-content.html-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 8px 0;
}

.result-content.html-content :deep(th),
.result-content.html-content :deep(td) {
  border: 1px solid var(--border-color);
  padding: 6px 10px;
  font-size: 0.8rem;
}

.result-content.html-content :deep(th) {
  background: var(--bg-tertiary);
  color: var(--accent-cyan);
  font-weight: 500;
}

.result-content.html-content :deep(td) {
  color: var(--text-secondary);
}

.demo-fulltext-box {
  max-height: 220px;
  overflow-y: auto;
}

.empty-state {
  padding: 32px 16px;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.85rem;
  line-height: 1.6;
}

/* Options */
.option-title {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text-primary);
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.demo-option-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
  color: var(--text-secondary);
}

.demo-option-item select {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 4px 8px;
  color: var(--text-primary);
  font-size: 0.82rem;
  font-family: var(--font-body);
  outline: none;
}

.demo-option-item select:focus {
  border-color: var(--accent-cyan);
}

.demo-option-item input[type="checkbox"] {
  accent-color: var(--accent-cyan);
  width: 15px;
  height: 15px;
}

.watermark-keywords-input {
  width: 100%;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 4px 8px;
  color: var(--text-primary);
  font-size: 0.78rem;
  font-family: var(--font-body);
  outline: none;
  transition: border-color 0.2s ease;
}

.watermark-keywords-input:focus {
  border-color: var(--accent-cyan);
}

/* Rule info tooltip */
.rule-info-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--bg-tertiary);
  color: var(--text-muted);
  font-size: 0.6rem;
  font-style: italic;
  cursor: help;
  position: relative;
  flex-shrink: 0;
  transition: all 0.2s ease;
  user-select: none;
}

.rule-info-trigger:hover,
.rule-info-trigger:focus {
  background: var(--accent-cyan);
  color: #fff;
  outline: none;
}

.rule-info-tooltip {
  position: absolute;
  left: calc(100% + 8px);
  top: 50%;
  transform: translateY(-50%);
  width: 260px;
  padding: 10px 12px;
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.18);
  z-index: 100;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s ease, visibility 0.2s ease;
  pointer-events: none;
  text-align: left;
}

.rule-info-trigger:hover .rule-info-tooltip,
.rule-info-trigger:focus .rule-info-tooltip {
  opacity: 1;
  visibility: visible;
}

.tooltip-desc {
  display: block;
  font-size: 0.78rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 6px;
}

.tooltip-examples {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.example-label {
  font-size: 0.7rem;
  color: var(--accent-cyan);
  font-weight: 500;
  margin-bottom: 2px;
}

.example-item {
  font-size: 0.72rem;
  font-family: var(--font-mono);
  color: var(--text-muted);
  line-height: 1.5;
  white-space: nowrap;
}

.demo-action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: var(--font-body);
  margin-top: 4px;
}

.demo-action-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.2);
}

.demo-action-btn:active {
  transform: translateY(0);
}

.highlight-block {
  padding: 10px 12px;
  background: rgba(6, 182, 212, 0.04);
  border-radius: 8px;
  border-left: 3px solid var(--accent-cyan);
  color: var(--text-secondary);
  line-height: 1.6;
}

.demo-slider-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.demo-slider-group label {
  font-size: 0.82rem;
  color: var(--text-secondary);
  display: flex;
  justify-content: space-between;
}

.demo-slider-group label span {
  color: var(--accent-cyan);
  font-family: var(--font-mono);
  font-weight: 500;
}

.demo-slider-group input[type="range"] {
  width: 100%;
  accent-color: var(--accent-cyan);
  height: 4px;
}

/* Chunks */
.demo-chunk-item {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin-bottom: 8px;
  overflow: hidden;
}

.chunk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 12px;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
}

.chunk-index {
  font-size: 0.78rem;
  color: var(--accent-cyan);
  font-weight: 500;
  font-family: var(--font-mono);
}

.chunk-size {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}

.chunk-text {
  padding: 10px 12px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  line-height: 1.65;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}

/* Image Preview */
.demo-image-preview {
  max-width: 100%;
  border-radius: 8px;
  margin-bottom: 12px;
  border: 1px solid var(--border-color);
}

/* Stats Bar */
.demo-stats-bar {
  display: flex;
  gap: 16px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.stat-value {
  font-family: var(--font-mono);
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--accent-cyan);
}

.stat-label {
  font-size: 0.72rem;
  color: var(--text-muted);
}

/* Responsive */
@media (max-width: 768px) {
  .demo-layout {
    flex-direction: column;
  }

  .demo-options-panel {
    width: 100%;
  }

  .demo-file-info {
    flex-direction: column;
    gap: 6px;
  }

  .demo-steps {
    gap: 4px;
  }

  .demo-step-tab {
    padding: 6px 10px;
    font-size: 0.78rem;
  }

  .demo-stats-bar {
    gap: 10px;
  }
}
</style>
