import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  server: {
    fs: {
      allow: [path.resolve(__dirname, '..')],
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: path.resolve(__dirname, '../tests/config/setup.ts'),
    coverage: {
      reporter: ['text', 'json', 'html'],
      reportsDirectory: path.resolve(__dirname, '../tests/reports/coverage'),
      exclude: [
        'node_modules/',
        'dist/',
        '*.config.js',
        '**/*.d.ts',
        'tests/',
        '**/*.test.ts',
        '**/*.spec.ts',
      ],
    },
    outputFile: path.resolve(__dirname, '../tests/reports/vitest-results.json'),
  },
  resolve: {
    alias: {
      '@testing-library/jest-dom': path.resolve(__dirname, './node_modules/@testing-library/jest-dom/dist/index.mjs'),
      '@': path.resolve(__dirname, './src'),
    },
  },
});
