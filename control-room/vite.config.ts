import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const config = {
  plugins: [react()],
  root: '.',
  resolve: {
    alias: {
      '@shared': fileURLToPath(new URL('./src/shared', import.meta.url)),
      '@server': fileURLToPath(new URL('./src/server', import.meta.url)),
      '@client': fileURLToPath(new URL('./src/client', import.meta.url))
    }
  },
  server: {
    host: '127.0.0.1',
    port: 4173,
    proxy: { '/api': 'http://127.0.0.1:4174' }
  },
  build: { outDir: 'dist/client' },
  test: {
    environment: 'jsdom',
    environmentMatchGlobs: [['tests/integration/**', 'node']]
  }
};

export default defineConfig(config);
