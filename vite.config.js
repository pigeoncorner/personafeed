import { defineConfig } from 'vite'

export default defineConfig({
  root: 'frontend',
  build: {
    outDir: '../dist',
    emptyOutDir: true,
  },
  server: {
    // В локальной разработке проксирует API-запросы к локальному uvicorn.
    // Для использования прод-API вместо этого создай frontend/.env.local
    // с VITE_API_BASE=https://api.stumblefeed.me
    proxy: {
      '/categories': 'http://localhost:8002',
      '/grid': 'http://localhost:8002',
      '/health': 'http://localhost:8002',
    },
  },
})
