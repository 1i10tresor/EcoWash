import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // Backend Flask local
        changeOrigin: true,
        // Pas de réécriture - on garde le préfixe /api
      },
    },
  },
})
