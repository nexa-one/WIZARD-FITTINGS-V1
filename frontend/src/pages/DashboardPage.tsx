import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store'

export function DashboardPage() {
  const { user } = useAuthStore()
  const navigate = useNavigate()

  const quickActions = [
    { label: 'New Order', icon: '📋', path: '/orders/new', desc: 'Create a fabrication order', color: 'var(--accent-blue)' },
    { label: 'Design Fitting', icon: '⚙️', path: '/fitting', desc: 'Configure a new fitting', color: 'var(--accent-cyan)' },
    { label: 'Search Orders', icon: '🔍', path: '/orders/search', desc: 'Find existing orders', color: 'var(--accent-purple)' },
    { label: 'Take Off', icon: '📐', path: '/takeoff', desc: 'Upload PDF plans', color: 'var(--accent-green)' },
  ]

  return (
    <div className="animate-fade-in">
      {/* Welcome */}
      <div
        style={{
          background: 'linear-gradient(135deg, var(--accent-blue-subtle), var(--bg-elevated))',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-xl)',
          padding: '28px 32px',
          marginBottom: 28,
        }}
      >
        <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 6 }}>
          Welcome back, {user?.full_name?.split(' ')[0] || 'there'} 👋
        </h1>
        <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
          CFM Fittings Pro — Commercial HVAC Ductwork Fittings Platform
        </p>
      </div>

      {/* Quick Actions */}
      <h2 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 14 }}>
        Quick Actions
      </h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 28 }}>
        {quickActions.map((action) => (
          <button
            key={action.path}
            onClick={() => navigate(action.path)}
            className="card"
            style={{
              padding: '20px 18px',
              textAlign: 'left',
              cursor: 'pointer',
              border: '1px solid var(--border-subtle)',
              transition: 'all var(--transition)',
              background: 'var(--bg-card)',
            }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.borderColor = action.color; (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)' }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.borderColor = 'var(--border-subtle)'; (e.currentTarget as HTMLElement).style.transform = 'none' }}
          >
            <div style={{ fontSize: 28, marginBottom: 10 }}>{action.icon}</div>
            <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 4, color: action.color }}>{action.label}</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{action.desc}</div>
          </button>
        ))}
      </div>

      {/* Platform Status */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div className="card" style={{ padding: 24 }}>
          <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 16 }}>
            Platform Modules
          </h3>
          {[
            { name: 'Auth & Multi-Tenant', status: 'active', color: 'var(--accent-green)' },
            { name: 'Orders Module', status: 'active', color: 'var(--accent-green)' },
            { name: 'Fittings Designer', status: 'active', color: 'var(--accent-green)' },
            { name: 'Take Off Module', status: 'v2', color: 'var(--accent-yellow)' },
            { name: 'AI Fitting Assistant', status: 'v2', color: 'var(--accent-yellow)' },
            { name: 'DXF/PDF Export', status: 'v2', color: 'var(--accent-yellow)' },
          ].map((mod) => (
            <div key={mod.name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ fontSize: 13 }}>{mod.name}</span>
              <span style={{ fontSize: 11, padding: '2px 8px', borderRadius: 99, background: mod.status === 'active' ? 'rgba(63,185,80,0.15)' : 'rgba(210,153,34,0.15)', color: mod.color }}>
                {mod.status === 'active' ? '● Active' : '◎ V2'}
              </span>
            </div>
          ))}
        </div>

        <div className="card" style={{ padding: 24 }}>
          <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 16 }}>
            Technology Stack
          </h3>
          {[
            { layer: 'Backend', tech: 'FastAPI + Python 3.12', icon: '🐍' },
            { layer: 'Frontend', tech: 'React 18 + TypeScript', icon: '⚛️' },
            { layer: 'Database', tech: 'PostgreSQL 16', icon: '🐘' },
            { layer: '3D Engine', tech: 'Three.js + R3F', icon: '🧊' },
            { layer: 'Auth', tech: 'JWT + Refresh Tokens', icon: '🔐' },
            { layer: 'Deploy', tech: 'Docker Compose', icon: '🐳' },
          ].map((s) => (
            <div key={s.layer} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '7px 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span>{s.icon}</span>
              <div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{s.layer}</div>
                <div style={{ fontSize: 13 }}>{s.tech}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
