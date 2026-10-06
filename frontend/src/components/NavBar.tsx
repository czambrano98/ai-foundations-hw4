import { NavLink } from 'react-router-dom'

export default function NavBar() {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    isActive ? 'nav-link active' : 'nav-link'

  return (
    <header className="nav">
      <div className="shell nav-inner">
        <NavLink to="/" className="brand">
          Campus <span>Customs</span>
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
          <NavLink to="/login" className={linkClass}>
            Log in
          </NavLink>
          <NavLink to="/signup" className="nav-link cta">
            Create account
          </NavLink>
        </nav>
      </div>
    </header>
  )
}
