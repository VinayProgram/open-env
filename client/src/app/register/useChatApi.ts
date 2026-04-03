/**
 * Custom React Query Hooks for Chat Registration
 * Handles data fetching, caching, and state management
 */

import { useMutation, useQuery } from '@tanstack/react-query'
import { registerChat, getChatHistory, sendChatMessage } from './chatApi'
import type { RegisterChatPayload } from './chatApi'

/**
 * Hook for registering a new chat session
 * Automatically handles loading, error, and success states
 *
 * @returns Mutation object with mutate function and status
 *
 * @example
 * const { mutate, isPending, isError, data } = useRegisterChat()
 *
 * const handleRegister = async () => {
 *   mutate({
 *     customer_name: 'Sakshi',
 *     chat_key: '0707'
 *   })
 * }
 */
export const useRegisterChat = () => {
  return useMutation({
    mutationFn: (payload: RegisterChatPayload) => registerChat(payload),
    onSuccess: (data) => {
      console.log('Chat registered successfully:', data)
    },
    onError: (error: Error) => {
      console.error('Failed to register chat:', error.message)
    },
  })
}

/**
 * Hook for fetching chat history
 * Only fetches when enabled
 *
 * @param chatId - The chat session ID
 * @param enabled - Whether to enable the query
 * @returns Query object with data and status
 *
 * @example
 * const { data, isLoading, error } = useChatHistory(chatId, !!chatId)
 */
export const useChatHistory = (chatId: string | null, enabled = false) => {
  return useQuery({
    queryKey: ['chatHistory', chatId],
    queryFn: () => getChatHistory(chatId!),
    enabled: enabled && !!chatId,
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

/**
 * Hook for sending a message in a chat
 *
 * @param chatId - The chat session ID
 * @returns Mutation object with mutate function
 *
 * @example
 * const { mutate } = useSendMessage(chatId)
 * mutate('Hello, this is my message')
 */
export const useSendMessage = (chatId: string | null) => {
  return useMutation({
    mutationFn: (message: string) => sendChatMessage(chatId!, message),
    onSuccess: (data) => {
      console.log('Message sent:', data)
    },
    onError: (error: Error) => {
      console.error('Failed to send message:', error.message)
    },
  })
}

export default {
  useRegisterChat,
  useChatHistory,
  useSendMessage,
}
