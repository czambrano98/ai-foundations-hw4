import { Link } from 'react-router-dom'
import type { Product } from '../types'
import { formatPrice } from '../api'

export default function ProductCard({ product }: { product: Product }) {
  return (
    <Link to={`/products/${product.product_id}`} className="card">
      <div className="card-image">
        <img src={product.image_url} alt={product.name} loading="lazy" />
      </div>
      <div className="card-body">
        <div className="card-name">{product.name}</div>
        <div className="card-desc">{product.short_description}</div>
        <div className="card-foot">
          <span className="price">{formatPrice(product.price)}</span>
          <span className={product.in_stock ? 'badge badge-stock' : 'badge badge-out'}>
            {product.in_stock ? 'In stock' : 'Sold out'}
          </span>
        </div>
      </div>
    </Link>
  )
}
