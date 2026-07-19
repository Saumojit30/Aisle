import { create } from "zustand"
import type { Message, PipelineNode, NodeEvent, ToolEvent, ProfilingEvent } from "@/types"

interface ChatState {
  messages: Message[]
  sessionId: string | null
  customerId: string | null
  pipelineState: Record<PipelineNode, { status: "pending" | "active" | "completed" | "failed" | "skipped"; result?: string }>
  activeToolCalls: ToolEvent[]
  profilingData: ProfilingEvent | null
  isProcessing: boolean
  agentTyping: boolean

  addMessage: (msg: Message) => void
  setSessionId: (id: string) => void
  setCustomerId: (id: string | null) => void
  setPipelineNode: (node: PipelineNode, status: NodeEvent["status"], result?: string) => void
  resetPipeline: () => void
  addToolEvent: (event: ToolEvent) => void
  setProfilingData: (data: ProfilingEvent | null) => void
  setIsProcessing: (v: boolean) => void
  setAgentTyping: (v: boolean) => void
  reset: () => void
}

const initialPipelineState: ChatState["pipelineState"] = {
  guardrail: { status: "pending" },
  supervisor: { status: "pending" },
  support: { status: "pending" },
  order: { status: "pending" },
  recommendation: { status: "pending" },
  respond: { status: "pending" },
  profiling: { status: "pending" },
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  sessionId: null,
  customerId: null,
  pipelineState: { ...initialPipelineState },
  activeToolCalls: [],
  profilingData: null,
  isProcessing: false,
  agentTyping: false,

  addMessage: (msg) =>
    set((s) => ({ messages: [...s.messages, msg] })),

  setSessionId: (id) => set({ sessionId: id }),
  setCustomerId: (id) => set({ customerId: id }),

  setPipelineNode: (node, status, result) =>
    set((s) => ({
      pipelineState: {
        ...s.pipelineState,
        [node]: { status, result },
      },
    })),

  resetPipeline: () =>
    set({ pipelineState: { ...initialPipelineState }, activeToolCalls: [], profilingData: null }),

  addToolEvent: (event) =>
    set((s) => ({
      activeToolCalls:
        event.status === "start"
          ? [...s.activeToolCalls, event]
          : s.activeToolCalls.map((t) =>
              t.tool === event.tool && t.node === event.node ? event : t
            ),
    })),

  setProfilingData: (data) => set({ profilingData: data }),
  setIsProcessing: (v) => set({ isProcessing: v }),
  setAgentTyping: (v) => set({ agentTyping: v }),

  reset: () =>
    set({
      messages: [],
      pipelineState: { ...initialPipelineState },
      activeToolCalls: [],
      profilingData: null,
      isProcessing: false,
      agentTyping: false,
    }),
}))
