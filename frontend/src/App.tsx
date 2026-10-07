import { Link, Route, Routes } from 'react-router-dom'
import NavBar from './components/NavBar'
import ChatPanel from './components/ChatPanel'
import Home from './pages/Home'
import Products from './pages/Products'
import ProductDetail from './pages/ProductDetail'
import About from './pages/About'
import Login from './pages/Login'
import SignUp from './pages/SignUp'

export default function App() {
  return (
    <div className="app">
      <div className="announce">
        Printed &amp; embroidered in New Haven
        <span className="sep">·</span>
        Family-run since 1973
        <span className="sep">·</span>
        Pickup at 57 Broadway
      </div>
      <NavBar />

      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/:productId" element={<ProductDetail />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
        </Routes>
      </main>

      <footer className="footer">
        <div className="shell">
          <div className="footer-cols">
            <div className="footer-col">
              <div className="footer-brand">Campus Customs</div>
              Yale apparel, printed and embroidered by hand in New Haven since
              1973. Built for the Blue, made to last.
            </div>
            <div className="footer-col">
              <h4>Shop</h4>
              <Link to="/products">All products</Link>
              <Link to="/products?category=hoodie">Hoodies</Link>
              <Link to="/products?category=crewneck">Crewnecks</Link>
              <Link to="/products?category=t-shirt">T-shirts</Link>
            </div>
            <div className="footer-col">
              <h4>Visit</h4>
              <span style={{ display: 'block', marginBottom: 7 }}>
                57 Broadway
                <br />
                New Haven, CT
              </span>
              <Link to="/about">Our story</Link>
            </div>
          </div>
          <div className="footer-bottom">
            <span>© {new Date().getFullYear()} Campus Customs</span>
            <span>Boola Boola.</span>
          </div>
        </div>
      </footer>

      <ChatPanel />
    </div>
  )
}
