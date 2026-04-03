import { Outlet } from '@tanstack/react-router'

/**
 * Root layout component that wraps all routes
 * This component renders the common layout elements and the route outlet
 */
export default function RootLayout() {
  return (
    <div className="min-h-screen">
      {/* Route outlet - renders the current page component */}
      <Outlet />
    </div>
  )
}
