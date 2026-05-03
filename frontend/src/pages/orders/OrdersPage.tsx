import React from 'react'
import { useNavigate } from 'react-router-dom'
import { ordersApi } from '@/services/api'
import type { Order, OrderStatus } from '@/types'
import toast from 'react-hot-toast'

const STATUS_COLORS: Record<string, string> = {
  draft: 'badge-draft',
  pending: 'badge-pending',
  in_fabrication: 'badge-in_fabrication',
  quality_check: 'badge-quality_check',
  ready: 'badge-ready',
  delivered: 'badge-delivered',
  cancelled: 'badge-cancelled',
}

const URGENCY_COLORS: Record<string, string> = {
  low: 'badge-low',
  normal: 'badge-normal',
  high: 'badge-high',
  critical: 'badge-critical',
}

export function OrdersPage() {
  const navigate = useNavigate()
  const [orders, setOrders] = React.useState<Order[]>([])
  const [loading, setLoading] = React.useState(true)
  const [total, setTotal] = React.useState(0)
  const [search, setSearch] = React.useState('')
  const [statusFilter, setStatusFilter] = React.useState<string>('')
  const [page, setPage] = React.useState(1)

  const fetchOrders = React.useCallback(async () => {
    setLoading(true)
    try {
      const params: Record<string, unknown> = { page, page_size: 20 }
      if (search) params.search = search
      if (statusFilter) params.status = statusFilter
      const { data } = await ordersApi.search(params)
      setOrders(data.items)
      setTotal(data.total)
    } catch {
      toast.error('Failed to load orders')
    } finally {
      setLoading(false)
    }
  }, [page, search, statusFilter])

  React.useEffect(() => { fetchOrders() }, [fetchOrders])

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 2 }}>Orders</h1>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>{total} total orders</p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate('/orders/new')}>
          + New Order
        </button>
      </div>

      {/* Filters */}
      <div
        className="card"
        style={{ padding: '16px 20px', marginBottom: 20, display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}
      >
        <input
          className="input"
          style={{ maxWidth: 280 }}
          placeholder="Search by number, requester..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1) }}
        />
        <select
          className="input"
          style={{ maxWidth: 180 }}
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
        >
          <option value="">All Status</option>
          <option value="draft">Draft</option>
          <option value="pending">Pending</option>
          <option value="in_fabrication">In Fabrication</option>
          <option value="quality_check">Quality Check</option>
          <option value="ready">Ready</option>
          <option value="delivered">Delivered</option>
          <option value="cancelled">Cancelled</option>
        </select>
        {(search || statusFilter) && (
          <button className="btn btn-ghost" onClick={() => { setSearch(''); setStatusFilter(''); setPage(1) }}>
            Clear
          </button>
        )}
      </div>

      {/* Table */}
      <div className="card" style={{ overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
            <div className="animate-pulse">Loading orders...</div>
          </div>
        ) : orders.length === 0 ? (
          <div style={{ padding: 60, textAlign: 'center' }}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>📋</div>
            <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>No orders found</div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>
              {search || statusFilter ? 'Try adjusting your filters' : 'Create your first order to get started'}
            </div>
            <button className="btn btn-primary" onClick={() => navigate('/orders/new')}>Create First Order</button>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Order #</th>
                <th>Requester</th>
                <th>Date</th>
                <th>Status</th>
                <th>Urgency</th>
                <th>Type</th>
                <th>Qty</th>
                <th>Tags</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr
                  key={order.id}
                  style={{ cursor: 'pointer' }}
                  onClick={() => navigate(`/orders/${order.id}`)}
                >
                  <td>
                    <span className="mono" style={{ color: 'var(--accent-blue-hover)', fontWeight: 600 }}>
                      {order.request_number}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-primary)' }}>{order.requester_name}</td>
                  <td>{order.order_date}</td>
                  <td>
                    <span className={`badge ${STATUS_COLORS[order.status] || 'badge-draft'}`}>
                      {order.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${URGENCY_COLORS[order.urgency] || 'badge-normal'}`}>
                      {order.urgency}
                    </span>
                  </td>
                  <td style={{ textTransform: 'capitalize' }}>{order.order_type}</td>
                  <td style={{ fontWeight: 600 }}>{order.piece_quantity}</td>
                  <td>
                    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                      {order.tags?.slice(0, 3).map((tag) => (
                        <span key={tag} style={{ fontSize: 10, padding: '2px 8px', borderRadius: 99, background: 'var(--accent-blue-subtle)', color: 'var(--accent-blue-hover)' }}>
                          {tag}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <button
                      className="btn btn-ghost"
                      style={{ padding: '4px 10px', fontSize: 12 }}
                      onClick={(e) => { e.stopPropagation(); navigate(`/orders/${order.id}`) }}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {/* Pagination */}
        {total > 20 && (
          <div style={{ padding: '14px 20px', borderTop: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              Page {page} of {Math.ceil(total / 20)}
            </span>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn btn-ghost" style={{ padding: '6px 12px' }} disabled={page === 1} onClick={() => setPage((p) => p - 1)}>← Prev</button>
              <button className="btn btn-ghost" style={{ padding: '6px 12px' }} disabled={page >= Math.ceil(total / 20)} onClick={() => setPage((p) => p + 1)}>Next →</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
