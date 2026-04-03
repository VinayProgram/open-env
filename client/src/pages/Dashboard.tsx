import { Link } from '@tanstack/react-router'
import { BarChart3, Home } from 'lucide-react'

/**
 * Dashboard Page - Example of a secondary route
 * This can be accessed by adding a dashboard route to the router
 */
export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="bg-slate-900/50 border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition">
                <Home className="w-5 h-5 text-blue-400" />
                <span className="text-sm text-slate-300">Back to Home</span>
              </Link>
            </div>
            <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid md:grid-cols-4 gap-6 mb-12">
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
            <p className="text-slate-400 text-sm mb-2">Total Complaints</p>
            <p className="text-4xl font-bold text-white">2,847</p>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
            <p className="text-slate-400 text-sm mb-2">Resolved</p>
            <p className="text-4xl font-bold text-green-400">2,677</p>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
            <p className="text-slate-400 text-sm mb-2">Pending</p>
            <p className="text-4xl font-bold text-yellow-400">170</p>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
            <p className="text-slate-400 text-sm mb-2">Resolution Rate</p>
            <p className="text-4xl font-bold text-blue-400">94%</p>
          </div>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8">
          <div className="flex items-center gap-3 mb-6">
            <BarChart3 className="w-6 h-6 text-blue-400" />
            <h2 className="text-2xl font-bold text-white">Application Routes</h2>
          </div>
          
          <p className="text-slate-300 mb-6">
            This example demonstrates how TanStack Router works with component-based routing. 
            Add more routes to the router configuration in <code className="bg-slate-900 px-2 py-1 rounded text-sm">src/router.tsx</code>.
          </p>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white mb-4">Example: Adding a New Route</h3>
            <pre className="bg-slate-900 p-4 rounded-lg text-sm text-slate-300 overflow-auto">
{`// In src/router.tsx

const dashboardRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/dashboard',
  component: Dashboard,
})

// Add to routeTree.addChildren()
const routeTree = rootRoute.addChildren([
  indexRoute,
  dashboardRoute,
  notFoundRoute,
])`}
            </pre>
          </div>
        </div>
      </main>
    </div>
  )
}
