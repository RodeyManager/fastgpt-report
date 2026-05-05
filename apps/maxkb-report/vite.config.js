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
  base: '/fastgpt-report/maxkb-report/',
  optimizeDeps: {
    include: ['echarts']
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})
