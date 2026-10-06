import { useState } from 'react'
import { Link } from 'react-router-dom'

export default function SignUp() {
  const [form, setForm] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
  })

  function update(field: keyof typeof form) {
    return (event: React.ChangeEvent<HTMLInputElement>) =>
      setForm((prev) => ({ ...prev, [field]: event.target.value }))
  }

  return (
    <div className="page">
      <div className="shell">
        <div className="form-card">
          <hr className="rule" />
          <h1 style={{ fontSize: '1.9rem' }}>Create account</h1>

          <div className="form-note">
            Sign-up isn't wired up yet — the <code>users</code> table is ready, but
            registration arrives in a later problem.
          </div>

          <form
            onSubmit={(event) => {
              event.preventDefault()
              alert('Account creation is not connected yet.')
            }}
          >
            <div className="field">
              <label htmlFor="firstName">First name</label>
              <input id="firstName" value={form.firstName} onChange={update('firstName')} required />
            </div>

            <div className="field">
              <label htmlFor="lastName">Last name</label>
              <input id="lastName" value={form.lastName} onChange={update('lastName')} required />
            </div>

            <div className="field">
              <label htmlFor="newEmail">Email</label>
              <input
                id="newEmail"
                type="email"
                value={form.email}
                onChange={update('email')}
                placeholder="you@yale.edu"
                required
              />
            </div>

            <div className="field">
              <label htmlFor="newPassword">Password</label>
              <input
                id="newPassword"
                type="password"
                value={form.password}
                onChange={update('password')}
                placeholder="At least 8 characters"
                minLength={8}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary btn-block">
              Create account
            </button>
          </form>

          <div className="form-foot">
            Already have one? <Link to="/login">Log in</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
