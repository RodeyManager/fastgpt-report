import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/overview' },
  { path: '/overview', name: 'overview', component: () => import('@/views/Section1Overview.vue'), meta: { title: '项目架构概览' } },
  { path: '/knowledge', name: 'knowledge', component: () => import('@/views/Section2Knowledge.vue'), meta: { title: '知识库管理' } },
  { path: '/upload', name: 'upload', component: () => import('@/views/Section3Upload.vue'), meta: { title: '文档上传' } },
  { path: '/deepdoc', name: 'deepdoc', component: () => import('@/views/Section4DeepDoc.vue'), meta: { title: '文档解析 DeepDoc' } },
  { path: '/cleaning', name: 'cleaning', component: () => import('@/views/Section5Cleaning.vue'), meta: { title: '数据清洗' } },
  { path: '/chunking', name: 'chunking', component: () => import('@/views/Section6Chunking.vue'), meta: { title: '文本分块' } },
  { path: '/embedding', name: 'embedding', component: () => import('@/views/Section7Embedding.vue'), meta: { title: '向量化' } },
  { path: '/retrieval', name: 'retrieval', component: () => import('@/views/Section8Retrieval.vue'), meta: { title: '检索' } },
  { path: '/summary', name: 'summary', component: () => import('@/views/Section9Summary.vue'), meta: { title: '总结与评价' } },
  { path: '/comparison', name: 'comparison', component: () => import('@/views/Section10Comparison.vue'), meta: { title: '三方对比' } },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior() { return { top: 0 } }
})

export default router
export { routes }
