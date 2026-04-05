import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  root: '.',
  build: {
    outDir: '../static/frontend',
    emptyOutDir: true,
    rollupOptions: {
      input: './index.html'
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
      '/accounts': 'http://localhost:8000',
      '/dashboard': 'http://localhost:8000',
      '/admin': 'http://localhost:8000',
    }
  }
})