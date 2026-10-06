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
