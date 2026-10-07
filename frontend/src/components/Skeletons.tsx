/** Shimmer placeholders shown while data loads, instead of "Loading..." text. */

export function ProductGridSkeleton({ count = 8 }: { count?: number }) {
  return (
    <div className="product-grid" aria-busy="true" aria-label="Loading products">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="skel-card">
          <div className="skeleton skel-img" />
          <div className="skeleton skel-line title" />
          <div className="skeleton skel-line" />
          <div className="skeleton skel-line sm" />
        </div>
      ))}
    </div>
  )
}

export function ProductDetailSkeleton() {
  return (
    <div className="detail" aria-busy="true" aria-label="Loading product">
      <div className="skeleton skel-detail-img" />
      <div>
        <div className="skeleton skel-line sm" style={{ margin: '0 0 16px' }} />
        <div className="skeleton skel-line lg" style={{ margin: '0 0 20px' }} />
        <div className="skeleton skel-line" style={{ margin: '0 0 10px' }} />
        <div className="skeleton skel-line" style={{ margin: '0 0 10px' }} />
        <div className="skeleton skel-line sm" style={{ margin: '0 0 32px' }} />
        <div className="skeleton" style={{ height: 44, width: '100%', borderRadius: 10 }} />
      </div>
    </div>
  )
}
