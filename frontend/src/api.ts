import type {
  AuthResponse,
  CategoryCount,
  ChatMessage,
  ChatReply,
  Product,
  ProductDetail,
  SignupInput,
  User,
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

// --- Auth -----------------------------------------------------------------

const TOKEN_KEY = 'campus_customs_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string | null) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }
}

/** POST a JSON body and surface the backend's error detail on failure. */
async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.detail ?? `${response.status} ${response.statusText}`)
  }
  return data as T
}

export function signup(input: SignupInput): Promise<AuthResponse> {
  return postJson<AuthResponse>('/api/auth/signup', input)
}

export function login(email: string, password: string): Promise<AuthResponse> {
  return postJson<AuthResponse>('/api/auth/login', { email, password })
}

/** Resolve the stored token to the current user, or null if not signed in. */
export async function fetchMe(): Promise<User | null> {
  const token = getToken()
  if (!token) return null
  const response = await fetch('/api/auth/me', {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!response.ok) {
    setToken(null) // expired or invalid; drop it
    return null
  }
  const data = await response.json()
  return data.user as User
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

export async function sendChatMessage(
  message: string,
  productId?: string | null,
): Promise<ChatReply> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  // Send the token when signed in, so the backend can save/recall history and
  // tell the agent who is chatting. Omitted for guests.
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  const response = await fetch('/api/chat', {
    method: 'POST',
    headers,
    // product_id is the page the shopper is on, for "do you have this in...".
    body: JSON.stringify({ message, product_id: productId ?? null }),
  })
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`)
  }
  return response.json() as Promise<ChatReply>
}

/** A signed-in shopper's saved chat, to reload when the widget opens. Empty for guests. */
export async function fetchChatHistory(): Promise<ChatMessage[]> {
  const token = getToken()
  if (!token) return []
  const response = await fetch('/api/chat/history', {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!response.ok) return []
  const data = await response.json()
  return (data.messages ?? []) as ChatMessage[]
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
