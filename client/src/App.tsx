import { RouterProvider } from '@tanstack/react-router'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { router } from './router'
import { QUERY_CONFIG } from './config/constants'

// Create a client for TanStack Query
export const queryClient = new QueryClient(QUERY_CONFIG)

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  )
}

export default App
