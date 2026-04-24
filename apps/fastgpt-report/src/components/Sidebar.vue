<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h1>FastGPT 技术分析</h1>
      <p>知识库管理深度报告 v4.0</p>
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
  { path: '/overview', num: '01', label: '项目概览', icon: createIcon('<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>') },
  { path: '/architecture', num: '02', label: '知识库架构', icon: createIcon('<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>') },
  { path: '/upload', num: '03', label: '文档上传与解析', icon: createIcon('<path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>') },
  { path: '/cleaning', num: '04', label: '数据清洗', icon: createIcon('<path d="M12 3v18"/><path d="M4 7l16 0"/><path d="M4 12l16 0"/><path d="M4 17l16 0"/>') },
  { path: '/chunking', num: '05', label: '文本分块', icon: createIcon('<rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/>') },
  { path: '/image', num: '06', label: '图片索引', icon: createIcon('<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/>') },
  { path: '/embedding', num: '07', label: '文本向量化', icon: createIcon('<circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="8" opacity="0.4"/><circle cx="12" cy="12" r="11" opacity="0.2"/>') },
  { path: '/retrieval', num: '08', label: '检索系统', icon: createIcon('<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>') },
  { path: '/training', num: '09', label: '训练模式与AI模型', icon: createIcon('<path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>') },
  { path: '/summary', num: '10', label: '技术总结', icon: createIcon('<path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/>') },
  { path: '/schemas', num: '11', label: '数据表结构', icon: createIcon('<path d="M3 3h18v18H3z"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M9 3v18"/>') },
  { path: '/dependencies', num: '12', label: '核心依赖包', icon: createIcon('<rect x="2" y="2" width="20" height="20" rx="2"/><path d="M7 7h10"/><path d="M7 12h10"/><path d="M7 17h10"/>') },
  { path: '/architecture-detail', num: '13', label: '项目架构图', icon: createIcon('<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><path d="M10 6.5h4"/><path d="M10 17.5h4"/><path d="M6.5 10v4"/><path d="M17.5 10v4"/>') },
]
</script>
