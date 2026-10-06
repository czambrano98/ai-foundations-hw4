import { useState } from 'react'
import { Link } from 'react-router-dom'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  return (
    <div className="page">
      <div className="shell">
        <div className="form-card">
          <hr className="rule" />
          <h1 style={{ fontSize: '1.9rem' }}>Log in</h1>

          <div className="form-note">
            Accounts aren't wired up yet. Authentication arrives in a later
            problem, and this form is the shape of what's coming.
          </div>

          <form
            onSubmit={(event) => {
              event.preventDefault()
              alert('Login is not connected yet.')
            }}
          >
            <div className="field">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@yale.edu"
                required
              />
            </div>

            <div className="field">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            <button type="submit" className="btn btn-primary btn-block">
              Log in
            </button>
          </form>

          <div className="form-foot">
            New here? <Link to="/signup">Create an account</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
