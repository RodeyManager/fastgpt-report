import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/overview' },
  { path: '/overview', name: 'overview', component: () => import('@/views/Section1Overview.vue'), meta: { title: '项目概览' } },
  { path: '/architecture', name: 'architecture', component: () => import('@/views/Section2Architecture.vue'), meta: { title: '知识库架构' } },
  { path: '/upload', name: 'upload', component: () => import('@/views/Section3Upload.vue'), meta: { title: '文档上传与解析' } },
  { path: '/cleaning', name: 'cleaning', component: () => import('@/views/Section4Cleaning.vue'), meta: { title: '数据清洗' } },
  { path: '/chunking', name: 'chunking', component: () => import('@/views/Section5Chunking.vue'), meta: { title: '文本分块' } },
  { path: '/image', name: 'image', component: () => import('@/views/Section6Image.vue'), meta: { title: '图片索引' } },
  { path: '/embedding', name: 'embedding', component: () => import('@/views/Section7Embedding.vue'), meta: { title: '文本向量化' } },
  { path: '/retrieval', name: 'retrieval', component: () => import('@/views/Section8Retrieval.vue'), meta: { title: '检索系统' } },
  { path: '/training', name: 'training', component: () => import('@/views/Section9Training.vue'), meta: { title: '训练模式与AI模型' } },
  { path: '/summary', name: 'summary', component: () => import('@/views/Section10Summary.vue'), meta: { title: '技术总结' } },
  { path: '/schemas', name: 'schemas', component: () => import('@/views/Section11Schemas.vue'), meta: { title: '数据表结构' } },
  { path: '/dependencies', name: 'dependencies', component: () => import('@/views/Section12Dependencies.vue'), meta: { title: '核心依赖包' } },
  { path: '/architecture-detail', name: 'architecture-detail', component: () => import('@/views/Section13ArchitectureDetail.vue'), meta: { title: '项目架构图' } },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior() { return { top: 0 } }
})

export default router
export { routes }
