import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// VULNERABILITY: Exposed source maps in production
export default defineConfig({
    plugins: [react()],
    server: {
        host: '0.0.0.0',
        port: 3000
    },
    build: {
        sourcemap: true  // VULNERABLE: Source maps expose code
    }
})
