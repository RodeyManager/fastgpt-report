import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  base: '/fastgpt-report/',
  optimizeDeps: {
    include: ['pdfjs-dist', 'mammoth', 'papaparse', 'xlsx', 'turndown', 'joplin-turndown-plugin-gfm']
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})
