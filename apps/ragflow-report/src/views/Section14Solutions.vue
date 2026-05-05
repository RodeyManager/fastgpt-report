<template>
  <div class="section-page">
    <div class="section-header">
      <h2>§14 行业智能解决方案</h2>
      <p>RAGFlow 赋能三大核心行业场景，从金融投资到法律分析再到制造业维护，开箱即用的智能解决方案。</p>
    </div>

    <!-- 前两个方案并排 -->
    <div class="two-col">
      <!-- 股票投资研究 -->
      <div class="card">
        <div class="card-title"><span class="icon">📈</span>股票投资研究</div>
        <p style="color:var(--text-secondary); font-size:0.88rem; margin-bottom:16px;">
          自动化企业数据收集，财务指标与研究见解整合，辅助投资决策。
        </p>
        <div class="flow-diagram" style="padding:20px 16px;">
          <div style="display:flex; flex-direction:column; align-items:center; gap:0;">
            <div class="flow-step" style="min-width:140px;">
              🏷️ 识别股票代码<br><small>自动识别目标标的</small>
            </div>
            <div style="width:2px; height:16px; background:rgba(16,185,129,0.5);"></div>
            <div class="flow-step" style="min-width:140px;">
              📊 数据汇总<br><small>外部 + 内部数据整合</small>
            </div>
            <div style="width:2px; height:16px; background:rgba(16,185,129,0.5);"></div>
            <div class="flow-step" style="min-width:140px;">
              🔬 深度分析<br><small>定性 + 定量综合分析</small>
            </div>
            <div style="width:2px; height:16px; background:rgba(16,185,129,0.5);"></div>
            <div class="flow-step primary" style="min-width:140px;">
              📋 投资报告<br><small>结构化研究输出</small>
            </div>
          </div>
        </div>
        <div class="highlight-block">
          <strong>核心价值：</strong>将数小时的研报阅读和数据整理压缩至分钟级，自动提取财务指标、行业趋势和风险因素。
        </div>
      </div>

      <!-- 法律判例分析 -->
      <div class="card">
        <div class="card-title"><span class="icon">⚖️</span>法律判例分析</div>
        <p style="color:var(--text-secondary); font-size:0.88rem; margin-bottom:16px;">
          结构化判例分析，快速检索可比案例，生成专业法律分析报告。
        </p>
        <div class="flow-diagram" style="padding:20px 16px;">
          <div style="display:flex; flex-direction:column; align-items:center; gap:0;">
            <div class="flow-step" style="min-width:140px;">
              📝 案件输入<br><small>案件描述与材料</small>
            </div>
            <div style="width:2px; height:16px; background:rgba(16,185,129,0.5);"></div>
            <div class="flow-step" style="min-width:140px;">
              🔑 属性提取<br><small>关键法律要素识别</small>
            </div>
            <div style="width:2px; height:16px; background:rgba(16,185,129,0.5);"></div>
            <div class="flow-step" style="min-width:140px;">
              🔍 判例检索<br><small>可比案例搜索匹配</small>
            </div>
            <div style="width:2px; height:16px; background:rgba(16,185,129,0.5);"></div>
            <div class="flow-step primary" style="min-width:140px;">
              📋 分析报告<br><small>结构化法律意见</small>
            </div>
          </div>
        </div>
        <div class="highlight-block">
          <strong>核心价值：</strong>基于海量判例库的语义检索，秒级定位相关判例，自动生成结构化分析报告，大幅提升律师研究效率。
        </div>
      </div>
    </div>

    <!-- 制造业维护支持 — 全宽 -->
    <div class="card">
      <div class="card-title"><span class="icon">🏭</span>制造业维护支持</div>
      <p style="color:var(--text-secondary); font-size:0.88rem; margin-bottom:16px;">
        智能维护指导，整合内部手册与外部技术数据，提供精准执行指令。
      </p>
      <div class="flow-diagram">
        <div class="flow-steps">
          <div class="flow-step">
            📋 任务输入<br><small>维护任务描述</small>
          </div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">
            ✅ 充分性验证<br><small>信息完整性检查</small>
          </div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">
            📖 手册提取<br><small>内部维修手册检索</small>
          </div>
          <div class="flow-arrow">→</div>
          <div class="flow-step">
            🌐 外部数据<br><small>技术资料整合</small>
          </div>
          <div class="flow-arrow">→</div>
          <div class="flow-step primary">
            🔧 执行指令<br><small>步骤化维护指南</small>
          </div>
        </div>
      </div>
      <div class="highlight-block" style="margin-top:12px;">
        <strong>核心价值：</strong>将分散的维修手册、技术文档和经验知识整合为即时可用的维护指南，减少设备停机时间，提升维护质量和一致性。
      </div>
    </div>

    <!-- 方案共性优势 -->
    <div class="card">
      <div class="card-title"><span class="icon">✨</span>方案共性优势</div>
      <div class="three-col">
        <div class="metric-card" style="text-align:left; padding:20px;">
          <div style="font-size:1.6rem; margin-bottom:8px;">⚡</div>
          <div style="font-weight:600; color:#fff; margin-bottom:6px;">分钟级响应</div>
          <div style="font-size:0.82rem; color:var(--text-secondary);">传统数小时的信息检索和分析工作压缩至分钟级完成</div>
        </div>
        <div class="metric-card" style="text-align:left; padding:20px;">
          <div style="font-size:1.6rem; margin-bottom:8px;">🎯</div>
          <div style="font-weight:600; color:#fff; margin-bottom:6px;">高精度检索</div>
          <div style="font-size:0.82rem; color:var(--text-secondary);">混合检索 + Rerank 重排序确保结果的相关性和准确性</div>
        </div>
        <div class="metric-card" style="text-align:left; padding:20px;">
          <div style="font-size:1.6rem; margin-bottom:8px;">🔌</div>
          <div style="font-weight:600; color:#fff; margin-bottom:6px;">低代码集成</div>
          <div style="font-size:0.82rem; color:var(--text-secondary);">可视化工作流编排，业务人员可快速构建和调整方案</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 纯模板组件，无额外逻辑
</script>
