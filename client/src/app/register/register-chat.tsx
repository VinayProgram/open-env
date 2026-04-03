import { useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { useRegisterChat } from './useChatApi'
import { Button } from '@/components/ui/button'
import { Phone, User, AlertCircle, CheckCircle, Loader } from 'lucide-react'

/**
 * Register Chat Component
 * Clean UI form for registering a new chat session
 * Collects customer name and phone number
 */
export default function RegisterChat() {
  const [customerName, setCustomerName] = useState('')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const navigate = useNavigate()

  const { mutate, isPending, isError, error, data } = useRegisterChat()

  /**
   * Handle form submission
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Validation
    if (!customerName.trim()) {
      return
    }

    if (!phoneNumber.trim()) {
      return
    }

    // Call API
    mutate(
      {
        customer_name: customerName.trim(),
        chat_key: crypto.randomUUID(),
      },
      {
        onSuccess: (response) => {
          setSuccessMessage(response.message || 'Chat registered successfully!')
          setCustomerName('')
          setPhoneNumber('')
          
          // Navigate to chat window after 1 second
          if (response.chat_key) {
            setTimeout(() => {
              navigate({ to: `/chat/${response.chat_key}` })
            }, 1000)
          } else {
            // Clear success message after 3 seconds if no chat_id
            setTimeout(() => {
              setSuccessMessage('')
            }, 3000)
          }
        },
      }
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Start a Chat</h1>
          <p className="text-slate-400">Register to begin speaking with our support team</p>
        </div>

        {/* Form Card */}
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-8 backdrop-blur">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Name Input */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-slate-300 mb-2">
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  id="name"
                  type="text"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  placeholder="e.g., Sakshi Kumar"
                  disabled={isPending}
                  className="w-full bg-slate-700/50 border border-slate-600/50 rounded-lg pl-10 pr-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:bg-slate-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                />
              </div>
            </div>

            {/* Phone Number Input */}
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-slate-300 mb-2">
                Phone Number
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  id="phone"
                  type="tel"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  placeholder="e.g., +91 98765 43210"
                  disabled={isPending}
                  className="w-full bg-slate-700/50 border border-slate-600/50 rounded-lg pl-10 pr-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:bg-slate-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                />
              </div>
            </div>

            {/* Error Message */}
            {isError && (
              <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-red-400 font-medium text-sm">Registration Failed</p>
                  <p className="text-red-300 text-xs mt-1">
                    {error instanceof Error ? error.message : 'An error occurred'}
                  </p>
                </div>
              </div>
            )}

            {/* Success Message */}
            {successMessage && (
              <div className="bg-green-500/10 border border-green-500/50 rounded-lg p-4 flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-green-400 font-medium text-sm">Success</p>
                  <p className="text-green-300 text-xs mt-1">{successMessage}</p>
                  {data?.chat_id && (
                    <p className="text-green-300 text-xs mt-2">
                      Chat ID: <code className="bg-green-900/30 px-2 py-1 rounded">{data.chat_id}</code>
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Submit Button */}
            <Button
              type="submit"
              disabled={isPending || !customerName.trim() || !phoneNumber.trim()}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold py-3 rounded-lg flex items-center justify-center gap-2 transition-all"
            >
              {isPending ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Registering...
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4" />
                  Register Chat
                </>
              )}
            </Button>
          </form>

          {/* Help Text */}
          <div className="mt-6 pt-6 border-t border-slate-700/50">
            <p className="text-slate-400 text-xs text-center">
              Your information will be used only to establish a support chat session. <br />
              No data sharing with third parties.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-slate-400 text-sm">
          <p>Having issues? <span className="text-blue-400 cursor-pointer hover:text-blue-300">Contact support</span></p>
        </div>
      </div>
    </div>
  )
}
