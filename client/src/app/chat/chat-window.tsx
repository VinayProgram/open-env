import { useEffect, useRef, useState } from 'react'
import { useParams } from '@tanstack/react-router'
import { Button } from '@/components/ui/button'
import { Send, MessageCircle, Loader } from 'lucide-react'
import { ChatWebSocket, createChatWebSocketUrl } from '@/services/websocket'

interface ChatMessage {
  id: string
  sender: 'customer' | 'support'
  message: string
  timestamp: number
}

interface ChatTurnResponse {
  chat_key: string
  customer_message?: {
    id: string
    message: string
    timestamp: number
  }
  assistant_message?: {
    id: string
    message: string
    timestamp: number
  }
}

/**
 * Chat Window Component
 * Real-time chat interface using raw WebSocket
 * Displays messages from both customer and support
 */
function ChatWindowContent() {
  const { chatId } = useParams({ from: '/chat/$chatId' })
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const wsRef = useRef<ChatWebSocket | null>(null)

  /**
   * Handle WebSocket messages
   */
  const handleWebSocketMessage = (data: ChatTurnResponse) => {
    if (data.customer_message) {
      const custMsg: ChatMessage = {
        id: data.customer_message.id,
        sender: 'customer',
        message: data.customer_message.message,
        timestamp: data.customer_message.timestamp,
      }
      setMessages((prev) => [...prev, custMsg])
    }

    if (data.assistant_message) {
      const assistMsg: ChatMessage = {
        id: data.assistant_message.id,
        sender: 'support',
        message: data.assistant_message.message,
        timestamp: data.assistant_message.timestamp,
      }
      setMessages((prev) => [...prev, assistMsg])
    }
  }

  /**
   * Initialize WebSocket connection
   */
  useEffect(() => {
    if (!chatId) return

    setIsConnecting(true)

    const wsUrl = createChatWebSocketUrl(chatId)
    const ws = new ChatWebSocket(wsUrl)

    // Setup message handler
    const unsubscribeMessage = ws.onMessage((data) => {
      handleWebSocketMessage(data)
    })

    
    // Setup close handler
    const unsubscribeClose = ws.onClose(() => {
      setIsConnected(false)
    })

    // Connect
    ws.connect()
      .then(() => {
        setIsConnected(true)
        setIsConnecting(false)
        wsRef.current = ws
      })
      .catch((_err) => {
        setIsConnecting(false)
      })

    // Cleanup on unmount
    return () => {
      unsubscribeMessage()
      unsubscribeClose()
      ws.close()
    }
  }, [chatId])

  /**
   * Auto-scroll to bottom when new messages arrive
   */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  /**
   * Handle message sending
   */
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!inputValue.trim() || !isConnected || !wsRef.current) {
      return
    }

    const messageText = inputValue.trim()
    setInputValue('')
    setIsSending(true)

    try {
      // Create local message object
      const localMessage: ChatMessage = {
        id: `msg_${Date.now()}`,
        sender: 'customer',
        message: messageText,
        timestamp: Date.now(),
      }

      // Add to local messages immediately for optimistic UI
      setMessages((prev) => [...prev, localMessage])

      // Send message via WebSocket
      wsRef.current.send({
        sender: 'customer',
        message: messageText,
      })
    } catch (err) {
      console.error('Failed to send message:', err)
    } finally {
      setIsSending(false)
    }
  }

  return (
    <div className="h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex flex-col">
      {/* Header */}
      <div className="bg-slate-800/50 border-b border-slate-700/50 px-6 py-4 backdrop-blur">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <MessageCircle className="w-6 h-6 text-blue-400" />
            <div>
              <h1 className="text-lg font-bold text-white">Chat Support</h1>
              <p className="text-sm text-slate-400">Chat ID: {chatId}</p>
            </div>
          </div>

          {/* Connection Status */}
          <div className="flex items-center gap-2">
            {isConnecting ? (
              <>
                <Loader className="w-4 h-4 animate-spin text-yellow-400" />
                <span className="text-sm text-yellow-400">Connecting...</span>
              </>
            ) : isConnected ? (
              <>
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-sm text-green-400">Connected</span>
              </>
            ) : (
              <>
                <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                <span className="text-sm text-red-400">Disconnected</span>
              </>
            )}
          </div>
        </div>
      </div>

     

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <MessageCircle className="w-12 h-12 text-slate-600 mb-3" />
            <p className="text-slate-400">No messages yet</p>
            <p className="text-slate-500 text-sm mt-1">Start the conversation</p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.sender === 'customer' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  msg.sender === 'customer'
                    ? 'bg-blue-600 text-white rounded-br-none'
                    : 'bg-slate-700 text-slate-100 rounded-bl-none'
                }`}
              >
                <p className="text-sm">{msg.message}</p>
                <p className="text-xs opacity-70 mt-1">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-slate-800/50 border-t border-slate-700/50 px-6 py-4 backdrop-blur">
        <form onSubmit={handleSendMessage} className="flex gap-3">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message..."
            disabled={!isConnected || isSending}
            className="flex-1 bg-slate-700/50 border border-slate-600/50 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:bg-slate-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <Button
            type="submit"
            disabled={!isConnected || isSending || !inputValue.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed px-6 py-3 rounded-lg flex items-center gap-2 transition-all"
          >
            {isSending ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            <span className="hidden sm:inline">Send</span>
          </Button>
        </form>

        {/* Helper Text */}
        {!isConnected && (
          <p className="text-xs text-slate-400 mt-2">
            ⚠️ Waiting for WebSocket connection...
          </p>
        )}
      </div>
    </div>
  )
}

/**
 * Chat Window - Export directly (no SocketProvider needed)
 */
export default ChatWindowContent
