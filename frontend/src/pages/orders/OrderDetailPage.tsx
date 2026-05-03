import React from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ordersApi } from '@/services/api'
import type { Order } from '@/types'
import toast from 'react-hot-toast'

const STATUS_LABELS: Record<string, string> = {
  draft: 'Draft', pending: 'Pending', in_fabrication: 'In Fabrication',
  quality_check: 'Quality Check', ready: 'Ready', delivered: 'Delivered', cancelled: 'Cancelled',
}

export function OrderDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [order, setOrder] = React.useState<Order | null>(null)
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    if (!id) return
    ordersApi.get(id)
      .then(({ data }) => setOrder(data))
      .catch(() => toast.error('Order not found'))
      .finally(() => setLoading(false))
  }, [id])

  const handleStatusChange = async (newStatus: string) => {
    if (!order) return
    try {
      const { data } = await ordersApi.update(order.id, { status: newStatus as any })
      setOrder(data)
      toast.success(`Status updated to ${STATUS_LABELS[newStatus]}`)
    } catch {
      toast.error('Failed to update status')
    }
  }

  if (loading) return <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>Loading...</div>
  if (!order) return <div style={{ padding: 40, textAlign: 'center', color: 'var(--accent-red)' }}>Order not found</div>

  return (
    <div className="animate-fade-in" style={{ maxWidth: 900, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <button className="btn btn-ghost" style={{ padding: '6px 10px' }} onClick={() => navigate('/orders')}>← Back</button>
          <div>
            <h1 style={{ fontSize: 22, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10 }}>
              <span className="mono" style={{ color: 'var(--accent-blue-hover)' }}>{order.request_number}</span>
              <span className={`badge badge-${order.status}`}>{STATUS_LABELS[order.status]}</span>
            </h1>
            <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
              By {order.requester_name} · {order.order_date}
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <select
            className="input"
            style={{ width: 180 }}
            value={order.status}
            onChange={(e) => handleStatusChange(e.target.value)}
          >
            {Object.entries(STATUS_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 20 }}>
        {/* Main Details */}
        <div className="card" style={{ padding: 24 }}>
          <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 16 }}>Order Details</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            {[
              ['Requester', order.requester_name],
              ['Order Date', order.order_date],
              ['Type', order.order_type.charAt(0).toUpperCase() + order.order_type.slice(1)],
              ['Urgency', <span className={`badge badge-${order.urgency}`}>{order.urgency}</span>],
              ['Qty', <strong>{order.piece_quantity} pcs</strong>],
            ].map(([label, value]) => (
              <div key={String(label)}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>{label}</div>
                <div style={{ fontSize: 14 }}>{value as React.ReactNode}</div>
              </div>
            ))}
          </div>

          {order.notes && (
            <>
              <hr className="divider" />
              <div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6 }}>NOTES</div>
                <div style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{order.notes}</div>
              </div>
            </>
          )}

          {order.tags?.length > 0 && (
            <>
              <hr className="divider" />
              <div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 8 }}>TAGS</div>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {order.tags.map((tag) => (
                    <span key={tag} style={{ fontSize: 11, padding: '3px 10px', borderRadius: 99, background: 'var(--accent-blue-subtle)', color: 'var(--accent-blue-hover)' }}>
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>

        {/* Items */}
        <div className="card" style={{ padding: 24 }}>
          <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 16 }}>
            Items ({order.items?.length || 0})
          </h3>
          {order.items?.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '20px 0', color: 'var(--text-muted)', fontSize: 13 }}>No items added</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {order.items.map((item, i) => (
                <div key={item.id} style={{ padding: '10px 12px', background: 'var(--bg-base)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 2 }}>{item.description}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    Qty: <strong>{item.quantity}</strong>{item.unit ? ` ${item.unit}` : ''}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
