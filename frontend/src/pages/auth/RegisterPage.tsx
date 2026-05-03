import React from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { authApi } from '@/services/api'
import toast from 'react-hot-toast'

interface RegisterForm {
  tenant_name: string
  full_name: string
  email: string
  password: string
  confirm_password: string
}

export function RegisterPage() {
  const navigate = useNavigate()
  const { register, handleSubmit, watch, formState: { errors, isSubmitting } } = useForm<RegisterForm>()
  const password = watch('password')

  const onSubmit = async (data: RegisterForm) => {
    try {
      await authApi.register({
        tenant_name: data.tenant_name,
        email: data.email,
        full_name: data.full_name,
        password: data.password,
      })
      toast.success('Account created! Please sign in.')
      navigate('/login')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Registration failed.')
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--bg-base)',
        padding: 24,
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 480,
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-xl)',
          padding: 40,
          boxShadow: 'var(--shadow-neumorphic)',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{ width: 48, height: 48, borderRadius: 12, background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-cyan))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20, margin: '0 auto 12px', boxShadow: '0 4px 12px rgba(31,111,235,0.3)' }}>⟨/⟩</div>
          <h1 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>Create your account</h1>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Start your CFM Fittings Pro trial</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="form-group" style={{ marginBottom: 14 }}>
            <label className="label">Company / Tenant Name</label>
            <input className="input" placeholder="Acme HVAC Services" {...register('tenant_name', { required: 'Company name is required', minLength: { value: 2, message: 'Min 2 characters' } })} />
            {errors.tenant_name && <span style={{ fontSize: 12, color: 'var(--accent-red)' }}>{errors.tenant_name.message}</span>}
          </div>

          <div className="form-group" style={{ marginBottom: 14 }}>
            <label className="label">Full Name</label>
            <input className="input" placeholder="John Doe" {...register('full_name', { required: 'Full name is required' })} />
            {errors.full_name && <span style={{ fontSize: 12, color: 'var(--accent-red)' }}>{errors.full_name.message}</span>}
          </div>

          <div className="form-group" style={{ marginBottom: 14 }}>
            <label className="label">Email Address</label>
            <input className="input" type="email" placeholder="you@company.com" {...register('email', { required: 'Email is required' })} />
            {errors.email && <span style={{ fontSize: 12, color: 'var(--accent-red)' }}>{errors.email.message}</span>}
          </div>

          <div className="form-group" style={{ marginBottom: 14 }}>
            <label className="label">Password</label>
            <input className="input" type="password" placeholder="Min 8 chars, 1 uppercase, 1 number" {...register('password', { required: 'Password required', minLength: { value: 8, message: 'Min 8 characters' } })} />
            {errors.password && <span style={{ fontSize: 12, color: 'var(--accent-red)' }}>{errors.password.message}</span>}
          </div>

          <div className="form-group" style={{ marginBottom: 24 }}>
            <label className="label">Confirm Password</label>
            <input className="input" type="password" placeholder="Confirm password" {...register('confirm_password', { required: 'Please confirm', validate: (v) => v === password || 'Passwords do not match' })} />
            {errors.confirm_password && <span style={{ fontSize: 12, color: 'var(--accent-red)' }}>{errors.confirm_password.message}</span>}
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '12px' }} disabled={isSubmitting}>
            {isSubmitting ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <div className="divider" />
        <p style={{ textAlign: 'center', fontSize: 13, color: 'var(--text-muted)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: 'var(--accent-blue-hover)', textDecoration: 'none' }}>Sign in</Link>
        </p>
      </div>
    </div>
  )
}
