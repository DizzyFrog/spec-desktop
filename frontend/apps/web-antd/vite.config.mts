import { defineConfig } from '@vben/vite-config';

export default defineConfig(async () => {
  return {
    application: {},
    vite: {
      server: {
        proxy: {
          '/api': {
            changeOrigin: true,
            rewrite: (path) => path,
            // 后端API地址
            target: 'http://localhost:8000',
            ws: true,
          },
        },
      },
    },
  };
});
