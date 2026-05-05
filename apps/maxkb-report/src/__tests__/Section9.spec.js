import { mount } from '@vue/test-utils'

// Mock ECharts 避免 jsdom 环境中 canvas 报错
const echartsMock = {
  init: vi.fn(() => ({ setOption: vi.fn(), resize: vi.fn(), dispose: vi.fn() })),
  graphic: { LinearGradient: class {}, RadialGradient: class {} }
}
vi.mock('echarts', () => ({ ...echartsMock, default: echartsMock }))

describe('Section9 Component', () => {
  it('挂载成功并包含 section-page 和 h2', async () => {
    const Section9 = (await import('@/views/Section9E2EFlow.vue')).default
    const wrapper = mount(Section9)
    expect(wrapper.find('.section-page').exists()).toBe(true)
    expect(wrapper.find('h2').exists()).toBe(true)
  })
})
