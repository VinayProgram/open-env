/**
 * Chat Registration Module Exports
 * Clean centralized exports for chat registration functionality
 */

export { default as RegisterChat } from './register-chat'
export { registerChat, getChatHistory, sendChatMessage } from './chatApi'
export type { RegisterChatPayload, RegisterChatResponse } from './chatApi'
export { useRegisterChat, useChatHistory, useSendMessage } from './useChatApi'
