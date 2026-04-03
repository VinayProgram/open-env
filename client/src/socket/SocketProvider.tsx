import { useCallback, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import type { SocketContextType } from './SocketContext'
import { SocketContext } from './SocketContext'
import { io } from 'socket.io-client'
import type { Socket } from 'socket.io-client'

/**
 * Socket Provider Props
 */
interface SocketProviderProps {
  children: ReactNode
  socketUrl?: string
  socketPath?: string
  autoConnect?: boolean
}

/**
 * SocketProvider Component
 * Manages socket connection and provides it to all child components via Context
 *
 * @example
 * <SocketProvider socketUrl="ws://localhost:8000" socketPath="/chat/ws/">
 *   <App />
 * </SocketProvider>
 */
export const SocketProvider = ({
  children,
  socketUrl = 'ws://localhost:8000',
  socketPath = '/chat/ws/',
  autoConnect = true,
}: SocketProviderProps) => {
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  /**
   * Initialize socket connection
   */
  const initializeSocket = useCallback(() => {
    if (socket?.connected) {
      console.log('Socket already connected')
      return
    }

    try {
      setIsConnecting(true)
      setError(null)

      const newSocket = io(socketUrl, {
        path: socketPath,
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: 5,
        transports: ['websocket'],
      })

      /**
       * Socket event handlers
       */
      newSocket.on('connect', () => {
        console.log('Socket connected:', newSocket.id)
        setIsConnected(true)
        setIsConnecting(false)
        setError(null)
      })

      newSocket.on('disconnect', () => {
        console.log('Socket disconnected')
        setIsConnected(false)
      })

      newSocket.on('error', (socketError: any) => {
        console.error('Socket error:', socketError)
        setError(socketError?.message || 'Connection error')
        setIsConnecting(false)
      })

      newSocket.on('connect_error', (connectionError: any) => {
        console.error('Connection error:', connectionError)
        setError(connectionError?.message || 'Failed to connect')
        setIsConnecting(false)
      })

      setSocket(newSocket)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to initialize socket'
      console.error('Error initializing socket:', errorMessage)
      setError(errorMessage)
      setIsConnecting(false)
    }
  }, [socket, socketUrl, socketPath])

  /**
   * Initialize socket on component mount or when autoConnect changes
   */
  useEffect(() => {
    if (autoConnect && !socket) {
      initializeSocket()
    }

    // Cleanup on unmount
    return () => {
      if (socket?.connected) {
        socket.disconnect()
      }
    }
  }, [autoConnect, socket, initializeSocket])

  /**
   * Context value
   */
  const value: SocketContextType = {
    socket,
    isConnected,
    isConnecting,
    error,
  }

  return <SocketContext.Provider value={value}>{children}</SocketContext.Provider>
}

export default SocketProvider
