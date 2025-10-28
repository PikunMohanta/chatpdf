import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [react()],
    
    // Development server configuration
    server: {
      port: parseInt(env.VITE_DEV_PORT) || 3000,
      host: env.VITE_DEV_HOST || 'localhost',
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
        },
        '/socket.io': {
          target: env.VITE_WS_URL || 'http://localhost:8000',
          ws: true,
        },
      },
    },

    // Build configuration
    build: {
      // Production optimizations
      rollupOptions: {
        output: {
          // Optimize chunks for better caching and loading
          manualChunks: {
            // Vendor chunks for better caching
            'react-vendor': ['react', 'react-dom', 'react-router-dom'],
            'ui-vendor': ['framer-motion'],
            'pdf-vendor': ['react-pdf', 'pdfjs-dist'],
            'utils-vendor': ['axios'],
          },
          // Optimize asset naming for caching
          assetFileNames: (assetInfo) => {
            const info = assetInfo.name?.split('.') || []
            let extType = info[info.length - 1]
            
            // Keep pdf.worker.min.js at root level without hashing
            if (assetInfo.name === 'pdf.worker.min.js') {
              return '[name][extname]'
            }
            
            if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType)) {
              extType = 'img'
            } else if (/woff|woff2|eot|ttf|otf/i.test(extType)) {
              extType = 'fonts'
            }
            
            return `assets/${extType}/[name]-[hash][extname]`
          },
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
        },
        external: mode === 'production' ? [] : undefined,
      },
      
      // Source maps for production debugging (if enabled)
      sourcemap: env.VITE_ENABLE_DEBUG === 'true',
      
      // Optimize for production
      minify: 'esbuild',
      target: 'es2020',
      
      // Set chunk size warning limit
      chunkSizeWarningLimit: parseInt(env.VITE_CHUNK_SIZE_WARNING) || 600,
      
      // Additional optimizations
      reportCompressedSize: true,
      cssCodeSplit: true,
    },

    // Enable code splitting in development
    optimizeDeps: {
      include: ['react', 'react-dom', 'react-router-dom', 'framer-motion', 'axios'],
      // Exclude problematic dependencies
      exclude: ['fsevents'],
    },

    // Define global constants
    define: {
      __APP_VERSION__: JSON.stringify(env.VITE_APP_VERSION || '1.0.0'),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    },

    // Resolve configuration
    resolve: {
      alias: {
        '@': '/src',
        '@components': '/src/components',
        '@utils': '/src/utils',
        '@styles': '/src/styles',
      },
    },

    // Ensure public assets (especially pdf.worker.min.js) are copied correctly
    publicDir: 'public',

    // CSS configuration
    css: {
      devSourcemap: command === 'serve',
      preprocessorOptions: {
        scss: {
          additionalData: `@import "@/styles/variables.scss";`,
        },
      },
    },

    // Preview server (for production builds)
    preview: {
      port: 4173,
      host: 'localhost',
    },
  }
})
