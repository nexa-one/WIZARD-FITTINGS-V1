import React, { Suspense } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { fittingsApi } from '@/services/api'
import type { FittingType, MaterialType, ConnectionType, Fitting } from '@/types'
import toast from 'react-hot-toast'
import { FittingViewer3D } from '@/three/FittingViewer3D'

interface FittingForm {
  name: string
  fitting_type: FittingType
  material: MaterialType
  connection_type: ConnectionType
  gauge: string
  description: string
  width_inlet: number
  height_inlet: number
  width_outlet: number
  height_outlet: number
  length: number
  angle: number
  radius: number
  neck_width: number
  neck_height: number
}

const FITTING_TYPES: { value: FittingType; label: string; icon: string }[] = [
  { value: 'elbow', label: 'Elbow', icon: '↪' },
  { value: 'tee', label: 'Tee', icon: '⊤' },
  { value: 'reducer', label: 'Reducer', icon: '▷◁' },
  { value: 'offset', label: 'Offset', icon: '⤵' },
  { value: 'transition', label: 'Transition', icon: '▷' },
  { value: 'duct', label: 'Straight Duct', icon: '━' },
  { value: 'cap', label: 'Cap / End', icon: '⊓' },
  { value: 'custom', label: 'Custom', icon: '⚙' },
]

