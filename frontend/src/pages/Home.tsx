import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { categoryLabel, fetchCategories, fetchProducts } from '../api'
import type { CategoryCount, Product } from '../types'
import ProductCard from '../components/ProductCard'

// The featured strip is locked to one row of four on desktop, so take exactly
// four in-stock products.
const FEATURED_COUNT = 4

export default function Home() {
  const [categories, setCategories] = useState<CategoryCount[]>([])
  const [featured, setFeatured] = useState<Product[]>([])

  useEffect(() => {
    fetchCategories().then(setCategories).catch(() => setCategories([]))
    fetchProducts()
      .then((all) => setFeatured(all.filter((p) => p.in_stock).slice(0, FEATURED_COUNT)))
      .catch(() => setFeatured([]))
  }, [])

  const totalStyles = categories.reduce((sum, item) => sum + item.count, 0)

  return (
    <>
      <section className="hero">
        <div className="shell">
          <div className="eyebrow">New Haven, since 1973</div>
          <h1>Yale, worn well.</h1>
          <p>
            We have been on Broadway long enough to know what survives four New
            Haven winters, and what someone still reaches for at their twentieth
            reunion. Everything here is printed and stitched by us, a few blocks
            from where you will wear it.
          </p>
          <Link to="/products" className="btn btn-primary">
            Shop the collection
          </Link>
        </div>
      </section>

      <section className="section">
        <div className="shell">
          <div className="section-head">
            <hr className="rule center" />
            <h2>Find your corner of campus</h2>
            <p>
              Every residential college, every school, every team, plus a few
              things for the people back home who are quietly very proud of you.
            </p>
          </div>

          {/* Seven categories plus a Shop all tile fills the 4-column grid
              exactly, so both rows are complete and every tile is the same size. */}
          <div className="cat-grid">
            {categories.map((item) => (
              <Link
                key={item.category}
                to={`/products?category=${item.category}`}
                className="cat-tile"
              >
                <span className="name">{categoryLabel(item.category)}</span>
                <span className="count">{item.count} styles</span>
              </Link>
            ))}
            {categories.length > 0 && (
              <Link to="/products" className="cat-tile all">
                <span className="name">Shop all</span>
                <span className="count">{totalStyles} styles</span>
              </Link>
            )}
          </div>
        </div>
      </section>

      {featured.length === FEATURED_COUNT && (
        <section className="section alt">
          <div className="shell">
            <div className="section-head">
              <hr className="rule center" />
              <h2>Picked for this week</h2>
              <p>A few things we have been pulling off the shelf lately.</p>
            </div>
            <div className="product-grid featured">
              {featured.map((product) => (
                <ProductCard key={product.product_id} product={product} />
              ))}
            </div>
            <div style={{ textAlign: 'center', marginTop: 44 }}>
              <Link to="/products" className="btn btn-outline">
                See all {totalStyles} styles
              </Link>
            </div>
          </div>
        </section>
      )}

      <section className="section">
        <div className="shell">
          <div className="pitch-grid">
            <div className="pitch">
              <hr className="rule" />
              <h3>Made in the back room</h3>
              <p>
                Our presses and embroidery machines are here in New Haven, not on
                the other side of an ocean. When a crest comes out crooked, we
                walk back and fix it ourselves.
              </p>
            </div>
            <div className="pitch">
              <hr className="rule" />
              <h3>Built to be kept</h3>
              <p>
                Heavyweight cotton, ribbed cuffs that hold their shape, stitching
                that outlasts the degree. We would rather sell you one sweatshirt
                that lasts than three that do not.
              </p>
            </div>
            <div className="pitch">
              <hr className="rule" />
              <h3>For everyone who claims you</h3>
              <p>
                Mom, Dad, Grandma, the aunt who tells strangers where you go to
                school. We make gear for all of them, because belonging here was
                never only about you.
              </p>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
