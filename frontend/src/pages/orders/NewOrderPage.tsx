import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { ordersApi } from '@/services/api'
import toast from 'react-hot-toast'

interface OrderForm {
  request_number: string
  requester_name: string
  order_date: string
  urgency: string
  piece_quantity: number
  status: string
  order_type: string
  notes: string
  tags_input: string
}

export function NewOrderPage() {
  const navigate = useNavigate()
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<OrderForm>({
    defaultValues: {
      order_date: new Date().toISOString().split('T')[0],
      urgency: 'normal',
      piece_quantity: 1,
      status: 'draft',
      order_type: 'standard',
    },
  })

  const onSubmit = async (data: OrderForm) => {
    try {
      const tags = data.tags_input ? data.tags_input.split(',').map((t) => t.trim()).filter(Boolean) : []
      const order = await ordersApi.create({
        request_number: data.request_number,
        requester_name: data.requester_name,
        order_date: data.order_date,
        urgency: data.urgency as any,
        piece_quantity: Number(data.piece_quantity),
        status: data.status as any,
        order_type: data.order_type as any,
        notes: data.notes || undefined,
        tags,
        items: [],
      })
      toast.success(`Order ${data.request_number} created!`)
      navigate(`/orders/${order.data.id}`)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to create order')
    }
  }

  return (
    <div className="animate-fade-in" style={{ maxWidth: 760, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 28 }}>
        <button className="btn btn-ghost" style={{ padding: '6px 10px' }} onClick={() => navigate('/orders')}>← Back</button>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700 }}>New Order</h1>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Create a new fabrication order</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="card" style={{ padding: 28, marginBottom: 20 }}>
          <h2 style={{ fontSize: 15, fontWeight: 700, marginBottom: 20, color: 'var(--accent-blue-hover)', display: 'flex', alignItems: 'center', gap: 8 }}>
            📋 Order Information
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label className="label">Request Number *</label>
              <input className="input" placeholder="REQ-2026-001" {...register('request_number', { required: 'Required' })} />
              {errors.request_number && <span style={{ fontSize: 12, color: 'var(--accent-red)' }}>{errors.request_number.message}</span>}
            </div>

            <div className="form-group">
              <label className="label">Requester Name *</label>
              <input className="input" placeholder="John Doe" {...register('requester_name', { required: 'Required' })} />
              {errors.requester_name && <span style={{ fontSize: 12, color: 'var(--accent-red)' }}>{errors.requester_name.message}</span>}
            </div>

            <div className="form-group">
              <label className="label">Order Date *</label>
              <input className="input" type="date" {...register('order_date', { required: 'Required' })} />
            </div>

            <div className="form-group">
              <label className="label">Piece Quantity *</label>
              <input className="input" type="number" min="1" {...register('piece_quantity', { required: 'Required', min: { value: 1, message: 'Min 1' } })} />
            </div>

            <div className="form-group">
              <label className="label">Urgency</label>
              <select className="input" {...register('urgency')}>
                <option value="low">Low</option>
                <option value="normal">Normal</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            <div className="form-group">
              <label className="label">Order Type</label>
              <select className="input" {...register('order_type')}>
                <option value="standard">Standard</option>
                <option value="custom">Custom</option>
                <option value="rush">Rush</option>
                <option value="revision">Revision</option>
                <option value="sample">Sample</option>
              </select>
            </div>

            <div className="form-group">
              <label className="label">Status</label>
              <select className="input" {...register('status')}>
                <option value="draft">Draft</option>
                <option value="pending">Pending</option>
                <option value="in_fabrication">In Fabrication</option>
                <option value="quality_check">Quality Check</option>
                <option value="ready">Ready</option>
                <option value="delivered">Delivered</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>

            <div className="form-group">
              <label className="label">Tags (comma separated)</label>
              <input className="input" placeholder="urgent, zone-a, rework" {...register('tags_input')} />
            </div>
          </div>

          <div className="form-group" style={{ marginTop: 16 }}>
            <label className="label">Notes</label>
            <textarea
              className="input"
              rows={3}
              placeholder="Additional notes or special instructions..."
              style={{ resize: 'vertical', minHeight: 80 }}
              {...register('notes')}
            />
          </div>
        </div>

        <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
          <button type="button" className="btn btn-ghost" onClick={() => navigate('/orders')}>Cancel</button>
          <button type="submit" className="btn btn-primary" disabled={isSubmitting} style={{ minWidth: 140 }}>
            {isSubmitting ? 'Creating...' : 'Create Order'}
          </button>
        </div>
      </form>
    </div>
  )
}
