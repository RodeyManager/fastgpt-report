import { createRouter, createWebHashHistory } from 'vue-router'
import KnowledgeProcessDemo from '../views/KnowledgeProcessDemo.vue'

const routes = [
  {
    path: '/',
    name: 'demo',
    component: KnowledgeProcessDemo
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
