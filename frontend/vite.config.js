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
  assetsInclude: ['**/*.PNG', '**/*.png'],
  server: {
    port: 5173,
    strictPort: false
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})
