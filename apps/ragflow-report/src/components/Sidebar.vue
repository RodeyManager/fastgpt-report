<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h1>RAGFlow RAG 分析</h1>
      <p>底座能力深度报告 v0.24.0</p>
    </div>
    <nav class="sidebar-nav">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
      >
        <span class="nav-num">{{ item.num }}</span>
        <component :is="item.icon" class="nav-icon" />
        <span>{{ item.label }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
import { h } from 'vue'

const createIcon = (paths) => ({
  render() {
    return h('svg', {
      viewBox: '0 0 24 24', fill: 'none',
      stroke: 'currentColor', 'stroke-width': '2',
      'stroke-linecap': 'round', 'stroke-linejoin': 'round',
      innerHTML: paths
    })
  }
})

const navItems = [
  { path: '/overview', num: '01', label: '项目架构概览', icon: createIcon('<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>') },
  { path: '/knowledge', num: '02', label: '知识库管理', icon: createIcon('<path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/>') },
  { path: '/upload', num: '03', label: '文档上传', icon: createIcon('<path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>') },
  { path: '/deepdoc', num: '04', label: '文档解析 DeepDoc', icon: createIcon('<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>') },
  { path: '/cleaning', num: '05', label: '数据清洗', icon: createIcon('<path d="M12 3v18"/><path d="M4 7l16 0"/><path d="M4 12l16 0"/><path d="M4 17l16 0"/>') },
  { path: '/chunking', num: '06', label: '文本分块', icon: createIcon('<rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/>') },
  { path: '/embedding', num: '07', label: '向量化', icon: createIcon('<circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="8" opacity="0.4"/><circle cx="12" cy="12" r="11" opacity="0.2"/>') },
  { path: '/retrieval', num: '08', label: '检索', icon: createIcon('<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>') },
  { path: '/summary', num: '09', label: '总结与评价', icon: createIcon('<path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/>') },
  { path: '/comparison', num: '10', label: '三方对比', icon: createIcon('<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>') },
]
</script>
