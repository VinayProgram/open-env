import { Link } from '@tanstack/react-router'
import { Button } from '../components/ui/button'
import { AlertCircle, ArrowLeft } from 'lucide-react'

/**
 * Not Found (404) page
 * Displayed when user navigates to a non-existent route
 */
export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        <div className="flex justify-center mb-6">
          <div className="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center">
            <AlertCircle className="w-10 h-10 text-red-400" />
          </div>
        </div>
        
        <h1 className="text-5xl font-bold text-white mb-2">404</h1>
        <h2 className="text-2xl font-semibold text-slate-200 mb-4">Page Not Found</h2>
        <p className="text-slate-400 mb-8">
          Sorry, the page you're looking for doesn't exist. It might have been moved or removed.
        </p>
        
        <Link to="/">
          <Button className="bg-blue-600 hover:bg-blue-700 gap-2">
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Button>
        </Link>
      </div>
    </div>
  )
}