export function FittingPage() {
  const navigate = useNavigate()
  const [savedFitting, setSavedFitting] = React.useState<Fitting | null>(null)
  const [previewData, setPreviewData] = React.useState<Record<string, unknown> | null>(null)

  const { register, handleSubmit, watch, formState: { errors, isSubmitting } } = useForm<FittingForm>({
    defaultValues: {
      fitting_type: 'elbow',
      material: 'galvanized',
      connection_type: 'slip',
      width_inlet: 12,
      height_inlet: 12,
      angle: 90,
      radius: 18,
      length: 24,
    },
  })

  const fittingType = watch('fitting_type')

  const onSubmit = async (data: FittingForm) => {
    try {
      const dims: Record<string, number> = {}
      const dimFields = ['width_inlet', 'height_inlet', 'width_outlet', 'height_outlet', 'length', 'angle', 'radius', 'neck_width', 'neck_height'] as const
      dimFields.forEach((f) => { if (data[f]) dims[f] = Number(data[f]) })

      const { data: fitting } = await fittingsApi.create({
        name: data.name,
        fitting_type: data.fitting_type,
        material: data.material,
        connection_type: data.connection_type,
        dimensions: dims as any,
        gauge: data.gauge || undefined,
        description: data.description || undefined,
      })
      setSavedFitting(fitting)
      setPreviewData(fitting.geometry_data)
      toast.success(`Fitting "${fitting.name}" saved!`)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to save fitting')
    }
  }

  const showDim = (dim: string) => {
    const map: Record<string, FittingType[]> = {
      angle: ['elbow'],
      radius: ['elbow'],
      width_outlet: ['reducer', 'transition'],
      height_outlet: ['reducer', 'transition'],
      neck_width: ['tee'],
      neck_height: ['tee'],
      offset_x: ['offset'],
    }
    return !map[dim] || map[dim].includes(fittingType)
  }

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 2 }}>Fitting Designer</h1>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Create and configure HVAC ductwork fittings</p>
        </div>
        {savedFitting && (
          <button className="btn btn-ghost" onClick={() => navigate('/orders/new')}>
            + Add to Order
          </button>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: 20 }}>
        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="card" style={{ padding: 24, marginBottom: 16 }}>
            <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 16 }}>Fitting Type</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8 }}>
              {FITTING_TYPES.map((ft) => (
                <label
                  key={ft.value}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: 4,
                    padding: '10px 6px',
                    borderRadius: 'var(--radius-md)',
                    border: `1px solid ${fittingType === ft.value ? 'var(--accent-blue)' : 'var(--border-default)'}`,
                    background: fittingType === ft.value ? 'var(--accent-blue-subtle)' : 'var(--bg-base)',
                    cursor: 'pointer',
                    transition: 'all var(--transition)',
                    fontSize: 10,
                    color: fittingType === ft.value ? 'var(--accent-blue-hover)' : 'var(--text-muted)',
                  }}
                >
                  <input type="radio" value={ft.value} {...register('fitting_type')} style={{ display: 'none' }} />
                  <span style={{ fontSize: 18 }}>{ft.icon}</span>
                  <span style={{ fontWeight: 600 }}>{ft.label}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="card" style={{ padding: 24, marginBottom: 16 }}>
            <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 16 }}>Basic Info</h3>
            <div style={{ display: 'grid', gap: 12 }}>
              <div className="form-group">
                <label className="label">Fitting Name *</label>
                <input className="input" placeholder="90° Elbow 12x12 Galv." {...register('name', { required: 'Required' })} />
                {errors.name && <span style={{ fontSize: 12, color: 'var(--accent-red)' }}>{errors.name.message}</span>}
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div className="form-group">
                  <label className="label">Material</label>
                  <select className="input" {...register('material')}>
                    <option value="galvanized">Galvanized</option>
                    <option value="stainless_304">Stainless 304</option>
                    <option value="stainless_316">Stainless 316</option>
                    <option value="aluminum">Aluminum</option>
                    <option value="black_iron">Black Iron</option>
                    <option value="pvc">PVC</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="label">Connection</label>
                  <select className="input" {...register('connection_type')}>
                    <option value="slip">Slip</option>
                    <option value="drive">Drive</option>
                    <option value="flanged">Flanged</option>
                    <option value="grooved">Grooved</option>
                    <option value="welded">Welded</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="label">Gauge</label>
                  <select className="input" {...register('gauge')}>
                    <option value="">Select...</option>
                    <option value="30">30ga</option>
                    <option value="28">28ga</option>
                    <option value="26">26ga</option>
                    <option value="24">24ga</option>
                    <option value="22">22ga</option>
                    <option value="20">20ga</option>
                    <option value="18">18ga</option>
                    <option value="16">16ga</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <div className="card" style={{ padding: 24, marginBottom: 16 }}>
            <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 16 }}>Dimensions (inches)</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div className="form-group">
                <label className="label">Inlet Width</label>
                <input className="input" type="number" step="0.125" {...register('width_inlet')} />
              </div>
              <div className="form-group">
                <label className="label">Inlet Height</label>
                <input className="input" type="number" step="0.125" {...register('height_inlet')} />
              </div>
              {showDim('width_outlet') && (
                <>
                  <div className="form-group">
                    <label className="label">Outlet Width</label>
                    <input className="input" type="number" step="0.125" {...register('width_outlet')} />
                  </div>
                  <div className="form-group">
                    <label className="label">Outlet Height</label>
                    <input className="input" type="number" step="0.125" {...register('height_outlet')} />
                  </div>
                </>
              )}
              <div className="form-group">
                <label className="label">Length</label>
                <input className="input" type="number" step="0.125" {...register('length')} />
              </div>
              {showDim('angle') && (
                <div className="form-group">
                  <label className="label">Angle (°)</label>
                  <input className="input" type="number" step="1" {...register('angle')} />
                </div>
              )}
              {showDim('radius') && (
                <div className="form-group">
                  <label className="label">CL Radius</label>
                  <input className="input" type="number" step="0.125" {...register('radius')} />
                </div>
              )}
              {showDim('neck_width') && (
                <>
                  <div className="form-group">
                    <label className="label">Neck Width</label>
                    <input className="input" type="number" step="0.125" {...register('neck_width')} />
                  </div>
                  <div className="form-group">
                    <label className="label">Neck Height</label>
                    <input className="input" type="number" step="0.125" {...register('neck_height')} />
                  </div>
                </>
              )}
            </div>
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '12px' }} disabled={isSubmitting}>
            {isSubmitting ? 'Saving...' : '💾 Save Fitting'}
          </button>
        </form>

        {/* 3D Preview */}
        <div>
          <div className="card" style={{ padding: 0, overflow: 'hidden', height: 400, marginBottom: 16 }}>
            <div style={{ padding: '14px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: 13, fontWeight: 600 }}>3D Preview</span>
              <span className="badge badge-draft">{fittingType.toUpperCase()}</span>
            </div>
            <div style={{ height: 350, background: 'var(--bg-base)' }}>
              <Suspense fallback={<div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>Loading 3D viewer...</div>}>
                <FittingViewer3D fittingType={fittingType} geometryData={previewData} />
              </Suspense>
            </div>
          </div>

          {savedFitting && (
            <div className="card" style={{ padding: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                <span style={{ fontSize: 16 }}>✅</span>
                <span style={{ fontWeight: 600, fontSize: 14 }}>Fitting Saved</span>
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                ID: {savedFitting.id.slice(0, 8)}...
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
