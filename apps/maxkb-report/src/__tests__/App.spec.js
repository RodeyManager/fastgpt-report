import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'

// 创建测试用 mock 路由
const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', redirect: '/overview' },
    { path: '/overview', component: { template: '<div>Overview</div>' } }
  ]
})

describe('App.vue', () => {
  it('成功挂载组件', async () => {
    router.push('/overview')
    await router.isReady()

    // 动态导入避免循环依赖
    const App = (await import('@/App.vue')).default
    const wrapper = mount(App, {
      global: {
        plugins: [router]
      }
    })

    expect(wrapper.find('.app-layout').exists()).toBe(true)
  })
})
