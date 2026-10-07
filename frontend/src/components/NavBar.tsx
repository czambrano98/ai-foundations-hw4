import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

export default function NavBar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    isActive ? 'nav-link active' : 'nav-link'

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <header className="nav">
      <div className="shell nav-inner">
        <NavLink to="/" className="brand">
          <span className="brand-mark" aria-hidden="true">CC</span>
          <span>
            Campus <span className="brand-accent">Customs</span>
          </span>
        </NavLink>

        <nav className="nav-links">
          <NavLink to="/" className={linkClass} end>
            Home
          </NavLink>
          <NavLink to="/products" className={linkClass}>
            Products
          </NavLink>
          <NavLink to="/about" className={linkClass}>
            About Us
          </NavLink>

          {user ? (
            <>
              <span className="nav-greeting">
                Hi, {user.first_name ?? user.name}
              </span>
              <button type="button" className="nav-link cta" onClick={handleLogout}>
                Log out
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className={linkClass}>
                Log in
              </NavLink>
              <NavLink to="/signup" className="nav-link cta">
                Create account
              </NavLink>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}
