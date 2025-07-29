import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true,
  },
  build: {
    // Enable CSS code splitting
    cssCodeSplit: true,
    
    // Increase chunk size warning limit to 1MB
    chunkSizeWarningLimit: 1000,
    
    // Rollup options for advanced optimizations
    rollupOptions: {
      output: {
        // Manual chunk splitting for better caching
        manualChunks: {
          // React and related core libraries
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          
          // Charting libraries
          'charts-vendor': ['recharts'],
          
          // Payment processing
          'stripe-vendor': ['@stripe/react-stripe-js', '@stripe/stripe-js'],
          
          // Animation libraries
          'animation-vendor': ['framer-motion'],
          
          // Utility libraries
          'utils-vendor': ['axios', 'date-fns'],
          
          // UI libraries
          'ui-vendor': ['lucide-react', 'react-toastify'],
        },
      },
    },
    
    // Terser minification options
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info', 'console.debug', 'console.warn'],
      },
      mangle: {
        safari10: true,
      },
      format: {
        comments: false,
      },
    },
    
    // Generate source maps for production debugging (optional)
    sourcemap: false,
    
    // Target modern browsers for smaller bundles
    target: 'es2015',
  },
  
  // Resolve aliases
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
})