import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/overview' },
  { path: '/overview', name: 'overview', component: () => import('@/views/Section1Overview.vue'), meta: { title: '项目架构概览' } },
  { path: '/knowledge', name: 'knowledge', component: () => import('@/views/Section2Knowledge.vue'), meta: { title: '知识管理能力' } },
  { path: '/upload', name: 'upload', component: () => import('@/views/Section3Upload.vue'), meta: { title: '文档上传机制' } },
  { path: '/parsing', name: 'parsing', component: () => import('@/views/Section4Parsing.vue'), meta: { title: '文档解析能力' } },
  { path: '/cleaning', name: 'cleaning', component: () => import('@/views/Section5Cleaning.vue'), meta: { title: '数据清洗能力' } },
  { path: '/chunking', name: 'chunking', component: () => import('@/views/Section6Chunking.vue'), meta: { title: '文本分块策略' } },
  { path: '/embedding', name: 'embedding', component: () => import('@/views/Section7Embedding.vue'), meta: { title: '向量化能力' } },
  { path: '/retrieval', name: 'retrieval', component: () => import('@/views/Section8Retrieval.vue'), meta: { title: '检索能力' } },
  { path: '/e2e-flow', name: 'e2e-flow', component: () => import('@/views/Section9E2EFlow.vue'), meta: { title: 'RAG端到端流程' } },
  { path: '/summary', name: 'summary', component: () => import('@/views/Section10Summary.vue'), meta: { title: '优势与不足总结' } },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior() { return { top: 0 } }
})

export default router
export { routes }
