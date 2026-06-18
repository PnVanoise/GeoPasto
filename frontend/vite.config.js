import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import { fileURLToPath, URL } from 'node:url'


export default defineConfig({
  plugins: [
    vue(),
    vuetify({ autoImport: true }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build: {
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return
          if (id.includes('vuetify')) return 'vendor-vuetify'
          if (id.includes('/ol/') || id.includes('ol-layerswitcher')) return 'vendor-ol'
          if (id.includes('vue-router') || id.includes('pinia')) return 'vendor-vue'
          if (id.includes('/vue/') || id.includes('/vue-demi/') || id.includes('/@vue/')) return 'vendor-vue'
        },
      },
    },
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/admin': 'http://localhost:8000',
    },
    allowedHosts: ['localhost', 'pastoralisme.vanoise-parcnational.fr']
  },
  preview: {
    allowedHosts: ['localhost', 'pastoralisme.vanoise-parcnational.fr']
  },
})
