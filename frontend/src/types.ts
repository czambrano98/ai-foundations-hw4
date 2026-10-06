export interface Product {
  product_id: string
  name: string
  garment_type: string
  category: string
  description: string
  short_description: string
  colors: string[]
  search_tags: string[]
  price: number
  image_url: string
  /** Hex color sampled from the photo's own corners, used as its tile background. */
  image_bg: string
  total_stock: number
  in_stock: boolean
}

export interface SizeStock {
  size: string
  quantity: number
  in_stock: boolean
}

export interface ProductDetail extends Product {
  inventory: SizeStock[]
  available_sizes: string[]
}

export interface CategoryCount {
  category: string
  count: number
}

export interface ChatReply {
  reply: string
  products: Product[]
  stub?: boolean
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  products?: Product[]
}

export interface User {
  id: number
  first_name: string | null
  last_name: string | null
  name: string
  email: string
}

export interface AuthResponse {
  token: string
  user: User
}

export interface SignupInput {
  first_name: string
  last_name: string
  email: string
  password: string
  confirm_password: string
}
