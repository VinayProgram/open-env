/**
 * Application Configuration
 * Centralized environment variables and configuration constants
 * All values are loaded from .env file with fallback defaults
 */

// ============================================================================
// API Configuration
// ============================================================================

/**
 * Base URL for API requests
 * @default 'http://localhost:8000'
 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * API Endpoints
 */
export const API_ENDPOINTS = {
  CHAT_START: '/customer_service/chat/start',
  CHAT_MESSAGES: (chatId: string) => `/chat/${chatId}/messages`,
  SEND_MESSAGE: (chatId: string) => `/chat/${chatId}/messages`,
}

// ============================================================================
// Socket Configuration
// ============================================================================

/**
 * WebSocket server URL
 * @default 'ws://localhost:8000'
 */
export const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'ws://localhost:8000'

/**
 * WebSocket connection path
 * @default '/chat/ws/'
 */
export const SOCKET_PATH = import.meta.env.VITE_SOCKET_PATH || '/chat/ws/'

/**
 * Socket configuration object
 */
export const SOCKET_CONFIG = {
  url: SOCKET_URL,
  path: SOCKET_PATH,
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  reconnectionAttempts: 5,
  transports: ['websocket'],
}

// ============================================================================
// Application Configuration
// ============================================================================

/**
 * Application name
 */
export const APP_NAME = import.meta.env.VITE_APP_NAME || 'PortFlow'

/**
 * Application version
 */
export const APP_VERSION = import.meta.env.VITE_APP_VERSION || '1.0.0'

/**
 * Environment (development, production, staging)
 */
export const ENVIRONMENT = import.meta.env.VITE_ENV || 'development'

/**
 * Is production environment
 */
export const IS_PRODUCTION = ENVIRONMENT === 'production'

/**
 * Is development environment
 */
export const IS_DEVELOPMENT = ENVIRONMENT === 'development'

// ============================================================================
// TanStack Query Configuration
// ============================================================================

/**
 * Number of retries for failed queries
 */
export const QUERY_RETRY_COUNT = parseInt(
  import.meta.env.VITE_QUERY_RETRY_COUNT || '1',
  10
)

/**
 * Stale time for queries in milliseconds (5 minutes default)
 */
export const QUERY_STALE_TIME = parseInt(
  import.meta.env.VITE_QUERY_STALE_TIME || '300000',
  10
)

/**
 * TanStack Query default options
 */
export const QUERY_CONFIG = {
  defaultOptions: {
    queries: {
      retry: QUERY_RETRY_COUNT,
      staleTime: QUERY_STALE_TIME,
    },
  },
}

// ============================================================================
// Timeout Configuration
// ============================================================================

/**
 * Default fetch timeout in milliseconds
 */
export const FETCH_TIMEOUT = 30000 // 30 seconds

/**
 * API request timeout in milliseconds
 */
export const API_TIMEOUT = 30000 // 30 seconds

/**
 * Socket reconnection timeout in milliseconds
 */
export const SOCKET_TIMEOUT = 5000 // 5 seconds

// ============================================================================
// Feature Flags
// ============================================================================

/**
 * Enable debug logging
 */
export const DEBUG = IS_DEVELOPMENT

/**
 * Enable mock API responses (for development/testing)
 */
export const USE_MOCK_API = false

// ============================================================================
// Export all configuration as object for reference
// ============================================================================

export const CONFIG = {
  // API
  API_BASE_URL,
  API_ENDPOINTS,

  // Socket
  SOCKET_URL,
  SOCKET_PATH,
  SOCKET_CONFIG,

  // App
  APP_NAME,
  APP_VERSION,
  ENVIRONMENT,
  IS_PRODUCTION,
  IS_DEVELOPMENT,

  // Query
  QUERY_RETRY_COUNT,
  QUERY_STALE_TIME,
  QUERY_CONFIG,

  // Timeouts
  FETCH_TIMEOUT,
  API_TIMEOUT,
  SOCKET_TIMEOUT,

  // Features
  DEBUG,
  USE_MOCK_API,
}

export default CONFIG
