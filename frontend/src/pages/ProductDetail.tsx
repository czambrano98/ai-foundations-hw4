import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { categoryLabel, fetchProduct, formatPrice } from '../api'
import type { ProductDetail as Detail } from '../types'

export default function ProductDetail() {
  const { productId } = useParams<{ productId: string }>()
  const [product, setProduct] = useState<Detail | null>(null)
  const [selectedSize, setSelectedSize] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!productId) return
    setLoading(true)
    setSelectedSize(null)
    window.scrollTo(0, 0)
    fetchProduct(productId)
      .then((data) => {
        setProduct(data)
        setError(null)
      })
      .catch(() => setError('We could not find that product.'))
      .finally(() => setLoading(false))
  }, [productId])

  if (loading) {
    return (
      <div className="page">
        <div className="state">
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  if (error || !product) {
    return (
      <div className="page">
        <div className="state">
          <h3>Not found</h3>
          <p>{error ?? 'That product does not exist.'}</p>
          <Link to="/products" className="btn btn-primary" style={{ marginTop: 16 }}>
            Back to products
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="page">
      <div className="shell">
        <div className="crumb">
          <Link to="/">Home</Link> / <Link to="/products">Products</Link> /{' '}
          <Link to={`/products?category=${product.category}`}>
            {categoryLabel(product.category)}
          </Link>{' '}
          / {product.name}
        </div>

        <div className="detail">
          <div className="detail-image">
            <img src={product.image_url} alt={product.name} />
          </div>

          <div>
            <span className="badge badge-cat">{product.garment_type}</span>
            <h1 style={{ marginTop: 12 }}>{product.name}</h1>
            <div className="detail-price">{formatPrice(product.price)}</div>

            <p className="detail-body">{product.description}</p>

            <div className="spec">
              <div className="spec-label">
                Sizes {product.in_stock ? '' : '— currently sold out'}
              </div>
              <div className="size-grid">
                {product.inventory.map((size) => (
                  <button
                    key={size.size}
                    className={
                      selectedSize === size.size ? 'size-box selected' : 'size-box'
                    }
                    disabled={!size.in_stock}
                    onClick={() => setSelectedSize(size.size)}
                    title={
                      size.in_stock
                        ? `${size.quantity} in stock`
                        : 'Out of stock in this size'
                    }
                  >
                    <span className="size-name">{size.size}</span>
                    <span className="size-qty">
                      {size.in_stock ? `${size.quantity} left` : 'Sold out'}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            <div className="spec">
              <div className="spec-label">Colors</div>
              <div className="swatch-row">
                {product.colors.map((color) => (
                  <span key={color} className="swatch">
                    {color}
                  </span>
                ))}
              </div>
            </div>

            <button
              className="btn btn-primary btn-block"
              disabled={!product.in_stock}
              onClick={() =>
                alert(
                  selectedSize
                    ? `Cart isn't built yet — but you picked ${product.name} in ${selectedSize}.`
                    : 'Pick a size first.',
                )
              }
            >
              {product.in_stock ? 'Add to bag' : 'Sold out'}
            </button>

            <div className="spec" style={{ marginTop: 32 }}>
              <div className="spec-label">Tags</div>
              <div className="tag-row">
                {product.search_tags.map((tag) => (
                  <span key={tag} className="tag">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
