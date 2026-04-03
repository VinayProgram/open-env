import { createRootRoute, createRoute, createRouter } from '@tanstack/react-router'
import RootLayout from './layouts/RootLayout'
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'
import { RegisterChat } from './app/register'
import { ChatWindow } from './app/chat'


// Root Route
const rootRoute = createRootRoute({
    component: RootLayout,
})

// Index Route (Landing Page)
const indexRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: '/',
    component: LandingPage,
})


const DashboardRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: '/dashboard',
    component: Dashboard,
})

const chatRegister = createRoute({
    getParentRoute: () => rootRoute,
    path: '/chat',
    component: RegisterChat,
})

const chatWindow = createRoute({
    getParentRoute: () => rootRoute,
    path: '/chat/$chatId',
    component: ChatWindow,
})


// Create Route Tree
const routeTree = rootRoute.addChildren([indexRoute, DashboardRoute, chatRegister, chatWindow])

// Create Router
export const router = createRouter({ routeTree })

// Register for type safety
declare module '@tanstack/react-router' {
    interface Register {
        router: typeof router
    }
}



