import React from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { useUIStore } from '@/store'

interface NavItem {
  label: string
  path: string
  icon: string
  children?: { label: string; path: string }[]
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Fitting', path: '/fitting', icon: '⚙️' },
  {
    label: 'Orders',
    path: '/orders',
    icon: '📋',
    children: [
      { label: 'New Order', path: '/orders/new' },
      { label: 'Search Order', path: '/orders/search' },
    ],
  },
  { label: 'Take Off', path: '/takeoff', icon: '📐' },
  { label: 'Configuration', path: '/configuration', icon: '🔧' },
]

export function Sidebar() {
  const { sidebarOpen } = useUIStore()
  const location = useLocation()
  const [expandedItems, setExpandedItems] = React.useState<string[]>(['Orders'])

  const toggleExpand = (label: string) => {
    setExpandedItems((prev) =>
      prev.includes(label) ? prev.filter((i) => i !== label) : [...prev, label],
    )
  }

  return (
    <aside
      style={{
        width: sidebarOpen ? 'var(--sidebar-width)' : 'var(--sidebar-collapsed)',
        minWidth: sidebarOpen ? 'var(--sidebar-width)' : 'var(--sidebar-collapsed)',
        height: '100vh',
        background: 'var(--bg-surface)',
        borderRight: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        transition: 'width 0.2s ease, min-width 0.2s ease',
        overflow: 'hidden',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      {/* Logo */}
      <div
        style={{
          padding: '20px 16px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          minHeight: 'var(--topbar-height)',
        }}
      >
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: 8,
            background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-cyan))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 16,
            flexShrink: 0,
            boxShadow: '0 2px 8px rgba(31,111,235,0.4)',
          }}
        >
          ⟨/⟩
        </div>
        {sidebarOpen && (
          <div>
            <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.2 }}>
              CFM Fittings
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
              Pro v1.0
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: '12px 8px', overflowY: 'auto' }}>
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname.startsWith(item.path)
          const isExpanded = expandedItems.includes(item.label)

          return (
            <div key={item.path} style={{ marginBottom: 2 }}>
              {item.children ? (
                <>
                  <button
                    onClick={() => toggleExpand(item.label)}
                    style={{
                      width: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 10,
                      padding: '10px 12px',
                      borderRadius: 'var(--radius-md)',
                      background: isActive ? 'var(--accent-blue-subtle)' : 'transparent',
                      border: 'none',
                      cursor: 'pointer',
                      color: isActive ? 'var(--accent-blue-hover)' : 'var(--text-secondary)',
                      fontSize: 14,
                      fontWeight: 500,
                      transition: 'all var(--transition)',
                      textAlign: 'left',
                    }}
                  >
                    <span style={{ fontSize: 16, flexShrink: 0 }}>{item.icon}</span>
                    {sidebarOpen && (
                      <>
                        <span style={{ flex: 1 }}>{item.label}</span>
                        <span style={{ fontSize: 10, transition: 'transform 0.2s', transform: isExpanded ? 'rotate(90deg)' : 'none' }}>▶</span>
                      </>
                    )}
                  </button>
                  {sidebarOpen && isExpanded && (
                    <div style={{ paddingLeft: 16, marginTop: 2 }}>
                      {item.children.map((child) => (
                        <NavLink
                          key={child.path}
                          to={child.path}
                          style={({ isActive }) => ({
                            display: 'flex',
                            alignItems: 'center',
                            gap: 8,
                            padding: '8px 12px',
                            borderRadius: 'var(--radius-md)',
                            background: isActive ? 'var(--accent-blue-subtle)' : 'transparent',
                            color: isActive ? 'var(--accent-blue-hover)' : 'var(--text-muted)',
                            fontSize: 13,
                            textDecoration: 'none',
                            transition: 'all var(--transition)',
                            marginBottom: 2,
                          })}
                        >
                          <span style={{ width: 4, height: 4, borderRadius: '50%', background: 'currentColor', flexShrink: 0 }} />
                          {child.label}
                        </NavLink>
                      ))}
                    </div>
                  )}
                </>
              ) : (
                <NavLink
                  to={item.path}
                  style={({ isActive }) => ({
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-md)',
                    background: isActive ? 'var(--accent-blue-subtle)' : 'transparent',
                    color: isActive ? 'var(--accent-blue-hover)' : 'var(--text-secondary)',
                    fontSize: 14,
                    fontWeight: 500,
                    textDecoration: 'none',
                    transition: 'all var(--transition)',
                  })}
                >
                  <span style={{ fontSize: 16, flexShrink: 0 }}>{item.icon}</span>
                  {sidebarOpen && <span>{item.label}</span>}
                </NavLink>
              )}
            </div>
          )
        })}
      </nav>

      {/* Bottom */}
      {sidebarOpen && (
        <div style={{ padding: '12px 16px', borderTop: '1px solid var(--border-subtle)' }}>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', textAlign: 'center' }}>
            CFM Fittings Pro © 2026
          </div>
        </div>
      )}
    </aside>
  )
}
