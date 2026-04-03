import { createContext, useContext } from 'react'
import { Socket } from 'socket.io-client'

export interface SocketContextType {
  socket: Socket | null
  isConnected: boolean
  isConnecting: boolean
  error: string | null
}


export const SocketContext = createContext<SocketContextType | undefined>(undefined)


export const useSocketContext = (): SocketContextType => {
  const context = useContext(SocketContext)

  if (!context) {
    throw new Error(
      'useSocketContext must be used within a SocketProvider. ' +
      'Wrap your app with <SocketProvider>...</SocketProvider>'
    )
  }

  return context
}
