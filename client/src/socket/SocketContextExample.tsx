import { useState } from 'react'
import { useSocketContext, useSocketEmit, useSocketOn } from '@/socket'
import { Button } from '@/components/ui/button'
import { Send, AlertCircle, CheckCircle, Loader } from 'lucide-react'

/**
 * Example component demonstrating Socket Context usage
 * Shows all the hooks available from the socket context
 */
export default function SocketContextExample() {
  const { isConnected, isConnecting, error: socketError } = useSocketContext()
  const emit = useSocketEmit()

  const [messages, setMessages] = useState<any[]>([])
  const [inputValue, setInputValue] = useState('')
  const [error, setError] = useState('')

  /**
   * Listen for incoming messages
   */
  useSocketOn('message', (data) => {
    setMessages((prev) => [
      ...prev,
      {
        type: 'received',
        content: data,
        timestamp: new Date().toLocaleTimeString(),
      },
    ])
  })

  /**
   * Listen for chat responses
   */
  useSocketOn('chat_response', (data) => {
    setMessages((prev) => [
      ...prev,
      {
        type: 'response',
        content: data,
        timestamp: new Date().toLocaleTimeString(),
      },
    ])
  })

  /**
   * Handle sending a message
   */
  const handleSendMessage = () => {
    if (!inputValue.trim()) {
      setError('Message cannot be empty')
      return
    }

    if (!isConnected) {
      setError('Not connected to server')
      return
    }

    // Emit message through socket
    const success = emit('send_message', {
      message: inputValue,
      timestamp: new Date().toISOString(),
    })

    if (success) {
      // Add to UI
      setMessages((prev) => [
        ...prev,
        {
          type: 'sent',
          content: inputValue,
          timestamp: new Date().toLocaleTimeString(),
        },
      ])
      setInputValue('')
      setError('')
    } else {
      setError('Failed to send message')
    }
  }

  /**
   * Handle sending a complaint
   */
  const handleReportComplaint = () => {
    const success = emit('send_complaint', {
      description: 'Late delivery - 8 hours delayed',
      severity: 'high',
      timestamp: new Date().toISOString(),
    })

    if (success) {
      setMessages((prev) => [
        ...prev,
        {
          type: 'sent',
          content: 'Complaint reported: Late delivery',
          timestamp: new Date().toLocaleTimeString(),
        },
      ])
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="space-y-6">
      {/* Connection Status Card */}
      <div
        className={`rounded-lg border p-4 ${
          isConnected
            ? 'border-green-500/50 bg-green-500/10'
            : 'border-red-500/50 bg-red-500/10'
        }`}
      >
        <div className="flex items-center gap-3">
          {isConnecting ? (
            <Loader className="w-5 h-5 text-yellow-400 animate-spin" />
          ) : isConnected ? (
            <CheckCircle className="w-5 h-5 text-green-400" />
          ) : (
            <AlertCircle className="w-5 h-5 text-red-400" />
          )}
          <div>
            <p className={isConnected ? 'text-green-400 font-semibold' : 'text-red-400 font-semibold'}>
              {isConnecting
                ? 'Connecting to server...'
                : isConnected
                ? 'Connected to server'
                : 'Disconnected'}
            </p>
            {socketError && <p className="text-red-400 text-sm">{socketError}</p>}
          </div>
        </div>
      </div>

      {/* Messages Display */}
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 h-80 overflow-y-auto space-y-3">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-slate-400 text-center">
            <div>
              <p className="text-sm mb-2">No messages yet</p>
              <p className="text-xs">Start by sending a message or reporting a complaint</p>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-lg text-sm ${
                msg.type === 'sent'
                  ? 'bg-blue-500/20 border border-blue-500/50 ml-8'
                  : msg.type === 'response'
                  ? 'bg-purple-500/20 border border-purple-500/50 mr-8'
                  : 'bg-slate-700/50 border border-slate-600'
              }`}
            >
              <div className="flex justify-between items-start mb-1">
                <span className="font-semibold text-white">
                  {msg.type === 'sent' && '📤 You'}
                  {msg.type === 'received' && '📥 Server'}
                  {msg.type === 'response' && '🤖 AI'}
                </span>
                <span className="text-xs text-slate-400">{msg.timestamp}</span>
              </div>
              <p className="text-slate-200 break-words">
                {typeof msg.content === 'string'
                  ? msg.content
                  : JSON.stringify(msg.content, null, 2)}
              </p>
            </div>
          ))
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {/* Input Area */}
      <div className="space-y-3">
        <div className="flex gap-3">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a message..."
            disabled={!isConnected}
            className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 disabled:opacity-50 text-sm"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!isConnected}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            Send
          </Button>
        </div>

        <Button
          onClick={handleReportComplaint}
          disabled={!isConnected}
          variant="outline"
          className="w-full border-slate-600 text-white hover:bg-slate-700 disabled:opacity-50"
        >
          📋 Report Complaint
        </Button>
      </div>

      {/* Code Example */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
        <h4 className="text-white font-semibold mb-3 text-sm">Usage Example</h4>
        <pre className="bg-slate-900 p-3 rounded text-xs text-slate-300 overflow-auto">
{`import { 
  useSocketContext, 
  useSocketEmit, 
  useSocketOn 
} from '@/socket'

// In your component:
const { isConnected } = useSocketContext()
const emit = useSocketEmit()

// Listen to events
useSocketOn('message', (data) => {
  console.log('Received:', data)
})

// Send events
emit('send_message', { text: 'Hello' })`}
        </pre>
      </div>
    </div>
  )
}
