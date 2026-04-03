import { useEffect, useCallback } from 'react'
import { useSocketContext } from './SocketContext'

/**
 * Hook for emitting socket events
 * Provides type-safe event emission
 *
 * @returns Function to emit events
 *
 * @example
 * const emit = useSocketEmit()
 * emit('send_message', { text: 'Hello' })
 */
export const useSocketEmit = () => {
  const { socket, isConnected } = useSocketContext()

  const emit = useCallback(
    (event: string, data?: any, callback?: (response: any) => void) => {
      if (!isConnected || !socket) {
        console.warn('Socket not connected. Cannot emit:', event)
        return false
      }

      try {
        if (callback) {
          socket.emit(event, data, callback)
        } else {
          socket.emit(event, data)
        }
        return true
      } catch (error) {
        console.error('Error emitting event:', event, error)
        return false
      }
    },
    [socket, isConnected]
  )

  return emit
}

/**
 * Hook for listening to socket events
 * Automatically handles cleanup
 *
 * @param event - Event name to listen for
 * @param handler - Callback function when event is received
 * @param deps - Dependency array
 *
 * @example
 * useSocketOn('message', (data) => {
 *   console.log('Received message:', data)
 * })
 */
export const useSocketOn = (
  event: string,
  handler: (data: any) => void,
  deps: any[] = []
) => {
  const { socket } = useSocketContext()

  useEffect(() => {
    if (!socket) return

    // Add event listener
    socket.on(event, handler)

    // Cleanup listener on unmount or dependency change
    return () => {
      socket.off(event, handler)
    }
  }, [socket, event, handler, ...deps])
}

/**
 * Hook for listening to socket events once
 * Automatically removes listener after first event
 *
 * @param event - Event name to listen for
 * @param handler - Callback function when event is received
 *
 * @example
 * useSocketOnce('connected', (data) => {
 *   console.log('Connected once:', data)
 * })
 */
export const useSocketOnce = (event: string, handler: (data: any) => void) => {
  const { socket } = useSocketContext()

  useEffect(() => {
    if (!socket) return

    // Add one-time event listener
    socket.once(event, handler)

    // Cleanup
    return () => {
      socket.off(event, handler)
    }
  }, [socket, event, handler])
}

/**
 * Hook to manually remove socket event listeners
 * Useful for complex event management
 *
 * @returns Function to remove listeners
 *
 * @example
 * const offEvent = useSocketOff()
 * offEvent('message')
 */
export const useSocketOff = () => {
  const { socket } = useSocketContext()

  const off = useCallback(
    (event: string, handler?: (data: any) => void) => {
      if (!socket) return

      if (handler) {
        socket.off(event, handler)
      } else {
        socket.off(event)
      }
    },
    [socket]
  )

  return off
}

/**
 * Hook for request-response pattern
 * Emit event and wait for response
 *
 * @returns Function for request-response
 *
 * @example
 * const request = useSocketRequest()
 * const response = await request('get_complaints', { page: 1 })
 */
export const useSocketRequest = () => {
  const emit = useSocketEmit()
  const { socket } = useSocketContext()

  const request = useCallback(
    (event: string, data?: any, timeout = 5000): Promise<any> => {
      return new Promise((resolve, reject) => {
        if (!socket) {
          reject(new Error('Socket not initialized'))
          return
        }

        const timeoutId = setTimeout(() => {
          reject(new Error(`Request timeout: ${event}`))
        }, timeout)

        socket.emit(event, data, (response: any) => {
          clearTimeout(timeoutId)
          resolve(response)
        })
      })
    },
    [socket, emit]
  )

  return request
}

export default {
  useSocketEmit,
  useSocketOn,
  useSocketOnce,
  useSocketOff,
  useSocketRequest,
}
