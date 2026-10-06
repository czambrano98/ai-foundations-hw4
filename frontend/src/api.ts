import type {
  CategoryCount,
  ChatReply,
  Product,
  ProductDetail,
} from './types'

// Paths are relative: Vite proxies /api and /images to the FastAPI backend in
// development (see vite.config.ts), so there is no host to configure here.

async function get<T>(path: string): Promise<T> {
  const response = await fetch(path)
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`)
  }
  return response.json() as Promise<T>
}

export async function fetchProducts(options?: {
  category?: string
  search?: string
}): Promise<Product[]> {
  const params = new URLSearchParams()
  if (options?.category && options.category !== 'all') {
    params.set('category', options.category)
  }
  if (options?.search) {
    params.set('search', options.search)
  }
  const query = params.toString()
  const data = await get<{ count: number; products: Product[] }>(
    `/api/products${query ? `?${query}` : ''}`,
  )
  return data.products
}

export function fetchProduct(productId: string): Promise<ProductDetail> {
  return get<ProductDetail>(`/api/products/${productId}`)
}

export function fetchCategories(): Promise<CategoryCount[]> {
  return get<CategoryCount[]>('/api/categories')
}

export async function sendChatMessage(message: string): Promise<ChatReply> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  })
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`)
  }
  return response.json() as Promise<ChatReply>
}

export function formatPrice(price: number): string {
  return `$${price.toFixed(2).replace(/\.00$/, '')}`
}

export function categoryLabel(category: string): string {
  const labels: Record<string, string> = {
    'crewneck': 'Crewnecks',
    'hoodie': 'Hoodies',
    't-shirt': 'T-Shirts',
    'quarter-zip': 'Quarter-Zips',
    'jacket': 'Jackets',
    'sweatshirt': 'Sweatshirts',
    'long-sleeve-shirt': 'Long Sleeves',
  }
  return labels[category] ?? category
}
