import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,          // listen on 0.0.0.0 so Docker exposes it
    port: 3000,          // match docker-compose.yml
    strictPort: true,    // fail if port 3000 is taken
    watch: {
      usePolling: true   // needed sometimes inside Docker
    }
  }
})
