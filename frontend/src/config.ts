// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const config = {
  apiBaseUrl: API_BASE_URL,
  apiUrl: `${API_BASE_URL}/api`,
  socketUrl: API_BASE_URL,
  
  // Environment
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
  
  // Feature flags
  enableDebugMode: import.meta.env.DEV,
  enableMockData: false,
}

console.log('🔧 Configuration loaded:', {
  environment: config.isProduction ? 'production' : 'development',
  apiBaseUrl: config.apiBaseUrl,
  socketUrl: config.socketUrl,
})

export default config