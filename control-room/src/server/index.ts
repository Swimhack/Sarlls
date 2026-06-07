import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import express from 'express';
import { createApi } from './api';

const api = createApi();
const port = Number(process.env.CONTROL_ROOM_PORT ?? '4174');

// In production, serve the built client
const clientDir = resolve(import.meta.dirname, '../../dist/client');
if (existsSync(clientDir)) {
  api.use(express.static(clientDir, { index: false }));
  // SPA fallback — only for non-API paths
  api.use((req, res, next) => {
    if (req.method !== 'GET' || req.path.startsWith('/api')) {
      next();
      return;
    }
    res.sendFile(resolve(clientDir, 'index.html'));
  });
}

const host = process.env.CONTROL_ROOM_HOST ?? '127.0.0.1';
api.listen(port, host, () => {
  console.log(`SafeSwitch Control Room API: http://${host}:${port}`);
});
