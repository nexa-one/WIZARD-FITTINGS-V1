import { describe, it, expect, beforeEach } from 'vitest'
import { useAuthStore, useUIStore } from '@/store'

describe('AuthStore', () => {
  beforeEach(() => {
    useAuthStore.setState({ user: null, accessToken: null, refreshToken: null })
  })

  it('should be unauthenticated by default', () => {
    const { isAuthenticated } = useAuthStore.getState()
    expect(isAuthenticated()).toBe(false)
  })

  it('should set auth correctly', () => {
    const { setAuth } = useAuthStore.getState()
    const mockUser = {
      id: 'user-1',
      email: 'test@test.com',
      full_name: 'Test User',
      role: 'admin' as const,
      tenant_id: 'tenant-1',
      is_active: true,
      is_verified: true,
    }
    setAuth(mockUser, 'access-token', 'refresh-token')
    const state = useAuthStore.getState()
    expect(state.isAuthenticated()).toBe(true)
    expect(state.user?.email).toBe('test@test.com')
    expect(state.accessToken).toBe('access-token')
  })

  it('should clear auth on logout', () => {
    const { setAuth, clearAuth } = useAuthStore.getState()
    setAuth({ id: '1', email: 'x@y.com', full_name: 'X', role: 'viewer', tenant_id: 't1', is_active: true, is_verified: true }, 'tok', 'ref')
    clearAuth()
    expect(useAuthStore.getState().isAuthenticated()).toBe(false)
    expect(useAuthStore.getState().user).toBeNull()
  })
})

describe('UIStore', () => {
  it('should default to dark theme', () => {
    expect(useUIStore.getState().theme).toBe('dark')
  })

  it('should toggle theme', () => {
    const { setTheme } = useUIStore.getState()
    setTheme('light')
    expect(useUIStore.getState().theme).toBe('light')
    setTheme('dark')
    expect(useUIStore.getState().theme).toBe('dark')
  })

  it('should toggle sidebar', () => {
    const initial = useUIStore.getState().sidebarOpen
    useUIStore.getState().toggleSidebar()
    expect(useUIStore.getState().sidebarOpen).toBe(!initial)
  })

  it('should set language', () => {
    useUIStore.getState().setLanguage('es')
    expect(useUIStore.getState().language).toBe('es')
  })
})
