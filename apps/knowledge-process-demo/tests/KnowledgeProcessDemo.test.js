import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
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

  // --- Markdown Tool Selector Tests ---
  it('selectedMdTools defaults to markitdown', () => {
    const wrapper = createWrapper()
    expect(wrapper.vm.selectedMdTools).toEqual(['markitdown'])
  })

  it('shows tool selector with two checkboxes in step 1', async () => {
    const wrapper = createWrapper()
    wrapper.vm.uploadedFile = createFile('test.pdf')
    wrapper.vm.activeStep = 1
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()

    const toolSection = wrapper.find('[data-testid="md-tool-selector"]')
    expect(toolSection.exists()).toBe(true)
    const toolCheckboxes = toolSection.findAll('input[type="checkbox"]')
    expect(toolCheckboxes.length).toBe(2)
  })

  it('can toggle markdownify tool on', async () => {
    const wrapper = createWrapper()
    wrapper.vm.toggleMdTool('markdownify')
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.selectedMdTools).toEqual(['markitdown', 'markdownify'])
  })

  it('cannot uncheck last tool', async () => {
    const wrapper = createWrapper()
    expect(wrapper.vm.selectedMdTools).toEqual(['markitdown'])
    wrapper.vm.toggleMdTool('markitdown')
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.selectedMdTools.length).toBeGreaterThanOrEqual(1)
    expect(wrapper.vm.selectedMdTools).toEqual(['markitdown'])
  })

  it('cannot select more than 2 tools', async () => {
    const wrapper = createWrapper()
    wrapper.vm.toggleMdTool('markdownify')
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.selectedMdTools.length).toBe(2)
  })

  // --- convertResults & side-by-side tests ---
  it('convertResults defaults to empty array', () => {
    const wrapper = createWrapper()
    expect(wrapper.vm.convertResults).toEqual([])
  })

  it('runMarkdownConvert passes tools in request body', async () => {
    const wrapper = createWrapper()
    wrapper.vm.rawText = '<h1>Hi</h1>'
    wrapper.vm.formatText = ''
    wrapper.vm.fileInfo = { ext: 'html' }
    wrapper.vm.selectedMdTools = ['markitdown', 'markdownify']

    const fetchMock = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          results: [
            { tool: 'markitdown', markdown: '# Hi\n', note: 'ok', duration_ms: 8.0 },
            { tool: 'markdownify', markdown: '# Hi', note: 'ok', duration_ms: 5.0 },
          ]
        })
      })
    )
    vi.stubGlobal('fetch', fetchMock)

    await wrapper.vm.runMarkdownConvert()
    const body = JSON.parse(fetchMock.mock.calls[0][1].body)
    expect(body.tools).toEqual(['markitdown', 'markdownify'])
    expect(wrapper.vm.convertResults.length).toBe(2)
    expect(wrapper.vm.markdownText).toBe('# Hi\n')

    vi.restoreAllMocks()
  })

  it('markdownText is set to first result for cleaning compat', async () => {
    const wrapper = createWrapper()
    wrapper.vm.rawText = '<h1>Hi</h1>'
    wrapper.vm.formatText = ''
    wrapper.vm.fileInfo = { ext: 'html' }

    const fetchMock = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          results: [
            { tool: 'markitdown', markdown: '# Result2', note: 'ok', duration_ms: 8.0 },
            { tool: 'markdownify', markdown: '# Result1', note: 'ok', duration_ms: 5.0 },
          ]
        })
      })
    )
    vi.stubGlobal('fetch', fetchMock)

    await wrapper.vm.runMarkdownConvert()
    expect(wrapper.vm.markdownText).toBe('# Result2')
    expect(wrapper.vm.convertResults.length).toBe(2)

    vi.restoreAllMocks()
  })

  it('shows side-by-side grid when 2 results', async () => {
    const wrapper = createWrapper()
    wrapper.vm.uploadedFile = createFile('test.docx')
    wrapper.vm.activeStep = 1
    wrapper.vm.rawText = '<h1>Hi</h1>'
    wrapper.vm.convertResults = [
      { tool: 'markitdown', markdown: '# B', note: '', duration_ms: 8.0 },
      { tool: 'markdownify', markdown: '# A', note: '', duration_ms: 5.0 },
    ]
    wrapper.vm.markdownText = '# B'
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()

    const html = wrapper.find('.demo-result-panel').html()
    expect(html).toContain('grid-template-columns')
    expect(html).toContain('Markdownify')
    expect(html).toContain('MarkItDown')
  })

  it('shows single result view when 1 result', async () => {
    const wrapper = createWrapper()
    wrapper.vm.uploadedFile = createFile('test.docx')
    wrapper.vm.activeStep = 1
    wrapper.vm.rawText = '<h1>Hi</h1>'
    wrapper.vm.convertResults = [
      { tool: 'markdownify', markdown: '# A', note: 'ok', duration_ms: 5.0 },
    ]
    wrapper.vm.markdownText = '# A'
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()

    const html = wrapper.find('.demo-result-panel').html()
    expect(html).not.toContain('grid-template-columns')
    expect(wrapper.text()).toContain('Markdown 转换结果')
  })
})
