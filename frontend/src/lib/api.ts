import type { ChatCompleteData, ChatStreamEvent, AdminStats, CustomerMemory, Product, Order, BudgetSummary } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"

export async function sendChatMessage(
  message: string,
  sessionId?: string,
  customerId?: string
): Promise<ChatCompleteData> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      session_id: sessionId || null,
      customer_id: customerId || null,
    }),
  })
  if (!res.ok) throw new Error("Chat request failed")
  const data = await res.json()
  return {
    reply: data.reply,
    budget: data.budget,
    session_id: data.session_id,
  }
}

export function streamChatMessage(
  message: string,
  sessionId?: string,
  customerId?: string,
  signal?: AbortSignal
): EventSource {
  const params = new URLSearchParams({
    message,
    ...(sessionId && { session_id: sessionId }),
    ...(customerId && { customer_id: customerId }),
  })
  const es = new EventSource(`${API_BASE}/chat/stream?${params}`)
  return es
}

export async function fetchAdminStats(): Promise<AdminStats> {
  const res = await fetch(`${API_BASE}/admin/stats`, { cache: "no-store" })
  if (!res.ok) throw new Error("Failed to fetch stats")
  return res.json()
}

export async function fetchBudget(sessionId: string): Promise<BudgetSummary> {
  const res = await fetch(`${API_BASE}/budget/${sessionId}`, { cache: "no-store" })
  if (!res.ok) throw new Error("Failed to fetch budget")
  return res.json()
}

export async function fetchProducts(): Promise<Product[]> {
  const res = await fetch(`${API_BASE}/products`, { cache: "no-store" })
  if (!res.ok) throw new Error("Failed to fetch products")
  return res.json()
}

export async function fetchOrders(): Promise<Order[]> {
  const res = await fetch(`${API_BASE}/orders`, { cache: "no-store" })
  if (!res.ok) throw new Error("Failed to fetch orders")
  return res.json()
}

export async function fetchCustomers(): Promise<CustomerMemory[]> {
  const res = await fetch(`${API_BASE}/memory/customers`, { cache: "no-store" })
  if (!res.ok) throw new Error("Failed to fetch customers")
  return res.json()
}

export async function fetchCustomerDetail(id: string): Promise<CustomerMemory> {
  const res = await fetch(`${API_BASE}/memory/customers/${id}`, { cache: "no-store" })
  if (!res.ok) throw new Error("Failed to fetch customer")
  return res.json()
}
