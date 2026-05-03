import { describe, it, expect } from 'vitest'
import type { Order, Fitting, FittingType, OrderStatus } from '@/types'

describe('Type definitions', () => {
  it('should allow valid OrderStatus values', () => {
    const statuses: OrderStatus[] = ['draft', 'pending', 'in_fabrication', 'quality_check', 'ready', 'delivered', 'cancelled']
    expect(statuses.length).toBe(7)
  })

  it('should allow valid FittingType values', () => {
    const types: FittingType[] = ['elbow', 'tee', 'reducer', 'offset', 'transition', 'cap', 'duct', 'custom']
    expect(types.length).toBe(8)
  })

  it('should construct a valid Order object', () => {
    const order: Order = {
      id: 'ord-1',
      request_number: 'REQ-001',
      requester_name: 'John Doe',
      order_date: '2026-05-03',
      urgency: 'high',
      piece_quantity: 5,
      status: 'draft',
      order_type: 'standard',
      tags: ['urgent'],
      tenant_id: 'ten-1',
      created_by: 'user-1',
      items: [],
      created_at: '2026-05-03T00:00:00Z',
      updated_at: '2026-05-03T00:00:00Z',
    }
    expect(order.request_number).toBe('REQ-001')
    expect(order.tags).toContain('urgent')
  })

  it('should construct a valid Fitting object', () => {
    const fitting: Fitting = {
      id: 'fit-1',
      name: '90° Elbow 12x12',
      fitting_type: 'elbow',
      material: 'galvanized',
      connection_type: 'slip',
      dimensions: { width_inlet: 12, height_inlet: 12, angle: 90 },
      geometry_data: { type: 'elbow' },
      engineering_data: {},
      is_validated: false,
      is_template: false,
      tenant_id: 'ten-1',
      created_by: 'user-1',
      created_at: '2026-05-03T00:00:00Z',
      updated_at: '2026-05-03T00:00:00Z',
    }
    expect(fitting.fitting_type).toBe('elbow')
    expect(fitting.dimensions.width_inlet).toBe(12)
  })
})
