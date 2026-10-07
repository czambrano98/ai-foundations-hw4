import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { categoryLabel, fetchCategories, fetchProducts } from '../api'
import { useChatResults } from '../chatResults'
import type { CategoryCount, Product } from '../types'
import ProductCard from '../components/ProductCard'

export default function Products() {
  const [searchParams, setSearchParams] = useSearchParams()
  const category = searchParams.get('category') ?? 'all'

  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<CategoryCount[]>([])
  const [search, setSearch] = useState(searchParams.get('search') ?? '')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Product matches pushed here by the chat assistant (Problem 7).
  const chatResults = useChatResults()

  useEffect(() => {
    fetchCategories().then(setCategories).catch(() => setCategories([]))
  }, [])

  // Debounce the search box so typing doesn't fire a request per keystroke.
  useEffect(() => {
    setLoading(true)
    const timer = setTimeout(() => {
      fetchProducts({ category, search })
        .then((results) => {
          setProducts(results)
          setError(null)
        })
        .catch(() =>
          setError(
            'Could not load products. Is the backend running on port 8000?',
          ),
        )
        .finally(() => setLoading(false))
    }, 250)
    return () => clearTimeout(timer)
  }, [category, search])

  function selectCategory(next: string) {
    const params = new URLSearchParams(searchParams)
    if (next === 'all') {
      params.delete('category')
    } else {
      params.set('category', next)
    }
    setSearchParams(params)
  }

  return (
    <div className="page">
      <div className="shell">
        <hr className="rule" />
        <h1>Products</h1>
        <p style={{ color: 'var(--slate)', marginBottom: 32 }}>
          Everything we currently make, straight from the shop floor.
        </p>

        {chatResults.results.length > 0 && (
          <>
            <section className="assistant-results">
              <div className="assistant-results-head">
                <div>
                  <div className="eyebrow">From the shop assistant</div>
                  <h2 style={{ marginBottom: 4 }}>
                    {chatResults.results.length}{' '}
                    {chatResults.results.length === 1 ? 'match' : 'matches'} for
                    “{chatResults.query}”
                  </h2>
                </div>
                <button className="btn btn-outline" onClick={chatResults.clear}>
                  Clear
                </button>
              </div>
              <div className="product-grid">
                {chatResults.results.map((product) => (
                  <ProductCard key={product.product_id} product={product} />
                ))}
              </div>
            </section>
            <h2 style={{ marginBottom: 20 }}>Browse everything</h2>
          </>
        )}

        <div className="toolbar">
          <div className="chips">
            <button
              className={category === 'all' ? 'chip active' : 'chip'}
              onClick={() => selectCategory('all')}
            >
              All
            </button>
            {categories.map((item) => (
              <button
                key={item.category}
                className={category === item.category ? 'chip active' : 'chip'}
                onClick={() => selectCategory(item.category)}
              >
                {categoryLabel(item.category)} ({item.count})
              </button>
            ))}
          </div>

          <input
            className="search-input"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search gear, teams, colleges..."
            aria-label="Search products"
          />
        </div>

        {error && (
          <div className="state">
            <h3>Something went wrong</h3>
            <p>{error}</p>
          </div>
        )}

        {!error && loading && (
          <div className="state">
            <p>Loading the collection...</p>
          </div>
        )}

        {!error && !loading && products.length === 0 && (
          <div className="state">
            <h3>Nothing matched</h3>
            <p>Try a different search, or browse all {categories.reduce((sum, c) => sum + c.count, 0)} styles.</p>
          </div>
        )}

        {!error && !loading && products.length > 0 && (
          <>
            <p style={{ color: 'var(--slate)', fontSize: '0.9rem', marginBottom: 20 }}>
              Showing {products.length} {products.length === 1 ? 'style' : 'styles'}
            </p>
            <div className="product-grid">
              {products.map((product) => (
                <ProductCard key={product.product_id} product={product} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
