import axios, { AxiosError } from 'axios'
import type { TokenResponse, User, Order, Fitting, PaginatedResponse } from '@/types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as typeof error.config & { _retry?: boolean }
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        try {
          const { data } = await axios.post<TokenResponse>(`${API_BASE}/api/v1/auth/refresh`, {
            refresh_token: refresh,
          })
          localStorage.setItem('access_token', data.access_token)
          localStorage.setItem('refresh_token', data.refresh_token)
          original.headers!['Authorization'] = `Bearer ${data.access_token}`
          return api(original)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  },
)

// Auth
export const authApi = {
  register: (data: { tenant_name: string; email: string; full_name: string; password: string }) =>
    api.post<User>('/auth/register', data),
  login: (email: string, password: string) =>
    api.post<TokenResponse>('/auth/login', { email, password }),
  me: () => api.get<User>('/auth/me'),
  logout: () => api.post('/auth/logout'),
}

// Orders
export const ordersApi = {
  create: (data: Partial<Order>) => api.post<Order>('/orders/', data),
  get: (id: string) => api.get<Order>(`/orders/${id}`),
  update: (id: string, data: Partial<Order>) => api.patch<Order>(`/orders/${id}`, data),
  delete: (id: string) => api.delete(`/orders/${id}`),
  search: (params: Record<string, unknown>) =>
    api.get<PaginatedResponse<Order>>('/orders/search', { params }),
}

// Fittings
export const fittingsApi = {
  create: (data: Partial<Fitting>) => api.post<Fitting>('/fittings/', data),
  get: (id: string) => api.get<Fitting>(`/fittings/${id}`),
  update: (id: string, data: Partial<Fitting>) => api.patch<Fitting>(`/fittings/${id}`, data),
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Fitting>>('/fittings/', { params }),
}
