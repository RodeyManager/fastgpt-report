import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import KnowledgeProcessDemo from '../src/views/KnowledgeProcessDemo.vue'

function createWrapper() {
  return mount(KnowledgeProcessDemo, {
    global: {
      stubs: {
        'router-link': { template: '<a><slot /></a>' }
      }
    }
  })
}

function createFile(name, type = 'application/pdf', content = 'fake') {
  return new File([content], name, { type })
}

function findEngineSelect(wrapper) {
  return wrapper.findAll('select').find(s => {
    const options = s.findAll('option')
    return options.some(o => o.text() === 'FastGPT 默认')
  })
}

describe('KnowledgeProcessDemo', () => {
  it('mounts successfully', () => {
    const wrapper = createWrapper()
    expect(wrapper.find('.demo-page').exists()).toBe(true)
  })

  it('renders engine selector after file upload', async () => {
    const wrapper = createWrapper()
    const file = createFile('test.pdf')
    const fileInput = wrapper.find('input[type="file"]')
    Object.defineProperty(fileInput.element, 'files', {
      value: [file],
      configurable: true
    })
    await fileInput.trigger('change')
    await wrapper.vm.$nextTick()

    const allOptions = wrapper.findAll('select').flatMap(s => s.findAll('option').map(o => o.text()))
    expect(allOptions).toContain('FastGPT 默认')
  })

  it('shows fastgpt and mineru for pdf', async () => {
    const wrapper = createWrapper()
    const file = createFile('test.pdf')
    const fileInput = wrapper.find('input[type="file"]')
    Object.defineProperty(fileInput.element, 'files', {
      value: [file],
      configurable: true
    })
    await fileInput.trigger('change')
    await wrapper.vm.$nextTick()

    const allOptions = wrapper.findAll('select').flatMap(s => s.findAll('option').map(o => o.text()))
    expect(allOptions).toContain('FastGPT 默认')
    expect(allOptions).toContain('MinerU')
  })

  it('shows mineru option for pdf file', async () => {
    const wrapper = createWrapper()
    const file = createFile('test.pdf')

    const fileInput = wrapper.find('input[type="file"]')
    Object.defineProperty(fileInput.element, 'files', {
      value: [file],
      configurable: true
    })
    await fileInput.trigger('change')
    await wrapper.vm.$nextTick()

    const engineSelect = findEngineSelect(wrapper)
    expect(engineSelect).toBeTruthy()
    const options = engineSelect.findAll('option')
    const labels = options.map(o => o.text())
    expect(labels).toContain('MinerU')
  })

  it('hides mineru for csv file', async () => {
    const wrapper = createWrapper()
    const file = createFile('data.csv', 'text/csv')

    const fileInput = wrapper.find('input[type="file"]')
    Object.defineProperty(fileInput.element, 'files', {
      value: [file],
      configurable: true
    })
    await fileInput.trigger('change')
    await wrapper.vm.$nextTick()

    const engineSelect = findEngineSelect(wrapper)
    if (engineSelect) {
      const labels = engineSelect.findAll('option').map(o => o.text())
      expect(labels).not.toContain('MinerU')
    }
  })

  it('compare view not shown when no results', () => {
    const wrapper = createWrapper()
    expect(wrapper.find('.compare-view').exists()).toBe(false)
  })

  it('compare view shown when both engines have results', async () => {
    const wrapper = createWrapper()
    const file = createFile('test.pdf')
    const fileInput = wrapper.find('input[type="file"]')
    Object.defineProperty(fileInput.element, 'files', {
      value: [file],
      configurable: true
    })
    await fileInput.trigger('change')
    await wrapper.vm.$nextTick()

    wrapper.vm.engineResults = {
      fastgpt: { raw_text: 'fg', html_preview: '<p>fg</p>', format_text: '', image_list: [], sheet_names: null },
      mineru: { raw_text: 'mu', html_preview: '<p>mu</p>', format_text: '', image_list: [], sheet_names: null }
    }
    wrapper.vm.parsedResult = '<p>test</p>'
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.compare-view').exists()).toBe(true)
    expect(wrapper.findAll('.compare-column').length).toBe(2)
  })

  it('single result shows normal view not compare', async () => {
    const wrapper = createWrapper()
    const file = createFile('test.pdf')
    const fileInput = wrapper.find('input[type="file"]')
    Object.defineProperty(fileInput.element, 'files', {
      value: [file],
      configurable: true
    })
    await fileInput.trigger('change')
    await wrapper.vm.$nextTick()

    wrapper.vm.engineResults = {
      fastgpt: { raw_text: 'r', html_preview: '<p>t</p>', format_text: '', image_list: [], sheet_names: null }
    }
    wrapper.vm.parsedResult = '<p>test</p>'
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.compare-view').exists()).toBe(false)
    expect(wrapper.find('.result-content').exists()).toBe(true)
  })

  it('file change resets engine results', async () => {
    const wrapper = createWrapper()
    wrapper.vm.engineResults = {
      fastgpt: { raw_text: 'result', html_preview: '<p>test</p>', format_text: '', image_list: [], sheet_names: null }
    }
    wrapper.vm.selectedEngine = 'mineru'

    const file = createFile('new.pdf')
    const fileInput = wrapper.find('input[type="file"]')
    Object.defineProperty(fileInput.element, 'files', {
      value: [file],
      configurable: true
    })
    await fileInput.trigger('change')
    await wrapper.vm.$nextTick()

    expect(Object.keys(wrapper.vm.engineResults).length).toBe(0)
    expect(wrapper.vm.selectedEngine).toBe('fastgpt')
  })
})
