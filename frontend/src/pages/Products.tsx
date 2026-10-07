import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { categoryLabel, fetchCategories, fetchProducts } from '../api'
import { useChatResults } from '../chatResults'
import type { CategoryCount, Product } from '../types'
import ProductCard from '../components/ProductCard'
import { ProductGridSkeleton } from '../components/Skeletons'

export default function Products() {
  const [searchParams, setSearchParams] = useSearchParams()
  const category = searchParams.get('category') ?? 'all'

  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<CategoryCount[]>([])
  const [search, setSearch] = useState(searchParams.get('search') ?? '')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Shopping filters (Problem 9): in-stock toggle and price sort, applied
  // client-side to the already-fetched set.
  const [inStockOnly, setInStockOnly] = useState(false)
  const [sort, setSort] = useState<'featured' | 'price-asc' | 'price-desc'>('featured')

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

  // Derive the shown list from the fetched products plus the active filters.
  const displayed = products
    .filter((p) => (inStockOnly ? p.in_stock : true))
    .sort((a, b) => {
      if (sort === 'price-asc') return a.price - b.price
      if (sort === 'price-desc') return b.price - a.price
      return 0 // 'featured' keeps the server's name order
    })

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

          <div className="toolbar-right">
            <label className="stock-toggle">
              <input
                type="checkbox"
                checked={inStockOnly}
                onChange={(event) => setInStockOnly(event.target.checked)}
              />
              In stock only
            </label>

            <select
              className="sort-select"
              value={sort}
              onChange={(event) =>
                setSort(event.target.value as typeof sort)
              }
              aria-label="Sort products"
            >
              <option value="featured">Sort: Featured</option>
              <option value="price-asc">Price: Low to High</option>
              <option value="price-desc">Price: High to Low</option>
            </select>

            <input
              className="search-input"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search gear, teams, colleges..."
              aria-label="Search products"
            />
          </div>
        </div>

        {error && (
          <div className="state">
            <h3>Something went wrong</h3>
            <p>{error}</p>
          </div>
        )}

        {!error && loading && <ProductGridSkeleton />}

        {!error && !loading && displayed.length === 0 && (
          <div className="state">
            <h3>Nothing matched</h3>
            <p>
              {inStockOnly
                ? 'Nothing in stock matches. Try turning off "In stock only" or a different search.'
                : `Try a different search, or browse all ${categories.reduce((sum, c) => sum + c.count, 0)} styles.`}
            </p>
          </div>
        )}

        {!error && !loading && displayed.length > 0 && (
          <>
            <p style={{ color: 'var(--slate)', fontSize: '0.9rem', marginBottom: 20 }}>
              Showing {displayed.length} {displayed.length === 1 ? 'style' : 'styles'}
            </p>
            <div className="product-grid">
              {displayed.map((product) => (
                <ProductCard key={product.product_id} product={product} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
