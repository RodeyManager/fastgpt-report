import { mount } from '@vue/test-utils'

// Mock ECharts 避免 jsdom 环境中 canvas 报错
const echartsMock = {
  init: vi.fn(() => ({ setOption: vi.fn(), resize: vi.fn(), dispose: vi.fn() })),
  graphic: { LinearGradient: class {}, RadialGradient: class {} }
}
vi.mock('echarts', () => ({ ...echartsMock, default: echartsMock }))

describe('Section2 Component', () => {
  it('挂载成功并包含 section-page 和 h2', async () => {
    const Section2 = (await import('@/views/Section2Knowledge.vue')).default
    const wrapper = mount(Section2)
    expect(wrapper.find('.section-page').exists()).toBe(true)
    expect(wrapper.find('h2').exists()).toBe(true)
  })
})
