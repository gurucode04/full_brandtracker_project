// API configuration
const getApiBase = () => {
  // Always use relative path - works for both Vite dev server (with proxy) and Django
  // When running on Vite (5173), the proxy in vite.config.js forwards /api to Django
  // When running on Django (8000), /api is served directly
  return '/api'
}

const getWsUrl = () => {
  const host = window.location.hostname
  const port = window.location.port || (window.location.protocol === 'https:' ? '443' : '80')
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  
  // Always use same origin for WebSocket
  return `${proto}://${host}:${port}/ws`
}

export const API_BASE = getApiBase()
export const WS_BASE = getWsUrl()

