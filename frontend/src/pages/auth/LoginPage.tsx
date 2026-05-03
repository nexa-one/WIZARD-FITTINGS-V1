import React from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useAuthStore } from '@/store'
import { authApi } from '@/services/api'
import toast from 'react-hot-toast'

interface LoginForm {
  email: string
  password: string
}

export function LoginPage() {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginForm>()

  const onSubmit = async (data: LoginForm) => {
    try {
      const { data: tokens } = await authApi.login(data.email, data.password)
      localStorage.setItem('access_token', tokens.access_token)
      const { data: user } = await authApi.me()
      setAuth(user, tokens.access_token, tokens.refresh_token)
      toast.success(`Welcome back, ${user.full_name}!`)
      navigate('/')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Login failed. Check your credentials.')
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
          maxWidth: 420,
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-xl)',
          padding: 40,
          boxShadow: 'var(--shadow-neumorphic)',
        }}
      >
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: 16,
              background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-cyan))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 24,
              margin: '0 auto 16px',
              boxShadow: '0 4px 16px rgba(31,111,235,0.4)',
            }}
          >
            ⟨/⟩
          </div>
          <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>CFM Fittings Pro</h1>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="form-group" style={{ marginBottom: 16 }}>
            <label className="label">Email address</label>
            <input
              className="input"
              type="email"
              placeholder="you@company.com"
              {...register('email', { required: 'Email is required' })}
            />
            {errors.email && <span style={{ fontSize: 12, color: 'var(--accent-red)' }}>{errors.email.message}</span>}
          </div>

          <div className="form-group" style={{ marginBottom: 24 }}>
            <label className="label">Password</label>
            <input
              className="input"
              type="password"
              placeholder="••••••••"
              {...register('password', { required: 'Password is required' })}
            />
            {errors.password && <span style={{ fontSize: 12, color: 'var(--accent-red)' }}>{errors.password.message}</span>}
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', justifyContent: 'center', padding: '12px', fontSize: 14 }}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="divider" />
        <p style={{ textAlign: 'center', fontSize: 13, color: 'var(--text-muted)' }}>
          No account?{' '}
          <Link to="/register" style={{ color: 'var(--accent-blue-hover)', textDecoration: 'none' }}>
            Register your company
          </Link>
        </p>
      </div>
    </div>
  )
}
