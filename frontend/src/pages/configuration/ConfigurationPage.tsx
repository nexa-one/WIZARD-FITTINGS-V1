import React from 'react'
import { useUIStore, useAuthStore } from '@/store'
import type { Theme, Language } from '@/types'

export function ConfigurationPage() {
  const { theme, setTheme, language, setLanguage } = useUIStore()
  const { user } = useAuthStore()

  const APP_VERSION = import.meta.env.VITE_APP_VERSION || '1.0.0'

  return (
    <div className="animate-fade-in" style={{ maxWidth: 700, margin: '0 auto' }}>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>Configuration</h1>
        <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Platform settings and preferences</p>
      </div>

      {/* Mode */}
      <div className="card" style={{ padding: 24, marginBottom: 16 }}>
        <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--accent-blue-hover)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 16 }}>
          🎨 Display Mode
        </h3>
        <div style={{ display: 'flex', gap: 12 }}>
          {(['dark', 'light'] as Theme[]).map((t) => (
            <button
              key={t}
              onClick={() => setTheme(t)}
              className={`btn ${theme === t ? 'btn-primary' : 'btn-ghost'}`}
              style={{ flex: 1, justifyContent: 'center' }}
            >
              {t === 'dark' ? '🌙 Dark Mode' : '☀️ Light Mode'}
              {theme === t && <span style={{ marginLeft: 6 }}>✓</span>}
            </button>
          ))}
        </div>
      </div>

      {/* Language */}
      <div className="card" style={{ padding: 24, marginBottom: 16 }}>
        <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--accent-blue-hover)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 16 }}>
          🌐 Language
        </h3>
        <div style={{ display: 'flex', gap: 12 }}>
          {([
            { value: 'en', label: '🇺🇸 English' },
            { value: 'es', label: '🇪🇸 Spanish' },
            { value: 'pt', label: '🇧🇷 Portuguese' },
          ] as { value: Language; label: string }[]).map((lang) => (
            <button
              key={lang.value}
              onClick={() => setLanguage(lang.value)}
              className={`btn ${language === lang.value ? 'btn-primary' : 'btn-ghost'}`}
            >
              {lang.label}
              {language === lang.value && <span style={{ marginLeft: 6 }}>✓</span>}
            </button>
          ))}
        </div>
      </div>

      {/* About */}
      <div className="card" style={{ padding: 24 }}>
        <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--accent-blue-hover)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 20 }}>
          ℹ️ About CFM Fittings Pro
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
          {[
            ['Version', `v${APP_VERSION}`],
            ['Development', 'Nexa One Technology'],
            ['Logged In As', user?.email || '—'],
            ['Tenant', user?.tenant_id?.slice(0, 8) + '...' || '—'],
            ['Role', user?.role || '—'],
            ['Platform', 'Docker / SaaS / Cloud'],
          ].map(([label, value]) => (
            <div key={label}>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>{label}</div>
              <div style={{ fontSize: 13, fontWeight: 500, fontFamily: label === 'Version' ? 'var(--font-mono)' : undefined }}>
                {value}
              </div>
            </div>
          ))}
        </div>

        <hr className="divider" />

        <div style={{ display: 'flex', gap: 16 }}>
          <a
            href="mailto:support@cfmfittings.com"
            style={{ fontSize: 13, color: 'var(--accent-blue-hover)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 6 }}
          >
            ✉️ support@cfmfittings.com
          </a>
          <span style={{ fontSize: 13, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
            💬 WhatsApp Support Available
          </span>
        </div>

        <div style={{ marginTop: 16, fontSize: 11, color: 'var(--text-muted)' }}>
          © 2026 CFM Fittings Pro. All rights reserved. Commercial SaaS Platform.
        </div>
      </div>
    </div>
  )
}
