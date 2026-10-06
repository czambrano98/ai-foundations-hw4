import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { categoryLabel, fetchCategories, fetchProducts } from '../api'
import type { CategoryCount, Product } from '../types'
import ProductCard from '../components/ProductCard'

export default function Home() {
  const [categories, setCategories] = useState<CategoryCount[]>([])
  const [featured, setFeatured] = useState<Product[]>([])

  useEffect(() => {
    fetchCategories().then(setCategories).catch(() => setCategories([]))
    fetchProducts()
      .then((all) => setFeatured(all.filter((p) => p.in_stock).slice(0, 4)))
      .catch(() => setFeatured([]))
  }, [])

  return (
    <>
      <section className="hero">
        <div className="shell">
          <div className="kicker">New Haven · Since 1973</div>
          <h1>Yale, worn well.</h1>
          <p>
            We've been on Broadway long enough to know what survives four New Haven
            winters — and what someone still wants to wear at their twentieth reunion.
            Every piece here is printed and stitched by us, a few blocks from where
            you'll wear it.
          </p>
          <Link to="/products" className="btn btn-gold">
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
              Every residential college, every school, every team — and a few things
              for the people back home who are quietly very proud of you.
            </p>
          </div>
          <div className="cat-grid">
            {categories.map((item) => (
              <Link
                key={item.category}
                to={`/products?category=${item.category}`}
                className="cat-tile"
              >
                <div className="name">{categoryLabel(item.category)}</div>
                <div className="count">{item.count} styles</div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {featured.length > 0 && (
        <section className="section alt">
          <div className="shell">
            <div className="section-head">
              <hr className="rule center" />
              <h2>Picked for this week</h2>
              <p>A few things we've been reaching for off the shelf lately.</p>
            </div>
            <div className="product-grid">
              {featured.map((product) => (
                <ProductCard key={product.product_id} product={product} />
              ))}
            </div>
            <div style={{ textAlign: 'center', marginTop: 40 }}>
              <Link to="/products" className="btn btn-primary">
                See all 102 styles
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
                Our presses and embroidery machines are here in New Haven, not on the
                other side of an ocean. When a crest looks wrong, we walk back and fix
                it ourselves.
              </p>
            </div>
            <div className="pitch">
              <hr className="rule" />
              <h3>Built to be kept</h3>
              <p>
                Heavyweight cotton, ribbed cuffs that hold their shape, stitching that
                outlasts the degree. We'd rather sell you one sweatshirt that lasts
                than three that don't.
              </p>
            </div>
            <div className="pitch">
              <hr className="rule" />
              <h3>For everyone who claims you</h3>
              <p>
                Mom, Dad, Grandma, the aunt who tells strangers where you go to school.
                We make gear for all of them, because belonging here was never only
                about you.
              </p>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
