export interface AgentState {
  budget_ok: boolean
  budget_message: string | null
  guardrail_fail: boolean
  guardrail_message: string | null
  routing_decision: RoutingDecision | ""
}

export type RoutingDecision = "support" | "order" | "recommendation" | "respond"

export type PipelineNode =
  | "guardrail"
  | "supervisor"
  | "support"
  | "order"
  | "recommendation"
  | "respond"
  | "profiling"

export interface NodeEvent {
  node: PipelineNode
  status: "pending" | "active" | "completed" | "failed" | "skipped"
  timestamp?: string
  result?: string
  elapsed_ms?: number
  details?: Record<string, unknown>
}

export interface ToolEvent {
  node: PipelineNode
  tool: string
  status: "start" | "end"
  args?: Record<string, unknown>
  result?: string
  duration_ms?: number
}

export interface ProfilingEvent {
  preferred_categories?: string[]
  interests?: string[]
  budget_preference?: string
  shopping_occasion?: string
  summary?: string
}

export interface ChatStreamEvent {
  type: "node_start" | "node_end" | "tool_start" | "tool_end" | "profiling" | "complete"
  data: NodeEvent | ToolEvent | ProfilingEvent | ChatCompleteData
}

export interface ChatCompleteData {
  reply: string
  budget: BudgetSummary
  session_id: string
}

export interface BudgetSummary {
  session_id: string
  session_tokens: number
  session_cost: number
  daily_cost: number
  daily_usage_pct: number
  total_tokens_all_time: number
  approaching_limit: boolean
}

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  pipelineEvents?: NodeEvent[]
  toolEvents?: ToolEvent[]
  profilingData?: ProfilingEvent
  budgetAfter?: BudgetSummary
}

export interface Product {
  id: string
  name: string
  category: string
  price: number
  stock: number
  rating: number
  tags: string[]
}

export interface OrderItem {
  name: string
  qty: number
  price: number
}

export interface Order {
  order_id: string
  customer_id: string
  status: "shipped" | "processing" | "delivered" | "cancelled"
  items: OrderItem[]
  total: number
  estimated_delivery?: string
  tracking?: string
  carrier?: string
  delivered_at?: string
}

export interface CustomerProfile {
  customer_id: string
  name: string
  tier: "gold" | "silver"
  member_since: string
}

export interface CustomerMemory {
  customer_id: string
  preferences: Record<string, unknown>
  interests: string[]
  interaction_count: number
  last_interaction: string | null
  created_at: string
}

export interface AdminStats {
  budget: BudgetSummary
  memory: {
    customers: number
    active_sessions: number
  }
}
