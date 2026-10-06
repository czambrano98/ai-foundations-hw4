import { Route, Routes } from 'react-router-dom'
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
        <div className="shell footer-inner">
          <div>
            <strong style={{ color: '#fff' }}>Campus Customs</strong>
            <br />
            57 Broadway, New Haven, CT · Since 1973
          </div>
          <div>
            Printed and embroidered in house.
            <br />
            Built for Yale, made in New Haven.
          </div>
        </div>
      </footer>

      <ChatPanel />
    </div>
  )
}
