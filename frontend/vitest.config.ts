import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: '../tests/config/setup.ts',
    coverage: {
      reporter: ['text', 'json', 'html'],
      reportsDirectory: '../tests/reports/coverage',
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
    outputFile: '../tests/reports/vitest-results.json',
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});