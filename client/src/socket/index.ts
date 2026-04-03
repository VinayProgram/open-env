/**
 * Socket Module - Centralized exports
 * Import all socket-related utilities from this file
 *
 * @example
 * import { SocketProvider, useSocketContext, useSocketEmit } from '@/socket'
 */

export { SocketProvider } from './SocketProvider'
export { SocketContext, useSocketContext, type SocketContextType } from './SocketContext'
export {
  useSocketEmit,
  useSocketOn,
  useSocketOnce,
  useSocketOff,
  useSocketRequest,
} from './useSocket'
