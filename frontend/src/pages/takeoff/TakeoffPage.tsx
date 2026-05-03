import React from 'react'

export function TakeoffPage() {
  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>Take Off</h1>
        <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>PDF upload, measurement tools, asset counting, and report export</p>
      </div>

      <div
        className="card"
        style={{
          padding: 60,
          textAlign: 'center',
          border: '2px dashed var(--border-default)',
          background: 'transparent',
        }}
      >
        <div style={{ fontSize: 48, marginBottom: 16 }}>📐</div>
        <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>Takeoff Module</div>
        <div style={{ fontSize: 13, color: 'var(--text-muted)', maxWidth: 440, margin: '0 auto', lineHeight: 1.6 }}>
          Upload PDF plans, use measurement tools to count grills, diffusers, and ductwork, and generate a comprehensive takeoff report.
        </div>
        <div style={{ marginTop: 24, display: 'flex', gap: 12, justifyContent: 'center' }}>
          <button className="btn btn-primary" disabled>
            📄 Upload PDF Plan
          </button>
          <span style={{ fontSize: 11, color: 'var(--text-muted)', alignSelf: 'center' }}>Coming in V2</span>
        </div>
      </div>
    </div>
  )
}
