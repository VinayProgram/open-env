
import { API_BASE_URL } from '@/config/constants'

export interface RegisterChatPayload {
  customer_name: string
  chat_key: string
}

export interface RegisterChatResponse {
  chat_id?: string
  status: string
  message?: string
  [key: string]: any
}


export const registerChat = async (
  payload: RegisterChatPayload
): Promise<RegisterChatResponse> => {
  const response = await fetch(`${API_BASE_URL}/customer-chat/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(
      errorData?.message || `Failed to register chat: ${response.statusText}`
    )
  }

  return response.json()
}

/**
 * Get chat history for a specific chat session
 *
 * @param chatId - The chat session ID
 * @returns Promise with chat messages
 */
export const getChatHistory = async (chatId: string) => {
  const response = await fetch(`${API_BASE_URL}/chat/${chatId}/messages`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch chat history: ${response.statusText}`)
  }

  return response.json()
}

/**
 * Send a message to the chat
 *
 * @param chatId - The chat session ID
 * @param message - The message content
 * @returns Promise with server response
 */
export const sendChatMessage = async (chatId: string, message: string) => {
  const response = await fetch(`${API_BASE_URL}/chat/${chatId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  })

  if (!response.ok) {
    throw new Error(`Failed to send message: ${response.statusText}`)
  }

  return response.json()
}

export default {
  registerChat,
  getChatHistory,
  sendChatMessage,
}
