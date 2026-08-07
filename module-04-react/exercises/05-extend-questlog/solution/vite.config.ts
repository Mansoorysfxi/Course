import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// See https://vite.dev/config/ and https://tailwindcss.com/docs/installation/using-vite
export default defineConfig({
  plugins: [react(), tailwindcss()],
})
