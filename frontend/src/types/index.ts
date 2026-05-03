export interface User {
  id: string
  email: string
  full_name: string
  role: 'superadmin' | 'admin' | 'manager' | 'estimator' | 'fabricator' | 'viewer'
  tenant_id: string
  is_active: boolean
  is_verified: boolean
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export type OrderStatus = 'draft' | 'pending' | 'in_fabrication' | 'quality_check' | 'ready' | 'delivered' | 'cancelled'
export type OrderType = 'standard' | 'custom' | 'rush' | 'revision' | 'sample'
export type UrgencyLevel = 'low' | 'normal' | 'high' | 'critical'

export interface OrderItem {
  id: string
  order_id: string
  description: string
  quantity: number
  unit?: string
  notes?: string
  sort_order: number
  specifications: Record<string, unknown>
  fitting_id?: string
}

export interface Order {
  id: string
  request_number: string
  requester_name: string
  order_date: string
  urgency: UrgencyLevel
  piece_quantity: number
  status: OrderStatus
  order_type: OrderType
  notes?: string
  tags: string[]
  tenant_id: string
  created_by: string
  job_id?: string
  job_area_id?: string
  items: OrderItem[]
  created_at: string
  updated_at: string
}

export type FittingType = 'elbow' | 'tee' | 'reducer' | 'offset' | 'transition' | 'cap' | 'duct' | 'custom'
export type MaterialType = 'galvanized' | 'stainless_304' | 'stainless_316' | 'aluminum' | 'black_iron' | 'pvc'
export type ConnectionType = 'slip' | 'drive' | 'flanged' | 'grooved' | 'welded'

export interface FittingDimensions {
  width_inlet?: number
  height_inlet?: number
  width_outlet?: number
  height_outlet?: number
  diameter_inlet?: number
  diameter_outlet?: number
  length?: number
  angle?: number
  radius?: number
  offset_x?: number
  offset_y?: number
  neck_width?: number
  neck_height?: number
}

export interface Fitting {
  id: string
  name: string
  fitting_type: FittingType
  material: MaterialType
  connection_type: ConnectionType
  dimensions: FittingDimensions
  geometry_data: Record<string, unknown>
  engineering_data: Record<string, unknown>
  gauge?: string
  description?: string
  is_validated: boolean
  is_template: boolean
  tenant_id: string
  created_by: string
  created_at: string
  updated_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface ApiError {
  detail: string
  code?: string
}

export type Theme = 'dark' | 'light'
export type Language = 'en' | 'es' | 'pt'
