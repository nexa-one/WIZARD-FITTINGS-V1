import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AppShell } from '@/layout/AppShell'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { LoginPage } from '@/pages/auth/LoginPage'
import { RegisterPage } from '@/pages/auth/RegisterPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { OrdersPage } from '@/pages/orders/OrdersPage'
import { NewOrderPage } from '@/pages/orders/NewOrderPage'
import { OrderDetailPage } from '@/pages/orders/OrderDetailPage'
import { FittingPage } from '@/pages/fitting/FittingPage'
import { TakeoffPage } from '@/pages/takeoff/TakeoffPage'
import { ConfigurationPage } from '@/pages/configuration/ConfigurationPage'
import { useUIStore } from '@/store'

function ThemeApplicator() {
  const { theme } = useUIStore()
  React.useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])
  return null
}

export default function App() {
  return (
    <BrowserRouter>
      <ThemeApplicator />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'var(--bg-elevated)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-default)',
            borderRadius: '10px',
            fontSize: '13px',
          },
          success: { iconTheme: { primary: 'var(--accent-green)', secondary: 'transparent' } },
          error: { iconTheme: { primary: 'var(--accent-red)', secondary: 'transparent' } },
        }}
      />
      <Routes>
        {/* Public */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected App Shell */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AppShell />
            </ProtectedRoute>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="fitting" element={<FittingPage />} />
          <Route path="orders" element={<OrdersPage />} />
          <Route path="orders/new" element={<NewOrderPage />} />
          <Route path="orders/search" element={<OrdersPage />} />
          <Route path="orders/:id" element={<OrderDetailPage />} />
          <Route path="takeoff" element={<TakeoffPage />} />
          <Route path="configuration" element={<ConfigurationPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
