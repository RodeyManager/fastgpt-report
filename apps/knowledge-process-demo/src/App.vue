<template>
  <div class="app-root">
    <header class="app-header">
      <h1 class="app-title">知识库文档处理流水线</h1>
      <span class="app-subtitle">FastGPT Knowledge Process Demo</span>
    </header>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');

*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --bg-primary: #0a0e1a;
  --bg-secondary: #0f1525;
  --bg-tertiary: #141b2d;
  --bg-card: #1a2332;
  --bg-hover: #1e2a3a;
  --border-color: #1e2d3d;
  --border-light: #2a3a4d;
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --accent-cyan: #06b6d4;
  --accent-green: #00ff88;
  --accent-blue: #6366f1;
  --accent-orange: #f59e0b;
  --accent-red: #ef4444;
  --accent-purple: #a78bfa;
  --font-body: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
}

html {
  font-size: 14px;
  scroll-behavior: smooth;
}

body {
  font-family: var(--font-body);
  background: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.6;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  padding: 16px 24px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: baseline;
  gap: 12px;
  flex-shrink: 0;
}

.app-title {
  font-size: 1.25rem;
  font-weight: 600;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-green));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.app-subtitle {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}

.app-main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
</style>
