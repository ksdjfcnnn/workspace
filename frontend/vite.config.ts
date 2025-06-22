import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 12006,
    host: '0.0.0.0',
    cors: true,
    strictPort: true,
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
    allowedHosts: true,
  },
})
