/**
 * WebSocket Service
 * Manages raw WebSocket connections for chat functionality
 */

type MessageHandler = (data: any) => void
type ErrorHandler = (error: string) => void
type CloseHandler = () => void

export class ChatWebSocket {
  private ws: WebSocket | null = null
  private url: string
  private messageHandlers: MessageHandler[] = []
  private errorHandlers: ErrorHandler[] = []
  private closeHandlers: CloseHandler[] = []
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  constructor(url: string) {
    this.url = url
  }

  /**
   * Connect to WebSocket server
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url)

        this.ws.onopen = () => {
          console.log(`WebSocket connected to ${this.url}`)
          this.reconnectAttempts = 0
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            this.messageHandlers.forEach((handler) => handler(data))
          } catch (err) {
            console.error('Failed to parse WebSocket message:', err)
          }
        }

        this.ws.onerror = (event) => {
          const errorMsg = `WebSocket error: ${event.type}`
          console.error(errorMsg)
          this.errorHandlers.forEach((handler) => handler(errorMsg))
          reject(new Error(errorMsg))
        }

        this.ws.onclose = () => {
          console.log('WebSocket closed')
          this.closeHandlers.forEach((handler) => handler())
          this.attemptReconnect()
        }
      } catch (err) {
        const errorMsg = `Failed to create WebSocket: ${err}`
        reject(new Error(errorMsg))
      }
    })
  }

  /**
   * Send message to server
   */
  send(data: any): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected')
      return
    }
    this.ws.send(JSON.stringify(data))
  }

  /**
   * Register message handler
   */
  onMessage(handler: MessageHandler): () => void {
    this.messageHandlers.push(handler)
    // Return unsubscribe function
    return () => {
      this.messageHandlers = this.messageHandlers.filter((h) => h !== handler)
    }
  }

  /**
   * Register error handler
   */
  onError(handler: ErrorHandler): () => void {
    this.errorHandlers.push(handler)
    return () => {
      this.errorHandlers = this.errorHandlers.filter((h) => h !== handler)
    }
  }

  /**
   * Register close handler
   */
  onClose(handler: CloseHandler): () => void {
    this.closeHandlers.push(handler)
    return () => {
      this.closeHandlers = this.closeHandlers.filter((h) => h !== handler)
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }

  /**
   * Close connection
   */
  close(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
      console.log(
        `Reconnecting... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms`
      )
      setTimeout(() => {
        this.connect().catch(() => {
          // Error already logged in connect()
        })
      }, delay)
    } else {
      console.error('Max reconnection attempts reached')
    }
  }
}

/**
 * Create WebSocket URL for chat
 */
export const createChatWebSocketUrl = (chatId: string): string => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  // Remove protocol from host if present
  const cleanHost = host.replace(/^https?:\/\//, '')
  return `${protocol}//${cleanHost}/chat/ws/${chatId}`
}
